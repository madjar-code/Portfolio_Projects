import json
import logging
import redis
from django.conf import settings

logger = logging.getLogger(__name__)


def publish_sse_event(user_id: str, application_id: str, status: str, application_number: str) -> None:
    """Publish SSE event to user's Redis channel. Errors are logged, never raised."""
    try:
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.publish(
            f"sse:user:{user_id}",
            json.dumps({
                "application_id": str(application_id),
                "status": status,
                "application_number": application_number,
            })
        )
        r.close()
        logger.info("SSE event published: user=%s status=%s", user_id, status)
    except Exception as exc:
        logger.error("Failed to publish SSE event: %s", exc)
