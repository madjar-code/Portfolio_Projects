import logging
import logging.handlers
import pathlib


_configured = False


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure root logger with:
    - StreamHandler (console)
    - RotatingFileHandler (agent/logs/agent.log, 10 MB × 5 files)

    Safe to call multiple times — handlers are only added once.
    """
    global _configured
    if _configured:
        return

    root = logging.getLogger()
    fmt = logging.Formatter("%(levelname)s:%(name)s:%(message)s")

    console = logging.StreamHandler()
    console.setFormatter(fmt)

    log_dir = pathlib.Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "agent.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)

    root.setLevel(level)
    root.addHandler(console)
    root.addHandler(file_handler)
    _configured = True
