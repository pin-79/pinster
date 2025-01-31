"""Main pinster module."""

import atexit
import importlib.resources
import json
import logging
import logging.config
import pathlib

import rich
import typer

logger = logging.getLogger("pinster")

app = typer.Typer()


@app.command()
def main(name: str) -> None:
    """Main command."""
    _setup_logging()
    rich.print(f"Hello {name}!")


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
    app()
