"""Logging setup."""

import atexit
import datetime as dt
import importlib.resources
import json
import logging
import logging.config
import logging.handlers
import pathlib
from typing import override

_LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


def setup_logging() -> None:
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


class JSONFormatter(logging.Formatter):
    """Custom JSON log formatter."""

    def __init__(self, *, fmt_keys: dict[str, str] | None = None):
        """Initializes the formatter.

        Args:
            fmt_keys: Log record attributes.
        """
        super().__init__()
        self.fmt_keys = fmt_keys or {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord) -> dict[str, str]:
        fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.UTC
            ).isoformat(),
        }
        if record.exc_info is not None:
            fields["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info is not None:
            fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(fields)

        extras = {
            key: val
            for key, val in record.__dict__.items()
            if key not in _LOG_RECORD_BUILTIN_ATTRS
        }
        message.update(extras)

        return message
