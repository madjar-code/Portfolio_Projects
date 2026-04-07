import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from callback import send_callback
from config import settings
from core.handler import handle_task
from models import TaskMessage

logger = logging.getLogger(__name__)


async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process(requeue=True):
        try:
            payload = json.loads(message.body)
            task = TaskMessage(**payload)
        except Exception as exc:
            logger.error("Failed to parse task messages: %s | body: %s", exc, message.body)
            return

        try:
            report = await handle_task(task)
            await send_callback(report)
        except Exception as exc:
            logger.exception(
                "Task failed for application %s: %s", payload.get("application_id"), exc
            )
            raise  # triggers requeue


async def start_consumer() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    queue = await channel.declare_queue(settings.agent_queue, durable=True)
    await queue.consume(on_message)

    logger.info("Agent consumer started. Listening on queue: %s", settings.agent_queue)

    # Keep running
    await asyncio.Future()
