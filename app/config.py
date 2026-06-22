from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "area-service";

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092";
    KAFKA_PRODUCE_TOPIC: str = "area.events"

    DATABASE_URL: str;

    class Config:
        env_file = ".env";
        extra = "ignore";

settings = Settings();
