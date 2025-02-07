"""Common utils."""

import dataclasses


@dataclasses.dataclass(frozen=True)
class SimpleSong:
    """Bare-bones data about a song."""

    title: str
    artist: str
