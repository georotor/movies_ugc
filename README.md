# Movies: Сервис сбора данных о пользовательской активности

[![CI](https://github.com/georotor/movies_ugc/actions/workflows/tests.yml/badge.svg)](https://github.com/georotor/movies_ugc/actions/workflows/tests.yml)


## Архитектура

![Архитектура TO BE](https://github.com/georotor/movies_ugc/blob/main/docs/to_be.png?raw=true)

## Компоненты
- [FastAPI - реализация API](https://github.com/georotor/movies_ugc/tree/main/app)
- Kafka - брокер
- ClickHouse - хранилище для событий
- Redis - хранилище для кэша
- [ETL - для переноса данных из брокера в хранилище](https://github.com/georotor/movies_ugc/tree/main/etl)

## Выбор хранилища
[Тестирование производительности БД Vertica и ClickHouse](https://github.com/georotor/movies_ugc/tree/main/db_reasearch)

## Описание
В проекте реализована проверка JWT токена во внешнем сервисе с последующим кэшированием в Redis для снижения нагрузку на Auth сервис.
Данную проверку можно отключить установив переменную окружения `JWT_VALIDATE=0`, в этом случае JWT токен будет проверяться только на время действия.  

## Запуск
Для упрощения compose файлов, запуск сервиса разделен на несколько частей:
- брокер Kafka и сервис с API, принимающим данные от клиента:
  ```commandline
  docker-compose -f docker-compose.yml -f docker-compose.kafka.yml up
  ```
  
- хранилище ClickHouse и ETL принимающий данные из брокера:
  ```commandline
  docker-compose -f docker-compose.clickhouse.yml -f docker-compose.etl.yml up
  ```
  
## Тесты
Для запуска тестов API необходим брокер:
  ```commandline
  docker-compose -f docker-compose.kafka.yml up -d \
  && docker-compose -f app/src/tests/functional/docker-compose.yml up --build tests
  ```