from typing import Coroutine, Any, Callable

import backoff
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from aiokafka.structs import ConsumerRecord

from core.config import settings


class ExtractKafka:
    def __init__(self, target: Callable[[list[ConsumerRecord]], Coroutine[Any, Any, Any]] | None = None):
        self.target = target
        self.consumer = AIOKafkaConsumer(
            settings.extract_topic,
            bootstrap_servers=f'{settings.kafka_host}:{settings.kafka_port}',
            group_id=f"etl_{settings.extract_topic}",
            enable_auto_commit=False,
            auto_offset_reset="earliest"
        )

    @backoff.on_exception(backoff.expo, KafkaConnectionError)
    async def start(self):
        await self.consumer.start()
        buf = []
        try:
            async for msg in self.consumer:
                buf.append(msg)
                if len(buf) == settings.extract_batch_size:
                    if self.target is not None:
                        await self.target(buf)
                    await self.consumer.commit()
                    buf = []
        finally:
            await self.consumer.stop()
