import logging

from config import settings

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """
    Initialise Sentry SDK. No-op unless production=True and sentry_dsn is set.
    Safe to call multiple times.
    """
    if not settings.production:
        logger.debug("Sentry disabled (non-production environment)")
        return
    if not settings.sentry_dsn:
        logger.warning("production=True but SENTRY_DSN is not set — Sentry disabled")
        return

    import sentry_sdk
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment="production",
        traces_sample_rate=0.0,  # errors only, no performance tracing
    )
    logger.info("Sentry initialised")
