"""Main pinster module."""

import logging
import logging.config
import random
from typing import Annotated, Any

import platformdirs
import rich
import rich.progress
import spotipy  # type: ignore[reportMissingTypeStubs]
import spotipy.cache_handler  # type: ignore[reportMissingTypeStubs]
import typer

import pinster.logger

logger = logging.getLogger("pinster")

app = typer.Typer()


GAME_LIMIT = 100
SILENCE_PODCAST_EPISODE_ID = "0KgjitRy881dfSEmRhUZE5"
SPOTIFY_MARKET = "PL"  # ISO 3166-1 alpha-2 country code


@app.callback()
def app_callback() -> None:
    """Runs setup before commands."""
    pinster.logger.setup_logging()


@app.command()
def play(
    spotify_client_id: Annotated[str, typer.Option(prompt=True)],
    spotify_client_secret: Annotated[str, typer.Option(prompt=True)],
    spotify_redirect_uri: str | None = None,
) -> None:
    """Runs the game."""
    sp = spotipy.Spotify(
        auth_manager=spotipy.SpotifyOAuth(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri=spotify_redirect_uri or "http://localhost:3000",
            scope="user-library-read, user-read-playback-state, user-modify-playback-state",
            cache_handler=spotipy.cache_handler.CacheFileHandler(
                cache_path=f"{platformdirs.user_cache_dir(app.info.name, appauthor=False, ensure_exists=True)}/.cache"
            ),
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


if __name__ == "__main__":
    app()
