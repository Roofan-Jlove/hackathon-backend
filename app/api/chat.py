from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime

from ..services.rag_service import rag_service  # Import the RAG service
from ..services.profile_service import ProfileService
from ..core.config import get_db, get_logger
from ..core.dependencies import get_current_user_optional
from ..models import Message, Conversation, User
from sqlalchemy.orm import Session
from sqlalchemy import and_

router = APIRouter()
logger = get_logger(__name__)

class ChatRequest(BaseModel):
    question: str
    context: Optional[str] = None
    conversation_id: Optional[UUID] = None  # Allow continuing existing conversations
    user_id: Optional[UUID] = None  # Optional user identification

class Source(BaseModel):
    chunk: str
    score: float
    source_file: Optional[str] = None
    chunk_index: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    conversation_id: UUID

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Receives a question and optional context, and returns a generated answer
    based on the book's content. Also manages conversation history.

    Supports optional authentication for personalized responses.
    """
    # Initialize or retrieve conversation
    conversation_id = request.conversation_id or uuid4()

    # Get user profile if authenticated for personalization
    user_profile = None
    if current_user:
        user_profile = ProfileService.get_profile(db, current_user.id)
        logger.info(f"Chat request from authenticated user {current_user.email}, profile: {user_profile is not None}")

    # Process the question through RAG pipeline with optional personalization
    try:
        answer, sources = await rag_service.query_rag_pipeline(
            question=request.question,
            context=request.context,
            conversation_id=conversation_id,
            user_profile=user_profile  # Pass profile for personalization
        )

        # Create chat response
        response = ChatResponse(
            answer=answer,
            sources=sources,
            conversation_id=conversation_id
        )

        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during chat processing")

@router.post("/index-book")
async def index_book():
    """
    Endpoint to index the book content into the vector database.
    """
    try:
        await rag_service.index_book_content_if_needed()
        return {"status": "success", "message": "Book content indexed successfully"}
    except Exception as e:
        logger.error(f"Error indexing book: {e}")
        raise HTTPException(status_code=500, detail="Failed to index book content")

# Additional endpoints for conversation management
@router.get("/conversations/{user_id}")
async def get_user_conversations(user_id: UUID):
    """
    Retrieve all conversations for a specific user.
    """
    try:
        # This would require database access to persist conversations
        # For now, return an empty list or implement full DB integration
        return {"conversations": []}
    except Exception as e:
        logger.error(f"Error retrieving conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversations")

@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: UUID):
    """
    Retrieve a specific conversation with all its messages.
    """
    try:
        # This would require database access to persist conversations
        # For now, return an empty conversation or implement full DB integration
        return {"conversation_id": conversation_id, "messages": []}
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")
