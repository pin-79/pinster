"""Wikipedia interaction."""

import pandas as pd

import pinster.utils

_ALL_TIME_POLISH_SONGS_TABLES_URL = (
    "https://pl.wikipedia.org/wiki/Lista_piosenek_Polskiego_Topu_Wszech_Czas%C3%B3w"
)


def get_all_time_polish_songs() -> set[pinster.utils.SimpleSong]:
    """Gets simple song data for all songs from Polski Top Wszech Czasów."""
    songs: set[pinster.utils.SimpleSong] = set()
    for table in pd.read_html(_ALL_TIME_POLISH_SONGS_TABLES_URL):
        for _, row in table.iterrows():
            songs.add(pinster.utils.SimpleSong(row["Utwór"], row["Wykonawca"]))
    return songs
