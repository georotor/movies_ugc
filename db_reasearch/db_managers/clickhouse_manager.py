from clickhouse_driver import Client
from db_managers.abstract_db_manager import AbstractDBManager


class ClickHouseManager(AbstractDBManager):
    def __init__(self, connection: Client):
        self.client = connection

    def init_db(self):
        self.client.execute("""CREATE DATABASE IF NOT EXISTS test;""")
        self.client.execute('DROP TABLE IF EXISTS test.views;')
        self.client.execute(
            """
            CREATE TABLE test.views (
                id UUID,
                user_id UUID,
                movie_id UUID,
                timestamp UInt32,
                event_time DateTime
            ) Engine=MergeTree() ORDER BY id
            """
        )

    def insert(self, sql: str, values: list[dict]):
        """Выполнение массового (bulk) INSERT запроса к БД.

        Args:
          sql: строка с SQL запросом;
          values: список из словарей со значениями для SQL запроса.

        """

        self.client.execute(sql, values)

    def select(self, sql, values=None):
        """Выполнение SELECT запроса к БД.

        Args:
          sql: строка с SQL запросом;
          values: словарь со значениями для SQL запроса.

        """
        return self.client.execute(sql, values)
