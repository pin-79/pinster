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

import pinster.billboard
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
    test: bool = False,  # noqa: FBT001, FBT002
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

    if test:
        songs = pinster.billboard.get_songs_with_total_weeks_in_range(10, 15)
    else:
        songs = pinster.billboard.get_songs_with_total_weeks_in_range(
            pinster.billboard.DEFAULT_MIN_WEEKS_THRESHOLD
        )

    songs = list(songs)
    random.shuffle(songs)
    typer.confirm(
        "Track queue ready. Make sure your target device is playing something. Start game?",
        abort=True,
    )

    for song in songs[:GAME_LIMIT]:
        song_search_result = _get_most_popular_search_result_for_song(sp, song)
        if not song_search_result:
            continue

        sp.start_playback(uris=[f"spotify:track:{song_search_result['id']}"])  # type: ignore[reportUnknownMemberType]
        with rich.progress.Progress(
            rich.progress.SpinnerColumn(),
            rich.progress.TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Playing track...", total=None)
            input()
        sp.start_playback(uris=[f"spotify:episode:{SILENCE_PODCAST_EPISODE_ID}"])  # type: ignore[reportUnknownMemberType]
        input()

        artists = [artist["name"] for artist in song_search_result["artists"]]
        name = song_search_result["name"]
        release_date = song_search_result["album"]["release_date"]
        rich.print(f"{name}\n{', '.join(artists)}\n{release_date[:4]}")
        input()


def _get_most_popular_search_result_for_song(
    sp: spotipy.Spotify, song: pinster.billboard.SimpleSong
) -> dict[str, Any] | None:
    search_result = sp.search(  # type: ignore[reportUnknownMemberType]
        q=f"track:'{song.title}' artist:'{song.artist}'", market=SPOTIFY_MARKET
    )
    if not search_result or not search_result.get("tracks", {}).get("items", []):
        return None
    return sorted(
        search_result["tracks"]["items"],
        key=lambda track: track["popularity"],
        reverse=True,
    )[0]


if __name__ == "__main__":
    app()
