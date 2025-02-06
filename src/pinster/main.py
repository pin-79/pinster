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

logger = logging.getLogger("pinster")

app = typer.Typer()


_SINGLE_GAME_SONG_QUEUE_LIMIT = 250


@app.command()
def play(
    spotify_client_id: Annotated[str, typer.Option(prompt=True)],
    spotify_client_secret: Annotated[str, typer.Option(prompt=True)],
    spotify_redirect_uri: str = "http://localhost:3000",
    test: bool = False,  # noqa: FBT001, FBT002
) -> None:
    """Runs the game."""
    pinster.logger.setup_logging()

    if test:
        songs = pinster.billboard.get_songs_with_total_weeks_in_range(10, 15)
    else:
        songs = pinster.billboard.get_songs_with_total_weeks_in_range(
            pinster.billboard.DEFAULT_MIN_WEEKS_THRESHOLD
        )
    songs = list(songs)
    random.shuffle(songs)
    spotify = pinster.spotify.Spotify(
        spotify_client_id, spotify_client_secret, spotify_redirect_uri
    )

    typer.confirm(
        "Track queue ready. Make sure your target device is playing something. Start game?",
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


if __name__ == "__main__":
    app()
