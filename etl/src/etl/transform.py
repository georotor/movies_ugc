import logging
from datetime import datetime
from uuid import UUID, uuid4
from typing import Coroutine, Any, Callable

from aiokafka.structs import ConsumerRecord


logger = logging.getLogger(__name__)


class TransformConsumerRecord:
    def __init__(self, target: Callable[[list[tuple]], Coroutine[Any, Any, Any]] | None = None):
        self.target = target

    async def transform(self, data: list[ConsumerRecord]):
        buf = []
        for msg in data:
            buf.append((
                uuid4(),
                UUID(msg.key.decode('utf8').split('+')[0]),
                UUID(msg.key.decode('utf8').split('+')[1]),
                int(msg.value.decode('utf8')),
                datetime.utcfromtimestamp(int(msg.timestamp/1000))
            ))

        if self.target is not None:
            logger.info(f'Transform {len(buf)} records')
            await self.target(buf)
