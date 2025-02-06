"""Fetching and manipulating Billboard Hot 100 charts."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import httpx
import pydantic

if TYPE_CHECKING:
    import datetime as dt

_ALL_CHARTS_URL = (
    "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/all.json"
)


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


def get_songs_with_most_total_weeks_on_the_chart(threshold: int) -> set[SimpleSong]:
    """Gets songs which have been on the Hot 100 for at least the threshold no. of weeks."""
    response = httpx.get(_ALL_CHARTS_URL)
    songs: set[SimpleSong] = set()
    for raw_chart in reversed(response.json()):
        chart = Chart.model_validate(raw_chart)
        for song in chart.data:
            if song.weeks_on_chart >= threshold:
                songs.add(SimpleSong(song.song, song.artist))
    return songs
