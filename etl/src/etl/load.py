import logging

import backoff
from aiochclient import ChClient
from aiohttp import ClientSession

from core.config import settings

logger = logging.getLogger(__name__)


class LoadClickHouse:
    def __init__(self):
        self.conn = None

    @backoff.on_exception(backoff.expo, Exception)
    async def init(self):
        session = ClientSession()
        self.conn = ChClient(session, url=f'http://{settings.clickhouse_host}:{settings.clickhouse_port}')
        await self.init_db()

    async def init_db(self):
        await self.conn.execute('CREATE DATABASE if not exists practix ON CLUSTER company_cluster')
        await self.conn.execute("""
            CREATE TABLE if not exists practix.film_views ON CLUSTER company_cluster
                (
                    `id`        UUID,
                    `user_id`   UUID,
                    `film_id`   UUID,
                    `timestamp` Int32,
                    `created`   DateTime('UTC')
                )
                ENGINE = MergeTree
                    ORDER BY id"""
            )

    @backoff.on_exception(backoff.expo, Exception)
    async def load(self, data: list[tuple]):
        await self.conn.execute(
            """INSERT INTO practix.film_views(id,user_id,film_id,timestamp,created) VALUES""",
            *data,
        )

        logger.info(f"Insert {len(data)} rows in table practix.film_views")
