from pydantic import BaseModel, BaseSettings


class Logging(BaseModel):
    level_root: str = 'INFO'
    level_console: str = 'DEBUG'


class Settings(BaseSettings):
    kafka_host: str = 'localhost'
    kafka_port: int = 9092

    extract_topic: str = 'film_views'
    extract_batch_size: int = 1024

    clickhouse_host: str = 'localhost'
    clickhouse_port: int = 8123

    logging: Logging = Logging()

    class Config:
        env_nested_delimiter = '__'


settings = Settings()
