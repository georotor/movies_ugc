from abc import ABC, abstractmethod


class AbstractDBManager(ABC):
    """Описание интерфейса для работы с БД. Позволяет создать таблицу,
    выполнить INSERT и SELECT запросы. Используется для тестирования
    производительности.

    """
    @abstractmethod
    def init_db(self):
        """Инициализация БД: создание схем, таблиц и пр."""

    @abstractmethod
    def insert(self, sql, values):
        """Выполнение массового (bulk) INSERT запроса к БД."""

    @abstractmethod
    def select(self, sql, values=None):
        """Выполнение SELECT запроса к БД."""
