import asyncio
import json
from fastapi import FastAPI
from typing import List
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from random import shuffle
from app.core.config import Settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(consume())
    yield  

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="last-robot-standing", version="0.1.0", lifespan=lifespan)

settings = Settings()

robot_names: List[str] = [name.strip() for name in settings.robot_names.split(",")]
kafka_bootstrap_servers: str = settings.kafka_bootstrap_servers
robotcorp_topic: str = settings.robotcorp_topic

my_name: str =  settings.my_name

mapping_place = {
    3: "name is in Third Place!!!",
    2: "name is in Second Place!!!",
    1: "name is the Winner!!!",
}


def robot_random(robot_list: List) -> List:
    shuffle(robot_list)
    return robot_list


async def play_turn(finalists: List):
    robot_order = robot_random(finalists)
    await send_one(topic=robotcorp_topic, msg=robot_order)


def kafka_serializer(value):
    return json.dumps(value).encode()


def encode_json(msg):
    to_load = msg.value.decode("utf-8")
    return json.loads(to_load)


def check_robot(finalists: List) -> bool:
    return my_name == finalists[0]


async def send_one(topic: str, msg: List):
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers
        )
        await producer.start()

        try:
            await producer.send_and_wait(topic, kafka_serializer(msg))
        except Exception as e:
            print(f"Failed to publish topic:{e}")
            raise
        finally:
            await producer.stop()
    except Exception as err:
        print(f"Some Kafka error: {err}")
        raise


async def robot_turn(msg):
    finalists = encode_json(msg)
    is_my_turn = check_robot(finalists)

    if is_my_turn:
        print(mapping_place[len(finalists)].replace('name', my_name))

        if len(finalists) > 1:
            finalists.pop(0)
            await play_turn(finalists)


kafka_actions = {
    robotcorp_topic : robot_turn,
}


async def consume():
    consumer = AIOKafkaConsumer(
        robotcorp_topic,
        bootstrap_servers=kafka_bootstrap_servers,
    )

    try:
        await consumer.start()

    except Exception as e:
        print(e)
        return

    try:
        async for msg in consumer:
            await kafka_actions[msg.topic](msg)

    finally:
        await consumer.stop()


@app.get("/")
async def root():
    return {"Kafka": "Last Robot Standing"}


@app.get("/start")
async def start_game():
    robot_order = robot_random(robot_names)
    await send_one(topic=robotcorp_topic, msg=robot_order)

    return {"order": robot_order}