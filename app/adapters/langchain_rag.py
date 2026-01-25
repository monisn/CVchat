
import os
import asyncio
from typing import AsyncGenerator, List, Dict

from langchain_community.document_loaders import WebBaseLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.documents import Document

from app.core.config import settings
from app.domain.ports import ChatServicePort

class LangChainRAGAdapter(ChatServicePort):
    def __init__(self):
        self.vector_store = None
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        self.llm = ChatGroq(
            model=settings.MODEL_NAME,
            api_key=settings.GROQ_API_KEY,
            streaming=True,
            temperature=0.7
        )

    async def initialize(self) -> None:
        """Loads data and builds the vector bucket."""
        loaders = [WebBaseLoader(settings.CONTENT_ORIGIN)]
        
        # Load local file
        if os.path.exists("extra_knowledge.txt"):
            loaders.append(TextLoader("extra_knowledge.txt"))

        docs = []
        for loader in loaders:
            docs.extend(loader.load())

        # Load from env var
        if settings.EXTRA_KNOWLEDGE:
             docs.append(Document(page_content=settings.EXTRA_KNOWLEDGE, metadata={"source": "env_extra_knowledge"}))

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = splitter.split_documents(docs)
        self.vector_store = FAISS.from_documents(splits, self.embeddings)
        print("Vector store initialized successfully.")

    async def stream_response(self, question: str, history: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        if not self.vector_store:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        # 1. Convert history
        chat_history = []
        for h in history:
            if h["role"] == "user":
                chat_history.append(HumanMessage(content=h.get("content", "")))
            else:
                chat_history.append(AIMessage(content=h.get("content", "")))

        # 2. Contextualize Question Prompt
        contextualize_q_system_prompt = "Dada la charla y la última pregunta, formula una pregunta independiente."
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        retriever = self.vector_store.as_retriever()
        history_aware_retriever = create_history_aware_retriever(self.llm, retriever, contextualize_q_prompt)

        # 3. QA Prompt
        system_prompt = (
            "Eres Mònica Sensat hablando con un posible recruiter. Responde BASÁNDOTE ÚNICAMENTE en el contexto proporcionado: {context}. "
            "IMPORTANTE: Detecta el idioma de la pregunta del usuario y responde EN ESE MISMO IDIOMA. "
            "Si la información sobre una habilidad específica no está en el contexto, di claramente que no tienes experiencia explícita en eso actualmente. "
            "SIN EMBARGO, añade siempre que si el proyecto es interesante, Mònica tiene total disposición y facilidad para aprender nuevas tecnologías rápidamente. "
            "Invita a contactar a monica@msensat.dev para discutirlo. "
            "Sé técnica pero cercana."
        )
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        async for chunk in rag_chain.astream({"input": question, "chat_history": chat_history}):
            if "answer" in chunk:
                yield chunk["answer"]
