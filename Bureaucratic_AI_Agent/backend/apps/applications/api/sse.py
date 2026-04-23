import asyncio
import logging

import redis.asyncio as aioredis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, StreamingHttpResponse
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)
User = get_user_model()


async def _authenticate(token: str):
    try:
        user_id = AccessToken(token)["user_id"]
        return await User.objects.aget(id=user_id, is_active=True)
    except (TokenError, User.DoesNotExist, Exception):
        return None


async def sse_view(request):
    """
    SSE endpoint for real-time application status updates.
    Auth: GET /api/v1/sse/?token=<jwt_access_token>
    """
    user = await _authenticate(request.GET.get("token", ""))
    if user is None:
        return HttpResponse("Unauthorized", status=401)

    async def event_stream():
        r = aioredis.Redis.from_url(settings.REDIS_URL)
        pubsub = r.pubsub()
        await pubsub.subscribe(f"sse:user:{user.id}")
        logger.info("SSE connected: user=%s", user.id)

        try:
            yield "event: connected\ndata: {}\n\n"
            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=30.0)
                if msg and msg["type"] == "message":
                    data = msg["data"].decode() if isinstance(msg["data"], bytes) else msg["data"]
                    yield f"event: application_updated\ndata: {data}\n\n"
                else:
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            logger.info("SSE disconnected: user=%s", user.id)
        finally:
            await pubsub.unsubscribe(f"sse:user:{user.id}")
            await r.aclose()

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
