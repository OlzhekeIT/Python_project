# models/track.py
# Модель данных одного трека — чистый dataclass, без UI-зависимостей.

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from models.base_media import BaseMedia


@dataclass
class Track(BaseMedia):
    """Представляет один аудио-трек в библиотеке."""

    title:        str
    artist:       str
    album:        str
    duration_sec: int
    file_path:    Path = field(default_factory=lambda: Path(""))
    cover_path:   Path = field(default_factory=lambda: Path(""))
    is_liked:     bool = False

    # ── Реализация BaseMedia ──────────────────────────────────────────────

    @property
    def duration_str(self) -> str:
        """Возвращает строку вида «3:47»."""
        m, s = divmod(self.duration_sec, 60)
        return f"{m}:{s:02d}"

    @property
    def display_name(self) -> str:
        return f"{self.artist} — {self.title}"

    def __str__(self) -> str:
        return f"Track({self.title!r}, {self.artist!r}, {self.duration_str})"
