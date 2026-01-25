🤖 MSensat AI Assistant
This is a virtual assistant based on RAG (Retrieval-Augmented Generation) integrated into my personal portfolio msensat.dev. The bot allows users to interact with my professional background, education, and technical projects in a conversational and real-time manner.

🚀 Technology Stack
Backend: FastAPI (Python)

AI / LLM: Llama 3.1 70B via Groq (Streaming enabled)

Orchestration: LangChain

Vector Store: FAISS (In-memory)

Frontend: Hugo (Toha Theme) + Vanilla JS / Bootstrap

Deployment: Docker

🛠️ Architecture
The bot consumes data directly from my website's HTML through a scraping and vectorization process at runtime:

Ingestion: Uses WebBaseLoader to fetch content from msensat.dev.

Chunking: Text is split using RecursiveCharacterTextSplitter.

Memory: Implementation of ConversationalRetrievalChain to maintain conversation context.

Streaming: Responses via FastAPI's StreamingResponse for a smooth UX.

📦 Installation and Usage
1. Clone the repository
Bash

git clone https://github.com/your-username/msensat-ai-bot.git
cd msensat-ai-bot
2. Configure environment variables
Create a .env file in the root:

Code snippet

GROQ_API_KEY=your_groq_api_key
CONTENT_ORIGIN=https://msensat.dev
EXTRA_KNOWLEDGE="Optional extra context"
USER_AGENT="CVchat/1.0"

> **Note**: `USER_AGENT` is required to avoid 403/406 blocking errors when fetching content from your website. It identifies the bot to the server.
3. Run with Docker
Bash

docker build -t msensat-bot .
docker run -p 8000:8000 msensat-bot
🔌 API Endpoints
POST /chat
Send a question and receive a text stream.

Body:

JSON

{
  "message": "What experience does Mònica have in Rust?",
  "history": []
}
📝 Hugo Customization (Toha)
The frontend integration is done through a custom partial and a script that handles the ReadableStream reader to display the response word by word.

🌍 Multilingual Support
The chatbot automatically works in **Catalan, Spanish, and English** without additional configuration:

- **Automatic detection**: The Llama 3.3 70B model detects the language of the question and responds in the same language
- **Multilingual content**: The RAG loads all content from msensat.dev as is, including all available languages
- **Multilingual embeddings**: The all-MiniLM-L6-v2 model supports multiple languages for semantic search

Simply ask in your preferred language and the bot will respond naturally in that same language.