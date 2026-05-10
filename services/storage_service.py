# services/storage_service.py
# Единственная точка доступа к JSON-файлам приложения.
# Никто другой к resources/data/ не обращается напрямую.

from __future__ import annotations

import json
from pathlib import Path

from models.track import Track

_DATA_DIR = Path(__file__).parent.parent / "resources" / "data"

# ── Начальные данные (используются при первом запуске) ────────────────────

_SEED_LIBRARY: list[dict] = [
    {"title": "Runaway",             "artist": "AURORA",          "album": "Neon Vertigo",        "duration_sec": 227, "is_liked": True},
    {"title": "Thursday",            "artist": "Khruangbin",      "album": "Terracotta",           "duration_sec": 252, "is_liked": False},
    {"title": "Goodie Bag",          "artist": "Still Woozy",     "album": "Still Woozy",          "duration_sec": 209, "is_liked": False},
    {"title": "Let It Happen",       "artist": "Tame Impala",     "album": "Bloom Season",         "duration_sec": 467, "is_liked": True},
    {"title": "Kong",                "artist": "Bonobo",          "album": "Midnight Run",         "duration_sec": 306, "is_liked": False},
    {"title": "Yellow Is the Color", "artist": "Soccer Mommy",    "album": "Colour Theory",        "duration_sec": 298, "is_liked": False},
    {"title": "Solar Power",         "artist": "Lorde",           "album": "Solar Power",          "duration_sec": 163, "is_liked": False},
    {"title": "Coffee",              "artist": "beabadoobee",     "album": "Fake It Flowers",      "duration_sec": 178, "is_liked": False},
    {"title": "Heat Waves",          "artist": "Glass Animals",   "album": "Dreamland",            "duration_sec": 238, "is_liked": True},
    {"title": "Motion Sickness",     "artist": "Phoebe Bridgers", "album": "Stranger in the Alps", "duration_sec": 222, "is_liked": False},
]

_SEED_PLAYLISTS: dict[str, list[str]] = {
    "Liked Songs":      ["Runaway", "Let It Happen", "Heat Waves"],
    "Chill Vibes":      ["Runaway", "Thursday", "Goodie Bag", "Let It Happen"],
    "Discover Weekly":  ["Let It Happen", "Kong", "Yellow Is the Color", "Solar Power"],
    "Late Night Drive": ["Kong", "Yellow Is the Color", "Solar Power", "Coffee", "Heat Waves", "Motion Sickness"],
    "Workout Hits":     ["Runaway", "Goodie Bag", "Kong", "Solar Power", "Heat Waves"],
    "Focus Mode":       ["Thursday", "Let It Happen", "Yellow Is the Color", "Coffee", "Motion Sickness"],
    "Jazz After Midnight": ["Thursday", "Kong", "Motion Sickness"],
}


class StorageService:
    """Загрузка и сохранение данных библиотеки через JSON."""

    # ── Библиотека треков ─────────────────────────────────────────────────

    @staticmethod
    def load_library() -> list[Track]:
        path = _DATA_DIR / "library.json"
        if not path.exists():
            StorageService._seed_library()
        raw: list[dict] = json.loads(path.read_text(encoding="utf-8"))
        return [
            Track(
                title=item["title"],
                artist=item["artist"],
                album=item["album"],
                duration_sec=item["duration_sec"],
                is_liked=item.get("is_liked", False),
            )
            for item in raw
        ]

    @staticmethod
    def save_library(tracks: list[Track]) -> None:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        data = [
            {
                "title":        t.title,
                "artist":       t.artist,
                "album":        t.album,
                "duration_sec": t.duration_sec,
                "is_liked":     t.is_liked,
            }
            for t in tracks
        ]
        (_DATA_DIR / "library.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ── Плейлисты ─────────────────────────────────────────────────────────

    @staticmethod
    def load_playlists(library: list[Track]) -> dict[str, list[Track]]:
        """Возвращает словарь name → список треков (ссылки из library)."""
        path = _DATA_DIR / "playlists.json"
        if not path.exists():
            StorageService._seed_playlists()
        raw: dict[str, list[str]] = json.loads(path.read_text(encoding="utf-8"))
        title_map = {t.title: t for t in library}
        return {
            name: [title_map[title] for title in titles if title in title_map]
            for name, titles in raw.items()
        }

    # ── Сидирование (первый запуск) ───────────────────────────────────────

    @staticmethod
    def _seed_library() -> None:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        (_DATA_DIR / "library.json").write_text(
            json.dumps(_SEED_LIBRARY, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @staticmethod
    def _seed_playlists() -> None:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        (_DATA_DIR / "playlists.json").write_text(
            json.dumps(_SEED_PLAYLISTS, ensure_ascii=False, indent=2), encoding="utf-8"
        )
