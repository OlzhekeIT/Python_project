# views/central_widget.py
# Центральная область: сетка альбомов + трекліст.
# Данные поступают снаружи через set_tracks() — никакого прямого доступа к хранилищу.

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy,
)

from models.track import Track


class AlbumCard(QWidget):
    """Карточка альбома в сетке."""

    clicked = pyqtSignal(int)   # индекс первого трека альбома

    def __init__(self, title: str, artist: str, color: str,
                 track_idx: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("albumCard")
        self._track_idx = track_idx
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(8)

        art = QFrame()
        art.setObjectName("albumArt")
        art.setFixedHeight(148)
        # Цвет задаётся из данных альбома — допустимое исключение из правила QSS-only
        art.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {color}, stop:1 #1A1A2E); border-radius: 12px;"
        )

        title_lbl = QLabel(title)
        title_lbl.setObjectName("albumTitle")
        title_lbl.setWordWrap(True)

        artist_lbl = QLabel(artist)
        artist_lbl.setObjectName("albumArtist")

        v.addWidget(art)
        v.addWidget(title_lbl)
        v.addWidget(artist_lbl)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        super().mousePressEvent(event)
        self.clicked.emit(self._track_idx)


class TrackRow(QWidget):
    """Одна строка трека в треклисте."""

    clicked = pyqtSignal(int)   # индекс в переданном списке

    def __init__(self, index: int, track: Track,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("trackRow")
        self._index = index
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        h = QHBoxLayout(self)
        h.setContentsMargins(8, 6, 8, 6)
        h.setSpacing(12)

        num = QLabel(str(index + 1))
        num.setObjectName("trackNum")
        num.setFixedWidth(24)
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        thumb = QFrame()
        thumb.setObjectName("trackThumb")
        thumb.setFixedSize(38, 38)

        info = QVBoxLayout()
        info.setSpacing(1)
        info.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel(track.title)
        title_lbl.setObjectName("trackTitle")

        artist_lbl = QLabel(track.artist)
        artist_lbl.setObjectName("trackArtist")

        info.addWidget(title_lbl)
        info.addWidget(artist_lbl)

        album_lbl = QLabel(track.album)
        album_lbl.setObjectName("trackAlbum")
        album_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        dur_lbl = QLabel(track.duration_str)
        dur_lbl.setObjectName("trackDuration")
        dur_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        h.addWidget(num)
        h.addWidget(thumb)
        h.addLayout(info, stretch=2)
        h.addWidget(album_lbl, stretch=2)
        h.addWidget(dur_lbl)

    def set_playing(self, playing: bool) -> None:
        self.setProperty("playing", playing)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        super().mousePressEvent(event)
        self.clicked.emit(self._index)


class CentralWidget(QWidget):
    """
    Центральная область (главный экран).
    Сигнал track_selected(index) — пользователь кликнул трек или альбом.
    Данные задаются извне через set_tracks().
    """

    track_selected = pyqtSignal(int)

    _ALBUMS = [
        ("Neon Vertigo",  "AURORA",       "#4A5AA7", 0),
        ("Terracotta",    "Khruangbin",   "#C05A3A", 1),
        ("Still Woozy",   "Still Woozy",  "#3A8FA0", 2),
        ("Bloom Season",  "Tame Impala",  "#3DAA6E", 3),
        ("Midnight Run",  "Bonobo",       "#1A2A4A", 4),
        ("Colour Theory", "Soccer Mommy", "#8A5EA7", 5),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("centralWidget")
        self._track_rows: list[TrackRow] = []

        scroll = QScrollArea()
        scroll.setObjectName("centralScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        inner.setObjectName("centralInner")
        v = QVBoxLayout(inner)
        v.setContentsMargins(0, 0, 0, 24)
        v.setSpacing(0)

        v.addWidget(self._build_header())
        v.addWidget(self._build_albums())
        v.addWidget(self._build_tracklist())

        scroll.setWidget(inner)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(scroll)

    # ── Секции ───────────────────────────────────────────────────────────

    def _build_header(self) -> QWidget:
        w = QWidget()
        w.setObjectName("centralHeader")
        h = QHBoxLayout(w)
        h.setContentsMargins(28, 18, 28, 14)
        h.setSpacing(0)

        title = QLabel("Good evening ✦")
        title.setObjectName("centralTitle")

        search_btn = QPushButton("⌕  Search songs, artists…")
        search_btn.setObjectName("searchButton")

        h.addWidget(title)
        h.addStretch()
        h.addWidget(search_btn)
        return w

    def _build_albums(self) -> QWidget:
        w = QWidget()
        w.setObjectName("albumsSection")
        v = QVBoxLayout(w)
        v.setContentsMargins(28, 0, 28, 0)
        v.setSpacing(14)

        header = QHBoxLayout()
        lbl = QLabel("Featured Albums")
        lbl.setObjectName("sectionTitle")
        see_all = QPushButton("See all →")
        see_all.setObjectName("seeAllButton")
        header.addWidget(lbl)
        header.addStretch()
        header.addWidget(see_all)
        v.addLayout(header)

        grid = QGridLayout()
        grid.setSpacing(16)
        for i, (title, artist, color, idx) in enumerate(self._ALBUMS):
            card = AlbumCard(title, artist, color, idx)
            card.clicked.connect(self.track_selected)
            grid.addWidget(card, 0, i)
        v.addLayout(grid)
        return w

    def _build_tracklist(self) -> QWidget:
        w = QWidget()
        w.setObjectName("tracklistSection")
        v = QVBoxLayout(w)
        v.setContentsMargins(28, 16, 28, 0)
        v.setSpacing(0)

        header = QHBoxLayout()
        lbl = QLabel("Popular Tracks")
        lbl.setObjectName("sectionTitle")
        see_all = QPushButton("See all →")
        see_all.setObjectName("seeAllButton")
        header.addWidget(lbl)
        header.addStretch()
        header.addWidget(see_all)
        v.addLayout(header)

        col_header = QWidget()
        col_header.setObjectName("tracklistHeader")
        ch = QHBoxLayout(col_header)
        ch.setContentsMargins(8, 6, 8, 6)
        ch.setSpacing(12)
        for text, stretch, align in [
            ("#",       0, Qt.AlignmentFlag.AlignCenter),
            ("Title",   2, Qt.AlignmentFlag.AlignLeft),
            ("Album",   2, Qt.AlignmentFlag.AlignLeft),
            ("Duration",0, Qt.AlignmentFlag.AlignRight),
        ]:
            lbl2 = QLabel(text)
            lbl2.setObjectName("colHeader")
            lbl2.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
            if text == "#":
                lbl2.setFixedWidth(24)
                ch.addWidget(lbl2)
            elif stretch:
                ch.addWidget(lbl2, stretch=stretch)
            else:
                ch.addWidget(lbl2)
        v.addWidget(col_header)

        # Контейнер строк — пополняется через set_tracks()
        self._rows_widget = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_widget)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(0)
        v.addWidget(self._rows_widget)
        v.addStretch()

        return w

    # ── Публичный API ─────────────────────────────────────────────────────

    def set_tracks(self, tracks: list[Track]) -> None:
        """Заменяет список треков в секции Popular Tracks."""
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._track_rows = []
        for i, track in enumerate(tracks):
            row = TrackRow(i, track)
            row.clicked.connect(self.track_selected)
            self._rows_layout.addWidget(row)
            self._track_rows.append(row)

    def highlight_track(self, index: int) -> None:
        """Подсвечивает активный трек в списке."""
        for i, row in enumerate(self._track_rows):
            row.set_playing(i == index)