from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.services.translation_service import translation_service
from app.models import User
from app.core.config import get_logger

router = APIRouter()
logger = get_logger(__name__)

class TranslateRequest(BaseModel):
    text: str
    target_language: str = "ur"
    source_file: str

    class Config:
        json_schema_extra = {
            "example": {
                "text": "# Week 1: Introduction to ROS 2\n\nROS is a flexible framework for writing robot software.",
                "target_language": "ur",
                "source_file": "module-1-ros-foundations/week-1.mdx"
            }
        }

class TranslateResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    cached: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "translated_text": "# ہفتہ 1: ROS 2 کا تعارف\n\nROS روبوٹ سافٹ ویئر لکھنے کے لیے ایک لچکدار فریم ورک ہے۔",
                "source_language": "en",
                "target_language": "ur",
                "cached": False
            }
        }

@router.post("/translate", response_model=TranslateResponse, tags=["translation"])
async def translate_content(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Translate markdown content to target language (Urdu).

    **Authentication Required**: Must be logged in with valid JWT token.

    **Request Body**:
    - `text`: Markdown content to translate
    - `target_language`: Target language code (default: "ur" for Urdu)
    - `source_file`: File path for logging/caching purposes

    **Response**:
    - `translated_text`: Translated markdown content
    - `source_language`: Detected source language
    - `target_language`: Target language
    - `cached`: Whether result was from cache (future enhancement)
    """
    logger.info(f"Translation request from user {current_user.id} for file {request.source_file}")

    if not request.text or request.text.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )

    if len(request.text) > 50000:  # Limit to ~50KB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text too long (max 50,000 characters)"
        )

    try:
        translated_text = await translation_service.translate_text(
            request.text,
            request.target_language
        )

        if not translated_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Translation failed. Please try again later."
            )

        logger.info(f"Translation completed for user {current_user.id}")

        return TranslateResponse(
            translated_text=translated_text,
            source_language="en",
            target_language=request.target_language,
            cached=False
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during translation"
        )
