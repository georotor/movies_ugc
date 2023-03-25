from typing import Optional

import vertica_python
from db_managers.abstract_db_manager import AbstractDBManager


class VerticaManager(AbstractDBManager):
    def __init__(self, connection: vertica_python.connect):
        self.connection = connection
        self.cursor = connection.cursor()

    def init_db(self):
        """Создаем схему и таблицу БД. Предполагается использование
        'autocommit': True, отдельного поэтому коммита не делаем.

        """
        self.cursor.execute("""CREATE SCHEMA IF NOT EXISTS test;""")
        self.cursor.execute('DROP TABLE IF EXISTS test.views;')
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test.views (
                id IDENTITY,
                user_id UUID NOT NULL,
                movie_id UUID NOT NULL,
                timestamp INTEGER NOT NULL,
                event_time DATETIME NOT NULL
            )
            ORDER BY id;
            """
        )

    def insert(self, sql, values: list[dict]):
        """Выполнение массового (bulk) INSERT запроса к БД.
        Подробнее про use_prepared_statements:
        https://github.com/vertica/vertica-python#passing-parameters-to-sql-queries

        Args:
          sql: строка с SQL запросом;
          values: список из словарей со значениями для SQL запроса.

        """

        self.cursor.executemany(sql, values, use_prepared_statements=True)

    def select(self, sql: str, values: Optional[list] = None):
        """Выполнение SELECT запроса к БД. В рамках тестирования нас устроит
        обычный fetchall().

        Args:
          sql: строка с SQL запросом;
          values: словарь со значениями для SQL запроса.

        """
        self.cursor.execute(sql, values)
        return self.cursor.fetchall()
