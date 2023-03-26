import asyncio
from logging import config as logging_config

from core.logger import LOGGING
from etl.extract import ExtractKafka
from etl.transform import TransformConsumerRecord
from etl.load import LoadClickHouse

logging_config.dictConfig(LOGGING)


async def etl():
    _load = LoadClickHouse()
    await _load.init()
    _transform = TransformConsumerRecord(target=_load.load)
    _extract = ExtractKafka(target=_transform.transform)
    await _extract.start()


if __name__ == '__main__':
    asyncio.run(etl())
