"""Logging configuration."""

import atexit
import importlib.resources
import json
import logging
import logging.config

import platformdirs


def setup_logging() -> None:
    """Sets up the root logger config."""
    with importlib.resources.open_text("pinster", "configs/logging.json") as f:  # type: ignore[reportArgumentType]
        config = json.load(f)

    # Ensure the logs directory exists
    config["handlers"]["file"]["filename"] = (
        f"{platformdirs.user_log_dir('pinster', appauthor=False, ensure_exists=True)}/pinster.log"
    )

    logging.config.dictConfig(config)

    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()  # type: ignore[reportUnknownMemberType]
        atexit.register(queue_handler.listener.stop)  # type: ignore[reportUnknownMemberType]
