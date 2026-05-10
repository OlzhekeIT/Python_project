# services/library_service.py
# Чистая бизнес-логика библиотеки: поиск и сортировка треков.
# Не импортирует PyQt6 — тестируется без GUI.

from __future__ import annotations

from models.track import Track


class LibraryService:
    """Поиск и сортировка коллекции треков."""

    _SORT_KEYS: dict[str, object] = {
        "title":    lambda t: t.title.lower(),
        "artist":   lambda t: t.artist.lower(),
        "album":    lambda t: t.album.lower(),
        "duration": lambda t: t.duration_sec,
    }

    def __init__(self, tracks: list[Track]) -> None:
        self._tracks: list[Track] = list(tracks)

    @property
    def tracks(self) -> list[Track]:
        return list(self._tracks)

    # ── Поиск ────────────────────────────────────────────────────────────

    def search(self, query: str) -> list[Track]:
        """Линейный поиск по названию, артисту и альбому."""
        q = query.lower().strip()
        if not q:
            return list(self._tracks)
        return [
            t for t in self._tracks
            if q in t.title.lower()
            or q in t.artist.lower()
            or q in t.album.lower()
        ]

    # ── Сортировка ───────────────────────────────────────────────────────

    def sort(self, tracks: list[Track], key: str, reverse: bool = False) -> list[Track]:
        """Сортирует переданный список по ключу (не изменяет self._tracks)."""
        fn = self._SORT_KEYS.get(key, self._SORT_KEYS["title"])
        return sorted(tracks, key=fn, reverse=reverse)  # type: ignore[arg-type]

    # ── Обновление ───────────────────────────────────────────────────────

    def update_like(self, track: Track, value: bool) -> None:
        """Обновляет is_liked нужного трека в хранимом списке."""
        for t in self._tracks:
            if t.title == track.title and t.artist == track.artist:
                t.is_liked = value
                return
