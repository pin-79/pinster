"""Main pinster module."""

import atexit
import importlib.resources
import json
import logging
import logging.config
import pathlib

logger = logging.getLogger("pinster")


def main() -> None:
    """Main entry point."""
    _setup_logging()
    logger.debug("debug msg", extra={"attr": "HELLO"})
    logger.info("debug msg")
    logger.warning("warning msg")
    logger.error("error msg")
    logger.critical("critical msg")
    try:
        _ = 1 / 0
    except ZeroDivisionError:
        logger.exception("exception msg")


def _setup_logging() -> None:
    """Sets up the root logger config."""
    with importlib.resources.open_text("pinster", "configs/logging.json") as f:
        config = json.load(f)

    # Ensure the logs directory exists
    log_file = pathlib.Path(config["handlers"]["file"]["filename"])
    log_file.parent.mkdir(exist_ok=True)

    logging.config.dictConfig(config)

    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()  # type: ignore[reportUnknownMemberType]
        atexit.register(queue_handler.listener.stop)  # type: ignore[reportUnknownMemberType]


if __name__ == "__main__":
    main()
