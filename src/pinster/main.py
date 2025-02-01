"""Main pinster module."""

import atexit
import importlib.resources
import json
import logging
import logging.config
import pathlib
from typing import Annotated

import spotipy
import typer

logger = logging.getLogger("pinster")

app = typer.Typer()


@app.command()
def main(
    spotify_client_id: Annotated[str, typer.Option(prompt=True)],
    spotify_client_secret: Annotated[str, typer.Option(prompt=True)],
) -> None:
    """Main command."""
    _setup_logging()

    sp = spotipy.Spotify(
        auth_manager=spotipy.SpotifyOAuth(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri="http://localhost:3000",
            scope="user-library-read, user-modify-playback-state",
        )
    )
    sp.start_playback(uris=["spotify:track:3qD07JJOPiyqjiQeg1wDK3"])  # type: ignore[reportUnknownMemberType]


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
