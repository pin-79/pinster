"""Spotify interaction."""

from __future__ import annotations

import datetime as dt  # noqa: TC003

import platformdirs
import pydantic
import spotipy  # type: ignore[reportMissingTypeStubs]

_DEFAULT_SPOTIFY_MARKET = "PL"  # ISO 3166-1 alpha-2 country code
_REQUIRED_SCOPE = (
    "user-library-read, user-read-playback-state, user-modify-playback-state"
)
_SILENCE_PODCAST_EPISODE_ID = "0KgjitRy881dfSEmRhUZE5"


class Spotify:
    """Wrapper around Spotify's API."""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """Initializes the class.

        Args:
            client_id: Spotify Web API client ID.
            client_secret: Spotify Web API client secret.
            redirect_uri: Spotify Web API redirect URI.
        """
        cache_handler = spotipy.cache_handler.CacheFileHandler(
            cache_path=f"{platformdirs.user_cache_dir('pinster', appauthor=False, ensure_exists=True)}/.cache"
        )
        auth_manager = spotipy.SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=_REQUIRED_SCOPE,
            cache_handler=cache_handler,
        )
        self._api = spotipy.Spotify(auth_manager=auth_manager)

    def play_track(self, track_id: str) -> None:
        """Starts playback on the track with the given id on the active device."""
        self._api.start_playback(uris=[f"spotify:track:{track_id}"])  # type: ignore[reportUnknownMemberType]

    def play_silence(self) -> None:
        """Plays an all-silent podcast episode to simulate pausing without disabling the active device."""
        self._api.start_playback(  # type: ignore[reportUnknownMemberType]
            uris=[f"spotify:episode:{_SILENCE_PODCAST_EPISODE_ID}"]
        )

    def get_most_popular_search_result(self, title: str, artist: str) -> Track | None:
        """Get the most popular track for a given title - artist combination."""
        raw_search_result = self._api.search(  # type: ignore[reportUnknownMemberType]
            q=f"track:{title} artist:{artist}", market=_DEFAULT_SPOTIFY_MARKET
        )
        if not raw_search_result or not raw_search_result["tracks"]["items"]:
            return None
        all_tracks_from_search = [
            Track.model_validate(raw_track)
            for raw_track in raw_search_result["tracks"]["items"]
        ]
        return all_tracks_from_search[0]


class Track(pydantic.BaseModel):
    """Spotify track."""

    model_config = pydantic.ConfigDict(frozen=True)

    id: str
    """The Spotify ID for the track."""
    name: str
    """The name of the track."""
    artists: list[SimplifiedArtist]
    """The artists who performed the track."""
    album: Album
    """The album on which the track appears."""

    def __str__(self) -> str:
        """Returns the most important track info (name, artists and year)."""
        artist_names = [artist.name for artist in self.artists]
        return f"{self.name}\n{', '.join(artist_names)}\n{self.album.release_date.year}"


class SimplifiedArtist(pydantic.BaseModel):
    """Basic Spotify artist info."""

    model_config = pydantic.ConfigDict(frozen=True)

    id: str
    """The Spotify ID for the artist."""
    name: str
    """The name of the artist."""


class Album(pydantic.BaseModel):
    """Spotify album."""

    model_config = pydantic.ConfigDict(frozen=True)

    id: str
    """The Spotify ID for the album."""
    name: str
    """The name of the album. In case of an album takedown, the value may be an empty string."""
    release_date: dt.datetime
    """The date the album was first released."""
