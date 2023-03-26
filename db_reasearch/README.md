# Тестирование производительность БД Vertica и ClickHouse

Условия тестирования
-

У каждой БД использовалась только одна нода. 

Обе БД запускались в docker контейнере со следующими ограничениями:

      cpus: '4'
      memory: 4G



Запуск контейнера
-

Контейнер собран на основе следующий образов:

- Vertica : jbfavre/vertica:9.2.0-7_debian-8
- ClickHouse: yandex/clickhouse-server:21.3.20

Запуск контейнера осуществляется следующей командой: 

```commandline
docker-compose up -d
```

Запуск тестов
-

Тесты запускаются локально. Для этого нужно:

1. Создать и активировать виртуальное окружение:
```commandline
python3.10 -m venv venv
. venv/bin/activate
```
2. Установить зависимости
```commandline
pip install -r requirements.txt
```
3. Запустить main.py:
```commandline
python3 ./main.py
```

Структура БД
-

**Схема таблицы Vertica:**
```sql
CREATE TABLE IF NOT EXISTS test.views (
    id IDENTITY,
    user_id UUID NOT NULL,
    movie_id UUID NOT NULL,
    timestamp INTEGER NOT NULL,
    event_time DATETIME NOT NULL
)
ORDER BY id;
```

**Схема таблицы ClickHouse:**
```sql
CREATE TABLE test.views (
    id UUID,
    user_id UUID,
    movie_id UUID,
    timestamp UInt32,
    event_time DateTime
) Engine=MergeTree() ORDER BY id
```

INSERT тесты
-

**Описание тестов:**
1. Вставка данных производилась пачками по 10, 100, 1000 записей. Каждый тест проводился 10 раз, затем считалось среднее время.

- Запрос Vertica:
```sql
INSERT INTO test.views
(user_id, movie_id, timestamp, event_time)
VALUES (?, ?, ?, ?);
```

- Запрос ClickHouse:
```sql
INSERT INTO test.views
(id, user_id, movie_id, timestamp, event_time)
VALUES
```

**Результаты Vertica:**

- вставка по 10 записей, среднее время: 0.04989
- вставка по 100 записей, среднее время: 0.47988
- вставка по 1000, среднее время: 4.57719

**Результаты ClickHouse:**

- вставка по 10 записей, среднее время: 0.00352
- вставка по 100 записей, среднее время: 0.00547
- вставка по 1000, среднее время: 0.02820


SELECT тесты
-

**Описание тестов:**

Тесты велись по внесенным на прошлом шаге данным. К этому моменту в БД было чуть более 10 000 записей.

1. Поиск по одному значению (поиск фильма по id пользователя).

- Запрос Vertica:
```sql
SELECT DISTINCT (movie_id)
FROM test.views
WHERE user_id = :user_id;
```

- Запрос ClickHouse:
```sql
SELECT DISTINCT (movie_id)
FROM test.views
WHERE user_id = %(user_id)s
```

2. Поиск по двум значениям (поиск временных меток по id фильма и id пользователя)

- Запрос Vertica:
```sql
SELECT movie_id, timestamp
FROM test.views
WHERE movie_id = :movie_id
AND user_id = :user_id
```

- Запрос ClickHouse:
```sql
SELECT movie_id, timestamp
FROM test.views
WHERE movie_id = %(movie_id)s
AND user_id = %(user_id)s
```

3. Поиск MAX по одному значению (поиск наибольших временных меток по id пользователя)

- Запрос Vertica:
```sql
SELECT movie_id, max(timestamp)
FROM test.views
WHERE user_id = :user_id
GROUP BY movie_id
```

- Запрос ClickHouse:
```sql
SELECT movie_id, max(timestamp)
FROM test.views
WHERE user_id = %(user_id)s
GROUP BY movie_id
```

4. Поиск MAX по двум значениям (поиск наибольших временных меток по id пользователя и id фильма)

- Запрос Vertica:
```sql
SELECT MAX (timestamp)
FROM test.views
WHERE movie_id = :movie_id
AND user_id = :user_id
```

- Запрос ClickHouse:
```sql
SELECT MAX (timestamp)
FROM test.views
WHERE movie_id = %(movie_id)s
AND user_id = %(user_id)s
```

5. Подсчет количества записей в таблице

- Запрос Vertica:
```sql
SELECT COUNT(*) FROM test.views;
```

- Запрос ClickHouse:
```sql
SELECT COUNT() FROM test.views;
```

**Результаты Vertica:**

1. тест movies_by_user, попыток: 10473, среднее время: 0.00945
2. тест max_timestamps_by_user, попыток: 10473, среднее время: 0.00874
3. тест timestamp_by_user_and_movie, попыток: 20946, среднее время: 0.00522
4. тест max_timestamps_by_user_and_movie, попыток: 20946, среднее время: 0.00584
5. тест count_all, попыток: 10, среднее время: 0.00521

**Результаты ClickHouse:**

1. тест: movies_by_user, попыток: 11100, среднее время: 0.00311
2. тест: max_timestamps_by_user, попыток: 11100, среднее время: 0.00341
3. тест: timestamp_by_user_and_movie, попыток: 22200, среднее время: 0.00345
4. тест: max_timestamps_by_user_and_movie, попыток: 22200, среднее время: 0.00362
5. тест: count_all, попыток: 10, среднее время: 0.00207

СТРЕСС тесты
-

**Описание тестов:**

Тесты велись в два потока. Первый поток имитирует фоновую нагрузку и записывает в БД 10 000 записей, по записи одной за раз.
Во втором потоке выполняется SELECT тест №2 (max_timestamps_by_user).

**Результаты Vertica:**

1. тест bulk_insert, попыток: 10473, среднее время: 0.00736
2. тест max_timestamps_by_user, попыток: 10473, среднее время: 0.01015

**Результаты ClickHouse:**

1. тест bulk_insert, попыток: 11100, среднее время: 0.00517
2. тест max_timestamps_by_user, попыток: 11100, среднее время: 0.00529
