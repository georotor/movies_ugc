from aiokafka import AIOKafkaProducer

producer: AIOKafkaProducer | None


async def get_kafka() -> AIOKafkaProducer:
    return producer
