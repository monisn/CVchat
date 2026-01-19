import os
import asyncio
from contextlib import asynccontextmanager

# Configurar USER_AGENT para evitar warnings/bloqueos
os.environ["USER_AGENT"] = "CVchat/1.0"
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import AsyncGenerator

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    loaders = [WebBaseLoader(os.getenv("CONTENT_ORIGIN"))]
    
    if os.path.exists("extra_knowledge.txt"):
        from langchain_community.document_loaders import TextLoader
        loaders.append(TextLoader("extra_knowledge.txt"))

    extra_env_info = os.getenv("EXTRA_KNOWLEDGE")
    if extra_env_info:
        from langchain_core.documents import Document
        # Later add the document
        pass

    docs = []
    for loader in loaders:
        docs.extend(loader.load())
    
    if extra_env_info:
        from langchain_core.documents import Document
        docs.append(Document(page_content=extra_env_info, metadata={"source": "env_extra_knowledge"}))

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    vector_store = FAISS.from_documents(splits, embeddings)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CONTENT_ORIGIN"), "http://localhost:1313"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = [] # Formato: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

async def stream_response(question: str, history: list) -> AsyncGenerator[str, None]:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", # Actualizado a Llama 3.3
        api_key=os.getenv("GROQ_API_KEY"),
        streaming=True,
        temperature=0.7
    )
    # 1. Convertir historial plano a objetos de mensaje de LangChain
    chat_history = []
    for h in history:
        if h["role"] == "user":
            chat_history.append(HumanMessage(content=h["content"]))
        else:
            chat_history.append(AIMessage(content=h["content"]))

    # 2. Prompt para reformular la pregunta basándose en el historial
    contextualize_q_system_prompt = "Dada la charla y la última pregunta, formula una pregunta independiente."
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    retriever = vector_store.as_retriever()
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    # 3. Prompt de respuesta final
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

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # 4. Generar el stream de tokens
    async for chunk in rag_chain.astream({"input": question, "chat_history": chat_history}):
        if "answer" in chunk:
            yield chunk["answer"]

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    return StreamingResponse(stream_response(request.message, request.history), media_type="text/event-stream")