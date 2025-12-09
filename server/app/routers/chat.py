from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str

class ChatResponse(BaseModel):
    response: str
    user_id: str

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """
    Chat endpoint for Deep-Shiva conversational AI.
    
    TODO: Connect to Ollama LLM here for actual AI responses.
    TODO: Integrate VectorDB for RAG-based context retrieval.
    """
    
    # Mock response - Replace with Ollama integration
    mock_response = f"I am Deep-Shiva. I will soon be connected to Ollama to answer your question about '{request.message}'. For now, I can tell you that Uttarakhand is home to the sacred Char Dham - Kedarnath, Badrinath, Gangotri, and Yamunotri. How may I assist you further?"
    
    return ChatResponse(
        response=mock_response,
        user_id=request.user_id
    )
