from pydantic import BaseModel, BaseSettings


class Logging(BaseModel):
    level_root: str = 'INFO'
    level_uvicorn: str = 'INFO'
    level_console: str = 'DEBUG'


class Settings(BaseSettings):
    project_name: str = 'ugc'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    jwt_validate: bool = True
    cache_expire: int = 600
    logging: Logging = Logging()
    auth_url: str = 'http://127.0.0.1:5000/api/v1/user/is_authenticated'

    class Config:
        env_nested_delimiter = '__'


settings = Settings()
