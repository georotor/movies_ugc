from mimesis import Generic

from .abstract_db_tester import AbstractInsertTester, AbstractSelectTester

fake = Generic()


class ClickHouseInsertTester(AbstractInsertTester):
    @staticmethod
    def generate_fake_data(size: int) -> list:
        """Генерируем фейковые данные. В ClickHouse поле id заполняем в явном
        виде.

        """
        fake_data = []
        for _ in range(size):
            fake_data.append(
                (
                    fake.cryptographic.uuid_object(),
                    fake.cryptographic.uuid_object(),
                    fake.cryptographic.uuid_object(),
                    fake.datetime.timestamp(),
                    fake.datetime.datetime(start=2000, end=2023),
                )
            )
        return fake_data

    def bulk_insert(self, size):
        """Тестируем вставку (INSERT) данных."""
        sql = """
                INSERT INTO test.views
                (id, user_id, movie_id, timestamp, event_time) VALUES
        """
        self.db.insert(sql, self.generate_fake_data(size))


class ClickHouseSelectTester(AbstractSelectTester):
    def _users_id(self):
        """Получаем список пользователей. Используется в других запросах."""
        return self.db.select('SELECT DISTINCT user_id from test.views')

    def _movies_id(self):
        """Получаем список фильмов. Используется в других запросах."""
        return self.db.select('SELECT DISTINCT movie_id from test.views')

    def movies_by_user(self, values):
        """Тестируем SELECT по одному значению. Получаем список фильмов по
        id пользователя.

        """
        sql = """
            SELECT DISTINCT (movie_id)
            FROM test.views
            WHERE user_id = %(user_id)s
        """
        return self.db.select(sql, values)

    def timestamp_by_user_and_movie(self, values):
        """Тестируем SELECT по двум значениям. Получаем временные метки по
        id фильма и id пользователя.

        """
        sql = """
            SELECT movie_id, timestamp
            FROM test.views
            WHERE movie_id = %(movie_id)s
            AND user_id = %(user_id)s
        """
        return self.db.select(sql, values)

    def max_timestamps_by_user(self, values):
        """Тестируем SELECT MAX по одному значению. Получаем максимальную
        временную метку по id пользователя.

        """
        sql = """
            SELECT movie_id, max(timestamp)
            FROM test.views
            WHERE user_id = %(user_id)s
            GROUP BY movie_id
        """
        return self.db.select(sql, values)

    def max_timestamps_by_user_and_movie(self, values):
        """Тестируем SELECT MAX по двумя значениям. Получаем максимальную метку
        по id фильма и id пользователя.

        """
        sql = """
            SELECT MAX (timestamp)
            FROM test.views
            WHERE movie_id = %(movie_id)s
            AND user_id = %(user_id)s
        """
        return self.db.select(sql, values)

    def count_all(self):
        """Получаем количество записей в таблице."""
        sql = """
            SELECT COUNT() FROM test.views;
        """
        return self.db.select(sql, None)
