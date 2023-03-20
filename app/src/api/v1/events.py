from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from services.auth import JWTBearer


router = APIRouter()


@router.post('')
async def events(
        film_id: UUID,
        value: int,
        user_id: UUID = Depends(JWTBearer())
):
    return user_id
