import enum
from multiprocessing import Process

import clickhouse_driver
import vertica_python
from db_managers.clickhouse_manager import ClickHouseManager
from db_managers.vertica_manager import VerticaManager
from db_testers.abstract_db_tester import (AbstractInsertTester,
                                           AbstractSelectTester)
from db_testers.clickhouse_tester import (ClickHouseInsertTester,
                                          ClickHouseSelectTester)
from db_testers.utils import (calculate_average, create_users_and_movies_query,
                              create_users_query, get_logger)
from db_testers.vertica_tester import VerticaInsertTester, VerticaSelectTester

RETRIES = 10
CHUNK_SIZES = [10, 100, 1000, 10000, 100000]

logger = get_logger()


class DataBase(enum.Enum):
    Vertica = 0
    ClickHouse = 1


def test_factory(
        db: DataBase, main_db_conn, alt_db_conn
) -> (AbstractInsertTester, AbstractSelectTester):
    """Фабрика, инициализирует БД и возвращает экземпляры классов-тестеров.
    Часть тестов проходит в два потока, поэтому подключений к БД несколько.

    Args:
      db: название тестируемой БД;
      main_db_conn: инициализированное подключение к БД для INSERT тестов;
      alt_db_conn: инициализированное подключение к БД для SELECT тестов.

    """
    db_testers = {
        DataBase.Vertica: [
            VerticaManager, VerticaInsertTester, VerticaSelectTester
        ],
        DataBase.ClickHouse: [
            ClickHouseManager, ClickHouseInsertTester, ClickHouseSelectTester
        ],
    }

    db_manager_cls, insert_tester_cls, select_tester_cls = db_testers[db]

    main_db_manager = db_manager_cls(connection=main_db_conn)
    alt_db_manager = db_manager_cls(connection=alt_db_conn)
    main_db_manager.init_db()

    insert = insert_tester_cls(db=main_db_manager)
    select = select_tester_cls(db=alt_db_manager)

    return insert, select


def run_tests(insert, select):
    """Запуск тестов. Они проходят в три этапа:

    INSERT тесты проверяют скорость вставки данных и заодно наполняют БД.
    SELECT тесты проверяют скорость чтения данных в идеальных условиях.
    СТРЕСС тесты проверяют скорость чтения данных под нагрузкой, с параллельной
    записью данных.

    Все тесты запускаются через calculate_average. Тестируются только время
    работы, сами результаты запросов к БД игнорируются.

    DEBUG выводится в консоль - это данные по времени работы каждого теста.
    INFO пишется в файл - это среднее время работы каждой группы тестов.

    Args:
      insert: инициализированный экземпляр класса для INSERT тестов;
      select: инициализированный экземпляр класса для SELECT тестов.

    """
    logger.info('=== INSERT тесты {} ==='.format(insert.__class__.__name__))

    for chunk_size in CHUNK_SIZES:
        logger.info('--- вставка по {} записей ---'.format(chunk_size))
        calculate_average(insert.bulk_insert, [[chunk_size]] * RETRIES)

    logger.info('=== SELECT тесты {} ==='.format(select.__class__.__name__))

    user_id_lst = select._users_id()
    movies_id_lst = select._movies_id()

    users = create_users_query(user_id_lst)
    users_and_movies = create_users_and_movies_query(
        user_id_lst, movies_id_lst
    )

    calculate_average(select.movies_by_user, users)
    calculate_average(select.max_timestamps_by_user, users)
    calculate_average(select.timestamp_by_user_and_movie, users_and_movies)
    calculate_average(select.max_timestamps_by_user_and_movie, users_and_movies)
    calculate_average(select.count_all, [[]] * RETRIES)

    logger.info('=== СТРЕСС тесты в несколько потоков ===')

    loader = Process(
        target=calculate_average, args=(insert.bulk_insert, [[1]] * len(users))
    )
    test = Process(
        target=calculate_average, args=(select.max_timestamps_by_user, users)
    )
    loader.start()
    test.start()

    loader.join()
    test.join()


if __name__ == '__main__':
    # В нашем случае речь идет об одноразовых тестах "пустых" БД, повторный
    # запуск не предполагается. Выносить настройки в settings и env нет смысла.

    connection_info = {
        'host': '127.0.0.1',
        'port': 5433,
        'user': 'dbadmin',
        'password': '',
        'database': 'docker',
        'autocommit': True,
    }

    # Два подключения нужно для проверки одновременной работы SELECT и INSERT
    with vertica_python.connect(**connection_info) as conn:
        with vertica_python.connect(**connection_info) as conn_alt:
            insert, select = test_factory(DataBase.Vertica, conn, conn_alt)
            run_tests(insert, select)

    with clickhouse_driver.Client(host="localhost") as conn:
        with clickhouse_driver.Client(host="localhost") as conn_alt:
            insert, select = test_factory(DataBase.ClickHouse, conn, conn_alt)
            run_tests(insert, select)
