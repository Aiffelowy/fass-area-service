import json
from aiokafka import AIOKafkaProducer
from app.config import settings

class KafkaEventProducer:
    def __init__(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS);

    async def start(self):
        await self.producer.start();

    async def stop(self):
        await self.producer.stop();

    async def send_event(self, event_type: str, payload: dict):
        message = {
            "event_type": event_type,
            "payload": payload
        };
        await self.producer.send_and_wait(
            settings.KAFKA_PRODUCE_TOPIC, 
            json.dumps(message).encode('utf-8')
        );

kafka_producer = KafkaEventProducer();
