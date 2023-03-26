import logging
from functools import lru_cache

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from fastapi import Depends

from db.kafka import get_kafka
from models.event import Event


logger = logging.getLogger(__name__)


class EventHandler:
    def __init__(self, producer: AIOKafkaProducer):
        self.producer = producer

    async def send(self, event: Event) -> bool:
        try:
            await self.producer.send(
                topic=event.topic,
                key=event.key.encode(),
                value=event.value.encode()
            )
            return True
        except KafkaError:
            logger.error(f'Ошибка записи в топик {event.topic} сообщения {event.key}:{event.value}', exc_info=True)

        return False


@lru_cache()
def get_event_service(producer: AIOKafkaProducer = Depends(get_kafka)) -> EventHandler:
    return EventHandler(producer)
