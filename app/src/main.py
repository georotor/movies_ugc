from logging import config as logging_config

import uvicorn
import redis.asyncio as aioredis
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import events
from core.config import settings
from core.logger import LOGGING
from db import redis, kafka

logging_config.dictConfig(LOGGING)

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    if settings.jwt_validate:
        redis.client = await aioredis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}",
            encoding="utf8",
            decode_responses=True,
            max_connections=20,
        )
    kafka.producer = AIOKafkaProducer(
        bootstrap_servers=f'{settings.kafka_host}:{settings.kafka_port}',
        max_batch_size=1024
    )


@app.on_event("shutdown")
async def shutdown():
    await redis.client.close()
    await kafka.producer.stop()


app.include_router(events.router, prefix="/api/v1/events", tags=["events"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
