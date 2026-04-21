import json
import logging

from celery import Task, shared_task
from django.conf import settings
from kombu import Connection, Queue
from kombu.exceptions import OperationalError as KombuOperationalError

from apps.applications.constants import ApplicationStatus

logger = logging.getLogger(__name__)


AGENT_QUEUE_ARGS = {
    "x-queue-type": "quorum",
    "x-delivery-limit": 5,
    "x-dead-letter-exchange": "agent_tasks_dlx",
}


def _publish_to_agent(payload: dict) -> None:
    """Publish task payload to agent_tasks queue via plain AMQP (kombu)."""
    agent_queue = Queue("agent_tasks", durable=True, queue_arguments=AGENT_QUEUE_ARGS)
    with Connection(settings.CELERY_BROKER_URL) as conn:
        with conn.Producer() as producer:
            producer.publish(
                json.dumps(payload),
                exchange="",
                routing_key="agent_tasks",
                declare=[agent_queue],
                content_type="application/json",
            )


class ProcessApplicationTask(Task):
    """Base class providing on_failure hook.

    on_failure fires once max_retries is exhausted OR the task raises a
    non-retryable exception. We use it to transition the application to
    FAILED so the user doesn't see a perpetual SUBMITTED state.
    """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        application_id = args[0] if args else kwargs.get("application_id")
        if not application_id:
            logger.error("publish_exhausted: task_id=%s no application_id in args", task_id)
            return
        try:
            from apps.applications.models import Application
            app = Application.objects.get(id=application_id)
            app.status = ApplicationStatus.FAILED
            app.save(update_fields=["status", "updated_at"])
            logger.error(
                "reliability=publish_exhausted application=%s task_id=%s error=%s",
                application_id, task_id, exc,
            )
        except Exception as save_exc:
            logger.exception(
                "on_failure: cannot mark %s FAILED: %s", application_id, save_exc,
            )


@shared_task(
    base=ProcessApplicationTask,
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=False,
)
def process_application(self, application_id: str) -> None:
    """Transition Application to PROCESSING and publish task to the AI agent queue.

    Retries up to 3 times on broker-level OperationalError with exponential
    backoff (1s, 2s, 4s). After exhaustion, on_failure marks the app FAILED.
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

    try:
        _publish_to_agent(payload)
    except (KombuOperationalError, ConnectionError) as exc:
        logger.warning(
            "reliability=publish_retry application=%s attempt=%d/%d error=%s",
            application_id, self.request.retries + 1, self.max_retries + 1, exc,
        )
        raise self.retry(exc=exc)

    logger.info(
        "process_application: application=%s is PROCESSING — task published to agent queue",
        application_id,
    )
