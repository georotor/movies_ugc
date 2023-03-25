import logging
import random
import time
from typing import Any, Callable

from mimesis import Generic

fake = Generic()

logger = logging.getLogger('db_test_logger')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('test_results_{}'.format(int(time.time())))
fh.setLevel(logging.INFO)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)



def calculate_average(
        func: Callable, data: list[list[Any]], logger=logger
) -> float:
    """Запускает функцию несколько раз и возвращает среднее время работы.
    Данные, которые возвращала оригинальная функция, при этом игнорируются.

    Args:
      func: функция (метод) для запуска;
      data: список из списка аргументов для каждого запуска;
      logger: логгер, рекомендованные уровни - DEBUG для StreamHandler и
      INFO для FileHandler.

    """
    result = []
    for func_args in data:
        start_time = time.monotonic()
        func(*func_args)
        result_time = time.monotonic() - start_time
        result.append(result_time)
        logger.debug(
            '   - {}: {} seconds'.format(func.__name__, result_time)
        )

    average = sum(result) / len(result)
    logger.info(
        ' - тест: {}, попыток: {}, среднее время: {}'.format(
            func.__name__, len(result), average
        )
    )
    return average


def create_users_query(user_id_lst) -> list[list[dict]]:
    """Формирует список аргументов для запуска остальных select тестов через
    calculate_average.

    Args:
      user_id_lst: список id пользователей.

    """
    users = [[{'user_id': user}] for user in user_id_lst]
    return users


def create_users_and_movies_query(
        user_id_lst, movies_id_lst
) -> list[list[dict]]:
    """Формирует список аргументов для запуска остальных select тестов через
    calculate_average.

    Args:
      user_id_lst: список id пользователей;
      movies_id_lst: список id фильмов.

    """
    users_and_movies = []
    for _ in range(len(user_id_lst) * 2):
        users_and_movies.append(
            [
                {
                    "user_id": random.choice(user_id_lst),
                    "movie_id": random.choice(movies_id_lst),
                }
            ]
        )
    return users_and_movies
