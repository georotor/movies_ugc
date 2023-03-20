from redis.asyncio.client import Redis


client: Redis | None = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return client
