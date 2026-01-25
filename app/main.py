from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.adapters.langchain_rag import LangChainRAGAdapter
from app.adapters.api import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize implementation
    adapter = LangChainRAGAdapter()
    await adapter.initialize()
    
    # Store in app state for dependency injection
    app.state.chat_service = adapter
    yield

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS, 
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_router)
    return app

app = create_app()
