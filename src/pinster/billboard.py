"""Fetching and manipulating Billboard Hot 100 charts."""

from __future__ import annotations

import datetime as dt  # noqa: TC003

import httpx
import pydantic

import pinster.utils

DEFAULT_WEEKS_THRESHOLD = 26
_ALL_CHARTS_URL = (
    "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/all.json"
)


def get_songs_with_total_weeks_above_threshold(
    threshold: int,
) -> set[pinster.utils.SimpleSong]:
    """Gets songs which have been on the Hot 100 above the threshold number of weeks."""
    response = httpx.get(_ALL_CHARTS_URL)
    songs: set[pinster.utils.SimpleSong] = set()
    for raw_chart in response.json():
        chart = Chart.model_validate(raw_chart)
        for song in chart.data:
            if song.weeks_on_chart >= threshold:
                songs.add(pinster.utils.SimpleSong(song.song, song.artist))
                continue
    return songs


def get_songs_with_total_weeks_not_above_threshold(
    threshold: int,
) -> set[pinster.utils.SimpleSong]:
    """Gets songs which have never been on the Hot 100 above the threshold number of weeks."""
    response = httpx.get(_ALL_CHARTS_URL)
    songs_above_threshold: set[pinster.utils.SimpleSong] = set()
    songs_not_above_threshold: set[pinster.utils.SimpleSong] = set()
    for raw_chart in response.json():
        chart = Chart.model_validate(raw_chart)
        for song in chart.data:
            simple_song = pinster.utils.SimpleSong(song.song, song.artist)
            if song.weeks_on_chart >= threshold:
                songs_above_threshold.add(simple_song)
                continue
            songs_not_above_threshold.add(simple_song)
    return songs_not_above_threshold - songs_above_threshold


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
