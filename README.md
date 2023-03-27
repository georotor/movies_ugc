# Проектная работа 8 спринта

Репозиторий: https://github.com/georotor/ugc_sprint_1

## Архитектура
<details><summary><b>AS IS</b></summary>

![Архитектура AS IS](https://github.com/georotor/ugc_sprint_1/blob/main/docs/as_is.png?raw=true)

</details>

<details><summary><b>TO BE</b></summary>

![Архитектура TO BE](https://github.com/georotor/ugc_sprint_1/blob/main/docs/to_be.png?raw=true)

</details>

## Выбор хранилища
[Тестирование производительности БД Vertica и ClickHouse](https://github.com/georotor/ugc_sprint_1/tree/main/db_reasearch)

## Описание
В проекте реализована проверка JWT токена во внешнем сервисе с последующим кэшированием в Redis для снижения нагрузку на Auth сервис.
Данную проверку можно отключить установив переменную окружения `JWT_VALIDATE=0`, в этом случае JWT токен будет проверяться только на время действия.  

## Запуск
Для упрощения compose файлов, запуск проекта разделен на несколько частей:
- брокер Kafka и сервис принимающий данные от клиента:
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
  docker-compose -f docker-compose.kafka.yml -f app/src/tests/functional/docker-compose.yml up
  ```