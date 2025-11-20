from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.db import get_db
from backend.models import Rating, Message
from backend.schemas import RatingCreate

router = APIRouter()

@router.post("/rating")
async def create_rating(rating_data: RatingCreate, db: AsyncSession = Depends(get_db)):
    # Verify message exists and belongs to chat
    result = await db.execute(
        select(Message).where(
            Message.id == rating_data.message_id,
            Message.chat_id == rating_data.chat_id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Message not found")

    # Validate score
    if rating_data.score not in [1, -1]:
        raise HTTPException(status_code=400, detail="Score must be 1 or -1")

    # Create or update rating
    result = await db.execute(
        select(Rating).where(Rating.message_id == rating_data.message_id)
    )
    existing_rating = result.scalar_one_or_none()
    
    if existing_rating:
        existing_rating.score = rating_data.score
    else:
        rating = Rating(
            message_id=rating_data.message_id,
            score=rating_data.score
        )
        db.add(rating)
    
    await db.commit()
    return {"status": "success"}