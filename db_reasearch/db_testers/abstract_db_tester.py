from abc import ABC, abstractmethod

from db_managers.abstract_db_manager import AbstractDBManager


class AbstractInsertTester(ABC):
    """Описание интерфейса для проведения INSERT тестов."""
    def __init__(self, db: AbstractDBManager):
        self.db = db

    @staticmethod
    @abstractmethod
    def generate_fake_data(size: int):
        """Генерируем массив фейковых данных заданной длинны."""

    @abstractmethod
    def bulk_insert(self, values):
        """Тестируем вставку (INSERT) данных."""


class AbstractSelectTester(ABC):
    """Описание интерфейса для проведения SELECT тестов. """
    def __init__(self, db: AbstractDBManager):
        self.db = db

    @abstractmethod
    def _users_id(self):
        """Получаем список пользователей. Используется в других запросах."""

    @abstractmethod
    def _movies_id(self):
        """Получаем список фильмов. Используется в других запросах."""

    @abstractmethod
    def movies_by_user(self, values):
        """Тестируем SELECT по одному значению. Получаем список фильмов по
        id пользователя.

        """

    @abstractmethod
    def timestamp_by_user_and_movie(self, values):
        """Тестируем SELECT по двум значениям. Получаем временные метки по
        id фильма и id пользователя.

        """

    @abstractmethod
    def max_timestamps_by_user(self, values):
        """Тестируем SELECT MAX по одному значению. Получаем максимальную
        временную метку по id пользователя.

        """

    @abstractmethod
    def max_timestamps_by_user_and_movie(self, values):
        """Тестируем SELECT MAX по двумя значениям. Получаем максимальную метку
        по id фильма и id пользователя.

        """

    @abstractmethod
    def count_all(self):
        """Получаем количество записей в таблице."""
