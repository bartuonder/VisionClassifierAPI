import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()


RABBITMQ_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")


celery_app = Celery(
    "vision_tasks",
    broker=RABBITMQ_URL,
    include=["services.tasks"]
)


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Istanbul",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True
)