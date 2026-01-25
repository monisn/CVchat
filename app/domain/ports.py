
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict

class ChatServicePort(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize resources (e.g. load vectors)."""
        pass

    @abstractmethod
    async def stream_response(self, question: str, history: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Generate a streaming response for the user question."""
        pass
