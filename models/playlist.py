# models/playlist.py
# Модель плейлиста — dataclass, без UI-зависимостей.

from __future__ import annotations

from dataclasses import dataclass, field

from models.base_media import BaseMedia
from models.track import Track


@dataclass
class Playlist(BaseMedia):
    """Именованный список треков."""

    name:   str
    tracks: list[Track] = field(default_factory=list)
    color:  str = "#4A5AA7"

    # ── Реализация BaseMedia ──────────────────────────────────────────────

    @property
    def duration_str(self) -> str:
        total = sum(t.duration_sec for t in self.tracks)
        h, rem = divmod(total, 3600)
        m, s   = divmod(rem, 60)
        return f"{h}h {m}m" if h else f"{m}m {s}s"

    @property
    def display_name(self) -> str:
        return f"{self.name} ({len(self.tracks)} tracks)"

    def __len__(self) -> int:
        return len(self.tracks)
