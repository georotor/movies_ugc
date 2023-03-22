from uuid import UUID

from fastapi import APIRouter, Depends

from models.event import Event
from services.auth import JWTBearer
from services.event import EventHandler, get_event_service

router = APIRouter()


@router.post('/film/views')
async def events(film_id: UUID, value: int, user_id: UUID = Depends(JWTBearer()),
                 handler: EventHandler = Depends(get_event_service)):

    event = Event(
        topic='film_views',
        key=f'{user_id}+{film_id}',
        value=value
    )

    return await handler.send(event)
