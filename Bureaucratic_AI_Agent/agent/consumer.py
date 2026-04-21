import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from callback import send_callback
from config import settings
from core.handler import handle_task
from core.logging_config import setup_logging
from core.sentry_setup import init_sentry
from models import TaskMessage

setup_logging()
init_sentry()

logger = logging.getLogger(__name__)

DLX_NAME = "agent_tasks_dlx"
DLQ_NAME = "agent_tasks_dlq"
MAX_DELIVERIES = 5


async def on_message(message: AbstractIncomingMessage) -> None:
    # 1. Poison parse: garbage body or schema violation. No retry budget
    #    makes sense — reject without requeue so the broker dead-letters it.
    try:
        payload = json.loads(message.body)
        task = TaskMessage(**payload)
    except Exception as exc:
        logger.error(
            "reliability=poison_parse body=%r error=%s → DLQ",
            message.body[:200], exc,
        )
        await message.reject(requeue=False)
        return

    # 2. Normal processing. On exception, message.process requeues; the
    #    broker's x-delivery-limit (set in start_consumer) auto-dead-letters
    #    after MAX_DELIVERIES redeliveries.
    try:
        async with message.process(requeue=True):
            report = await handle_task(task)
            await send_callback(report)
    except Exception as exc:
        # message.process already nacked with requeue=True; log for visibility.
        logger.exception(
            "reliability=task_failed application=%s error=%s",
            payload.get("application_id"), exc,
        )


async def start_consumer() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Dead-letter exchange + queue (terminal drain for exhausted retries)
    dlx = await channel.declare_exchange(DLX_NAME, aio_pika.ExchangeType.DIRECT, durable=True)
    dlq = await channel.declare_queue(DLQ_NAME, durable=True)
    await dlq.bind(dlx, routing_key=settings.agent_queue)

    # Main queue: quorum type, broker-enforced delivery limit, auto-DLX on exceed.
    queue = await channel.declare_queue(
        settings.agent_queue,
        durable=True,
        arguments={
            "x-queue-type": "quorum",
            "x-delivery-limit": MAX_DELIVERIES,
            "x-dead-letter-exchange": DLX_NAME,
        },
    )
    await queue.consume(on_message)

    logger.info(
        "Agent consumer started. queue=%s (quorum) dlx=%s dlq=%s delivery_limit=%d",
        settings.agent_queue, DLX_NAME, DLQ_NAME, MAX_DELIVERIES,
    )
    await asyncio.Future()
