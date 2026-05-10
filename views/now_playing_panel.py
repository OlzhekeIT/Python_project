# views/now_playing_panel.py
# Правая панель «Now Playing»: обложка, инфо, прогресс, очередь.

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy,
)

from models.track import Track


class QueueItem(QWidget):
    """Строка в списке очереди."""

    clicked = pyqtSignal(int)

    def __init__(self, index: int, track: Track,
                 is_next: bool = False,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._index = index
        self.setObjectName("queueItemNext" if is_next else "queueItem")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        h = QHBoxLayout(self)
        h.setContentsMargins(8, 6, 8, 6)
        h.setSpacing(10)

        thumb = QFrame()
        thumb.setObjectName("queueThumb")
        thumb.setFixedSize(34, 34)

        info = QVBoxLayout()
        info.setSpacing(1)
        info.setContentsMargins(0, 0, 0, 0)

        title = QLabel(track.title)
        title.setObjectName("queueTrackTitle")

        artist = QLabel(track.artist)
        artist.setObjectName("queueTrackArtist")

        info.addWidget(title)
        info.addWidget(artist)

        h.addWidget(thumb)
        h.addLayout(info)
        h.addStretch()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        super().mousePressEvent(event)
        self.clicked.emit(self._index)


class NowPlayingPanel(QWidget):
    """
    Правая панель целиком.
    Сигналы:
      like_toggled()          — пользователь нажал кнопку лайка
      queue_track_clicked(i)  — выбран трек из очереди
    """

    like_toggled        = pyqtSignal()
    queue_track_clicked = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("nowPlayingPanel")
        self.setFixedWidth(300)

        self._liked = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_tabs())
        root.addWidget(self._build_art())
        root.addWidget(self._build_info())
        root.addWidget(self._build_mini_seek())
        root.addWidget(self._build_queue(), stretch=1)

    # ── Секции ───────────────────────────────────────────────────────────

    def _build_tabs(self) -> QWidget:
        w = QWidget()
        w.setObjectName("rpTabs")
        h = QHBoxLayout(w)
        h.setContentsMargins(16, 16, 16, 0)
        h.setSpacing(4)
        h.addStretch()

        for text, active in [("Now Playing", True), ("Queue", False)]:
            btn = QPushButton(text)
            btn.setObjectName("rpTabActive" if active else "rpTab")
            btn.setCheckable(True)
            btn.setChecked(active)
            h.addWidget(btn)

        return w

    def _build_art(self) -> QWidget:
        w = QWidget()
        w.setObjectName("rpArtContainer")
        v = QVBoxLayout(w)
        v.setContentsMargins(20, 16, 20, 0)

        self._art_frame = QFrame()
        self._art_frame.setObjectName("rpArt")
        self._art_frame.setMinimumHeight(220)
        self._art_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        v.addWidget(self._art_frame)
        return w

    def _build_info(self) -> QWidget:
        w = QWidget()
        w.setObjectName("rpInfo")
        v = QVBoxLayout(w)
        v.setContentsMargins(20, 14, 20, 0)
        v.setSpacing(2)

        self._song_lbl = QLabel("Runaway")
        self._song_lbl.setObjectName("rpSongTitle")

        self._artist_lbl = QLabel("AURORA · Neon Vertigo")
        self._artist_lbl.setObjectName("rpArtistLabel")

        # Кнопки действий
        actions = QHBoxLayout()
        actions.setContentsMargins(0, 10, 0, 0)
        actions.setSpacing(8)

        self._like_btn = QPushButton("♥")
        self._like_btn.setObjectName("rpLikeButton")
        self._like_btn.setFixedSize(32, 32)
        self._like_btn.setCheckable(True)
        self._like_btn.setChecked(True)
        self._like_btn.clicked.connect(self._on_like)

        tag1 = QPushButton("Electronic")
        tag1.setObjectName("rpTag")
        tag2 = QPushButton("Pop")
        tag2.setObjectName("rpTag")

        share_btn = QPushButton("⤴")
        share_btn.setObjectName("rpShareButton")
        share_btn.setFixedSize(28, 28)

        actions.addWidget(self._like_btn)
        actions.addWidget(tag1)
        actions.addWidget(tag2)
        actions.addStretch()
        actions.addWidget(share_btn)

        v.addWidget(self._song_lbl)
        v.addWidget(self._artist_lbl)
        v.addLayout(actions)
        return w

    def _build_mini_seek(self) -> QWidget:
        from views.seek_slider import SeekSlider  # локальный импорт во избежание цикла

        w = QWidget()
        w.setObjectName("rpMiniSeek")
        v = QVBoxLayout(w)
        v.setContentsMargins(20, 14, 20, 0)
        v.setSpacing(4)

        self._mini_slider = SeekSlider(Qt.Orientation.Horizontal)
        self._mini_slider.setObjectName("miniSeekSlider")
        self._mini_slider.setRange(0, 100)
        self._mini_slider.setValue(38)

        times = QHBoxLayout()
        times.setContentsMargins(0, 0, 0, 0)
        self._cur_lbl   = QLabel("1:26")
        self._cur_lbl.setObjectName("seekTimeLabel")
        self._total_lbl = QLabel("3:47")
        self._total_lbl.setObjectName("seekTimeLabel")
        times.addWidget(self._cur_lbl)
        times.addStretch()
        times.addWidget(self._total_lbl)

        v.addWidget(self._mini_slider)
        v.addLayout(times)
        return w

    def _build_queue(self) -> QWidget:
        w = QWidget()
        w.setObjectName("rpQueue")
        v = QVBoxLayout(w)
        v.setContentsMargins(20, 14, 20, 12)
        v.setSpacing(2)

        lbl = QLabel("UP NEXT")
        lbl.setObjectName("queueSectionLabel")
        v.addWidget(lbl)

        scroll = QScrollArea()
        scroll.setObjectName("queueScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        self._queue_layout = QVBoxLayout(inner)
        self._queue_layout.setContentsMargins(0, 0, 0, 0)
        self._queue_layout.setSpacing(2)
        self._queue_layout.addStretch()

        scroll.setWidget(inner)
        v.addWidget(scroll)
        return w

    # ── Публичный API ─────────────────────────────────────────────────────

    def update_track(self, track: Track) -> None:
        self._song_lbl.setText(track.title)
        self._artist_lbl.setText(f"{track.artist} · {track.album}")
        self._total_lbl.setText(track.duration_str)
        self._mini_slider.setRange(0, track.duration_sec)
        self._like_btn.setChecked(track.is_liked)
        self._update_art_color(track)

    def update_position(self, seconds: int, total: int) -> None:
        self._mini_slider.setValue(seconds)
        m, s = divmod(seconds, 60)
        self._cur_lbl.setText(f"{m}:{s:02d}")

    def update_queue(self, tracks: list[Track], current_index: int) -> None:
        # Очищаем старые виджеты (кроме stretch)
        while self._queue_layout.count() > 1:
            item = self._queue_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        upcoming = tracks[current_index + 1:current_index + 6]
        for i, track in enumerate(upcoming):
            actual_idx = current_index + 1 + i
            qi = QueueItem(actual_idx, track, is_next=(i == 0))
            qi.clicked.connect(self.queue_track_clicked)
            self._queue_layout.insertWidget(i, qi)

    # ── Внутреннее ───────────────────────────────────────────────────────

    def _on_like(self) -> None:
        self.like_toggled.emit()

    def _update_art_color(self, track: Track) -> None:
        colors = {
            "AURORA":        ("#4A5AA7", "#7B5EA7"),
            "Khruangbin":    ("#C05A3A", "#F0A500"),
            "Still Woozy":   ("#3A8FA0", "#3BBFBF"),
            "Tame Impala":   ("#3DAA6E", "#3A8FA0"),
            "Bonobo":        ("#1A2A4A", "#4A90E2"),
            "Soccer Mommy":  ("#8A5EA7", "#4A90E2"),
            "Lorde":         ("#2A4A2A", "#3DAA6E"),
            "beabadoobee":   ("#C05A3A", "#F0A500"),
            "Glass Animals": ("#1A4A3A", "#3BBFBF"),
            "Phoebe Bridgers":("#4A3A5A", "#8A5EA7"),
        }
        c1, c2 = colors.get(track.artist, ("#4A5AA7", "#7B5EA7"))
        self._art_frame.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {c1}, stop:1 {c2}); border-radius: 14px;"
        )
