
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.domain.models import ChatRequest
from app.domain.ports import ChatServicePort

# We will need a way to get the service instance. 
# For now, we can use a basic dependency pattern.
def get_chat_service(request: Request) -> ChatServicePort:
    return request.app.state.chat_service

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, service: ChatServicePort = Depends(get_chat_service)):
    return StreamingResponse(
        service.stream_response(request.message, request.history), 
        media_type="text/event-stream"
    )
