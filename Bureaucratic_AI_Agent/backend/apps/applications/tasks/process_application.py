import json
import logging

from celery import shared_task
from django.conf import settings
from kombu import Connection, Queue

from apps.applications.constants import ApplicationStatus

logger = logging.getLogger(__name__)


def _publish_to_agent(payload: dict) -> None:
    """Publish task payload to agent_tasks queue via plain AMQP (kombu)"""
    agent_queue = Queue("agent_tasks", durable=True)
    with Connection(settings.CELERY_BROKER_URL) as conn:
        with conn.Producer() as producer:
            producer.publish(
                json.dumps(payload),
                exchange="",
                routing_key="agent_tasks",
                declare=[agent_queue],
                content_type="application/json",
            )

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_application(self, application_id: str) -> None:
    """
    Transition application to PROCESSING
    and publish task to the AI agent queue
    """
    from apps.applications.models import Application

    try:
        application = Application.objects.prefetch_related("documents").get(id=application_id)
    except Application.DoesNotExist:
        logger.error("process_application: Application %s not found", application_id)
        return

    application.status = ApplicationStatus.PROCESSING
    application.save(update_fields=["status", "updated_at"])

    document = application.documents.filter(is_active=True).first()

    payload = {
        "application_id": str(application.id),
        "procedure": application.procedure,
        "form_data": application.form_data,
        "document": {
            "file_name": document.file_name,
            "file_url": document.file.url,
            "file_format": document.file_format,
            "file_size": document.file_size,
        } if document else None,
    }

    _publish_to_agent(payload)

    logger.info(
        "process_application: Application %s is PROCESSING — task published to agent queue",
        application_id,
    )
