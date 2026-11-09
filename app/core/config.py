from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    robot_names: str
    robotcorp_topic: str
    kafka_bootstrap_servers: str
    my_name: str
