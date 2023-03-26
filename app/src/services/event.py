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
        res = False
        try:
            await self.producer.send_and_wait(
                topic=event.topic,
                key=event.key.encode(),
                value=event.value.encode()
            )
            res = True
        except KafkaError:
            logger.error(f'Ошибка записи в топик {event.topic} сообщения {event.value}', exc_info=True)
        finally:
            await self.producer.flush()

        return res


@lru_cache()
def get_event_service(producer: AIOKafkaProducer = Depends(get_kafka)) -> EventHandler:
    return EventHandler(producer)
