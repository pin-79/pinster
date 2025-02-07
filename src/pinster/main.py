"""Main pinster module."""

import logging
import logging.config
import random
from typing import Annotated

import rich
import rich.progress
import typer

import pinster.billboard
import pinster.logger
import pinster.spotify
import pinster.utils
import pinster.wikipedia

logger = logging.getLogger("pinster")

app = typer.Typer()


_SINGLE_GAME_SONG_QUEUE_LIMIT = 500
_BILLBOARD_SONGS_RATIO = 0.75
_PL_SONGS_RATIO = 0.2


@app.command()
def play(
    spotify_client_id: Annotated[str, typer.Option(prompt=True)],
    spotify_client_secret: Annotated[str, typer.Option(prompt=True)],
    spotify_redirect_uri: str = "http://localhost:3000",
    test: bool = False,  # noqa: FBT001, FBT002
) -> None:
    """Runs the game."""
    pinster.logger.setup_logging()

    songs = _get_billboard_songs(test=test)
    songs.extend(_get_pl_songs())
    random.shuffle(songs)

    spotify = pinster.spotify.Spotify(
        spotify_client_id, spotify_client_secret, spotify_redirect_uri
    )

    typer.confirm(
        f"Track queue ({len(songs)}) ready. Make sure your target device is playing something. Start game?",
        abort=True,
    )
    for song in songs[:_SINGLE_GAME_SONG_QUEUE_LIMIT]:
        current_track = spotify.get_most_popular_search_result(song.title, song.artist)
        if not current_track:
            continue

        spotify.play_track(current_track.id)
        with rich.progress.Progress(
            rich.progress.SpinnerColumn(),
            rich.progress.TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Playing track...", total=None)
            input()

        spotify.play_silence()
        input()

        rich.print(str(current_track))
        input()


def _get_billboard_songs(*, test: bool = False) -> list[pinster.utils.SimpleSong]:
    if test:
        songs = pinster.billboard.get_songs_with_total_weeks_not_above_threshold(
            pinster.billboard.DEFAULT_WEEKS_THRESHOLD
        )
    else:
        songs = pinster.billboard.get_songs_with_total_weeks_above_threshold(
            pinster.billboard.DEFAULT_WEEKS_THRESHOLD
        )
    songs = list(songs)
    random.shuffle(songs)
    limit = int(_SINGLE_GAME_SONG_QUEUE_LIMIT * _BILLBOARD_SONGS_RATIO)
    return songs[:limit]


def _get_pl_songs() -> list[pinster.utils.SimpleSong]:
    songs = list(pinster.wikipedia.get_all_time_polish_songs())
    random.shuffle(songs)
    limit = int(_SINGLE_GAME_SONG_QUEUE_LIMIT * _PL_SONGS_RATIO)
    return songs[:limit]


if __name__ == "__main__":
    app()
