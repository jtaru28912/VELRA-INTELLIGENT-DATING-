import logging


def configure_logging(log_level: str) -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.handlers.clear()

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
