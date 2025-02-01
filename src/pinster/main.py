"""Main pinster module."""

import atexit
import dataclasses
import importlib.resources
import json
import logging
import logging.config
import pathlib
from typing import Annotated, Any

import rich
import spotipy
import typer

logger = logging.getLogger("pinster")

app = typer.Typer()


SPOTIFY_MARKET = "PL"  # ISO 3166-1 alpha-2 country code
TRACK_FIELDS_TO_RETURN = "id,name,album(release_date),artists(name)"


@dataclasses.dataclass(frozen=True)
class GameTrack:
    """Track to be used in-game (not representative of the Spotify API response)."""

    id: str
    name: str
    artists: list[str]
    release_date: str


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
            scope="user-library-read, user-modify-playback-state",
        )
    )
    playlist_tracks = _get_all_playlist_tracks(sp, "21pb7wgr2qqVzKInStmoEm")
    tracks_to_use: list[GameTrack] = []
    for track in playlist_tracks:
        track_data = track["track"]
        tracks_to_use.append(
            GameTrack(
                track_data["id"],
                track_data["name"],
                [artist["name"] for artist in track_data["artists"]],
                track_data["album"]["release_date"],
            )
        )

    rich.print(tracks_to_use)


def _get_all_playlist_tracks(
    sp: spotipy.Spotify, playlist_id: str
) -> list[dict[str, Any]]:
    """Get all tracks from a playlist."""
    playlist_tracks: list[dict[str, Any]] = []
    offset = 0
    limit = 100
    total = 1
    while offset < total:
        response = sp.playlist_items(
            playlist_id,
            fields=f"limit,offset,total,items(track({TRACK_FIELDS_TO_RETURN}))",
            offset=offset,
            limit=limit,
            market=SPOTIFY_MARKET,
        )
        if response is None:
            break
        playlist_tracks.extend(response["items"])
        offset += limit
        total = response["total"]
    return playlist_tracks


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
