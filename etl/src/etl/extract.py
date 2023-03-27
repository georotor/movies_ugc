import asyncio
import logging
from typing import Coroutine, Any, Callable

import backoff
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from aiokafka.structs import ConsumerRecord

from core.config import settings


logger = logging.getLogger(__name__)


class ExtractKafka:
    def __init__(self, target: Callable[[list[ConsumerRecord]], Coroutine[Any, Any, Any]] | None = None):
        self.task = None
        self.buf = []
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

        async for msg in self.consumer:
            self.buf.append(msg)
            await self.set_task()

            if len(self.buf) == settings.extract_batch_size:
                await self.clear_task()
                await self.next()

        await self.consumer.stop()

    async def next(self):
        if self.target is not None:
            logger.info(f'Extract {len(self.buf)} messages')
            await self.target(self.buf)

        await self.consumer.commit()
        self.buf.clear()

    async def set_task(self):
        await self.clear_task()
        self.task = asyncio.ensure_future(self.run_task())

    async def clear_task(self):
        if self.task is not None:
            self.task.cancel()

    async def run_task(self):
        await asyncio.sleep(settings.extract_wait_msg)
        logger.info('Execute task')
        await self.next()
