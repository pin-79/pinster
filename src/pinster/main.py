"""Main pinster module."""

import atexit
import importlib.resources
import json
import logging
import logging.config
import pathlib
import random
from typing import Annotated, Any

import rich
import rich.progress
import spotipy
import typer

logger = logging.getLogger("pinster")

app = typer.Typer()


GAME_LIMIT = 100
SILENCE_PODCAST_EPISODE_ID = "0KgjitRy881dfSEmRhUZE5"
SPOTIFY_MARKET = "PL"  # ISO 3166-1 alpha-2 country code


@app.command()
def main(
    spotify_client_id: Annotated[str, typer.Option(prompt=True)],
    spotify_client_secret: Annotated[str, typer.Option(prompt=True)],
    spotify_redirect_uri: str | None = None,
) -> None:
    """Main command."""
    _setup_logging()
    sp = spotipy.Spotify(
        auth_manager=spotipy.SpotifyOAuth(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri=spotify_redirect_uri or "http://localhost:3000",
            scope="user-library-read, user-read-playback-state, user-modify-playback-state",
        )
    )

    liked_songs = _get_all_liked_songs_from_api(sp)
    random.shuffle(liked_songs)
    typer.confirm(
        "Track queue ready. Make sure your target device is playing something. Start game?",
        abort=True,
    )

    for song in liked_songs[:GAME_LIMIT]:
        song_data = song["track"]
        sp.start_playback(uris=[f"spotify:track:{song_data['id']}"])  # type: ignore[reportUnknownMemberType]
        with rich.progress.Progress(
            rich.progress.SpinnerColumn(),
            rich.progress.TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Playing track...", total=None)
            input()
        sp.start_playback(uris=[f"spotify:episode:{SILENCE_PODCAST_EPISODE_ID}"])  # type: ignore[reportUnknownMemberType]
        input()

        artists = [artist["name"] for artist in song_data["artists"]]
        name = song_data["name"]
        release_date = song_data["album"]["release_date"]
        rich.print(f"{name}\n{', '.join(artists)}\n{release_date[:4]}")
        input()


def _get_all_liked_songs_from_api(sp: spotipy.Spotify) -> list[dict[str, Any]]:
    """Get all tracks from a playlist."""
    liked_songs: list[dict[str, Any]] = []
    offset = 0
    limit = 50
    total = 1
    while offset < total:
        response = sp.current_user_saved_tracks(  # type: ignore[reportUnknownMemberType]
            limit=limit, offset=offset, market=SPOTIFY_MARKET
        )
        if response is None:
            break
        liked_songs.extend(response["items"])
        offset += limit
        total = response["total"]
    return liked_songs


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
