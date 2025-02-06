"""Fetching and manipulating Billboard Hot 100 charts."""

from __future__ import annotations

import dataclasses
import datetime as dt  # noqa: TC003

import httpx
import pydantic

DEFAULT_MIN_WEEKS_THRESHOLD = 25  # this returns just shy of 2000 songs
_ALL_CHARTS_URL = (
    "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/all.json"
)


def get_songs_with_total_weeks_in_range(
    min_threshold: int, max_threshold: int | None = None
) -> set[SimpleSong]:
    """Gets songs which have been on the Hot 100 between min (incl.) and max (excl.) threshold no. of weeks."""
    response = httpx.get(_ALL_CHARTS_URL)
    songs: set[SimpleSong] = set()
    for raw_chart in reversed(response.json()):
        chart = Chart.model_validate(raw_chart)
        for song in chart.data:
            if max_threshold is None:
                if song.weeks_on_chart >= min_threshold:
                    songs.add(SimpleSong(song.song, song.artist))
                continue
            if max_threshold > song.weeks_on_chart >= min_threshold:
                songs.add(SimpleSong(song.song, song.artist))
    return songs


class Song(pydantic.BaseModel):
    """A song in the context of a Billboard Hot 100 chart."""

    model_config = pydantic.ConfigDict(frozen=True)

    song: str
    """The song's title."""
    artist: str
    """The song's artist."""
    this_week: int
    """The song's current chart position."""
    last_week: int | None
    """The songs' chart position during the previous week."""
    peak_position: int
    """The song's peak chart position during any week."""
    weeks_on_chart: int
    """The number of weeks that the song has been on the chart."""


class Chart(pydantic.BaseModel):
    """Billboard Hot 100 chart for a single week.

    Reference: https://github.com/mhollingshead/billboard-hot-100?tab=readme-ov-file#chart-object
    """

    model_config = pydantic.ConfigDict(frozen=True)

    date: dt.datetime
    """The chart's release date (formatted YYYY-MM-DD)."""
    data: list[Song]
    """All 100 songs on the chart."""


@dataclasses.dataclass(frozen=True)
class SimpleSong:
    """Bare-bones data about a song."""

    title: str
    artist: str
