from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from open_webui.constants import ERROR_MESSAGES
from open_webui.internal.db import get_async_session
from open_webui.utils.auth import get_verified_user

log = logging.getLogger(__name__)

router = APIRouter()


class MessageRequest(BaseModel):
    """Request model for character chat messages."""
    content: str
    conversation_history: Optional[list[dict]] = None


class MessageResponse(BaseModel):
    """Response model for character chat messages."""
    role: str
    content: str


@router.post('/message', response_model=MessageResponse)
async def send_character_message(
    request: MessageRequest,
    user=Depends(get_verified_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Send a message to the character chat and receive a response.
    
    Args:
        request: MessageRequest containing user message and conversation history
        user: Authenticated user
        db: Database session
        
    Returns:
        MessageResponse with assistant's reply
    """
    try:
        if not request.content or not request.content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Message content cannot be empty'
            )

        # Process the message with the character
        # This is a simple implementation that echoes back the user's message
        # In a real implementation, this would call an LLM or process through business logic
        response_content = generate_character_response(
            user_message=request.content,
            conversation_history=request.conversation_history or []
        )

        return MessageResponse(
            role='assistant',
            content=response_content
        )

    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT()
        )


def generate_character_response(
    user_message: str,
    conversation_history: list[dict]
) -> str:
    """
    Generate a response from the character.
    
    This is a simple implementation. In production, this could:
    - Call an LLM API (OpenAI, Ollama, etc.)
    - Use retrieval-augmented generation (RAG)
    - Process through custom business logic
    
    Args:
        user_message: The user's message
        conversation_history: Previous messages in the conversation
        
    Returns:
        The character's response text
    """
    # Simple response generation
    # In production, replace this with actual LLM integration
    character_personality = "a helpful and friendly character"
    
    response = f"Thank you for your message! As {character_personality}, I'd like to respond to: '{user_message}'"
    
    if conversation_history:
        response += f" This is message #{len(conversation_history) + 1} in our conversation."
    
    return response


@router.get('/test')
async def test_character_chat():
    """
    Test endpoint to verify character chat is working.
    No authentication required for testing.
    """
    return {
        'status': 'Character chat is working',
        'message': 'API endpoint is accessible and operational!'
    }
