# views/playback_bar.py
# Нижняя панель воспроизведения.
# Три зоны: трек-инфо | управление + сикбар | доп. кнопки + громкость.

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy,
)

from views.seek_slider import SeekSlider
from models.track import Track


class IconButton(QPushButton):
    """Маленькая иконочная кнопка без рамки."""

    def __init__(self, icon: str, tooltip: str = "",
                 object_name: str = "iconButton",
                 parent: QWidget | None = None) -> None:
        super().__init__(icon, parent)
        self.setObjectName(object_name)
        if tooltip:
            self.setToolTip(tooltip)
        self.setFixedSize(34, 34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class PlaybackBar(QWidget):
    """
    Нижняя панель.
    Сигналы:
      play_pause_clicked()
      next_clicked()
      prev_clicked()
      seek_requested(seconds: int)
      volume_changed(value: int)   — 0..100
      shuffle_clicked()
      repeat_clicked()
      like_clicked()
    """

    play_pause_clicked = pyqtSignal()
    next_clicked       = pyqtSignal()
    prev_clicked       = pyqtSignal()
    seek_requested     = pyqtSignal(int)
    volume_changed     = pyqtSignal(int)
    shuffle_clicked    = pyqtSignal()
    repeat_clicked     = pyqtSignal()
    like_clicked       = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("playbackBar")
        self.setFixedHeight(86)

        root = QHBoxLayout(self)
        root.setContentsMargins(24, 0, 24, 0)
        root.setSpacing(12)

        root.addWidget(self._build_track_info(), stretch=0)
        root.addWidget(self._build_center(),     stretch=1)
        root.addWidget(self._build_right(),      stretch=0)

    # ── Зоны ─────────────────────────────────────────────────────────────

    def _build_track_info(self) -> QWidget:
        w = QWidget()
        w.setObjectName("pbTrackInfo")
        w.setFixedWidth(260)

        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)

        self._pb_art = QFrame()
        self._pb_art.setObjectName("pbArt")
        self._pb_art.setFixedSize(48, 48)
        self._pb_art.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #4A5AA7, stop:1 #7B5EA7); border-radius: 10px;"
        )

        info = QVBoxLayout()
        info.setSpacing(1)
        info.setContentsMargins(0, 0, 0, 0)

        self._pb_title = QLabel("Runaway")
        self._pb_title.setObjectName("pbTitle")

        self._pb_artist = QLabel("AURORA")
        self._pb_artist.setObjectName("pbArtist")

        info.addWidget(self._pb_title)
        info.addWidget(self._pb_artist)

        self._pb_like = IconButton("♥", "Like", "pbLikeButton")
        self._pb_like.setCheckable(True)
        self._pb_like.setChecked(True)
        self._pb_like.clicked.connect(self.like_clicked)

        h.addWidget(self._pb_art)
        h.addLayout(info)
        h.addWidget(self._pb_like)
        return w

    def _build_center(self) -> QWidget:
        w = QWidget()
        w.setObjectName("pbCenter")

        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(8)
        v.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Кнопки управления
        controls = QHBoxLayout()
        controls.setSpacing(4)
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._btn_shuffle = IconButton("⇌", "Shuffle", "ctrlButton")
        self._btn_shuffle.setCheckable(True)
        self._btn_shuffle.setChecked(True)
        self._btn_shuffle.clicked.connect(self.shuffle_clicked)

        self._btn_prev = IconButton("⏮", "Previous", "ctrlButton")
        self._btn_prev.clicked.connect(self.prev_clicked)

        self._btn_play = QPushButton("⏸")
        self._btn_play.setObjectName("playButton")
        self._btn_play.setFixedSize(44, 44)
        self._btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_play.clicked.connect(self.play_pause_clicked)

        self._btn_next = IconButton("⏭", "Next", "ctrlButton")
        self._btn_next.clicked.connect(self.next_clicked)

        self._btn_repeat = IconButton("⇄", "Repeat", "ctrlButton")
        self._btn_repeat.setCheckable(True)
        self._btn_repeat.clicked.connect(self.repeat_clicked)

        controls.addStretch()
        controls.addWidget(self._btn_shuffle)
        controls.addWidget(self._btn_prev)
        controls.addWidget(self._btn_play)
        controls.addWidget(self._btn_next)
        controls.addWidget(self._btn_repeat)
        controls.addStretch()

        # Сикбар
        seek_row = QHBoxLayout()
        seek_row.setSpacing(10)
        seek_row.setContentsMargins(0, 0, 0, 0)

        self._cur_time = QLabel("1:26")
        self._cur_time.setObjectName("pbTimeLabel")
        self._cur_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._cur_time.setFixedWidth(36)

        self._seekbar = SeekSlider(Qt.Orientation.Horizontal)
        self._seekbar.setObjectName("mainSeekSlider")
        self._seekbar.setRange(0, 227)
        self._seekbar.setValue(86)
        self._seekbar.seek_requested.connect(self.seek_requested)

        self._total_time = QLabel("3:47")
        self._total_time.setObjectName("pbTimeLabel")
        self._total_time.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._total_time.setFixedWidth(36)

        seek_row.addWidget(self._cur_time)
        seek_row.addWidget(self._seekbar, stretch=1)
        seek_row.addWidget(self._total_time)

        v.addStretch()
        v.addLayout(controls)
        v.addLayout(seek_row)
        v.addStretch()
        return w

    def _build_right(self) -> QWidget:
        w = QWidget()
        w.setObjectName("pbRight")
        w.setFixedWidth(260)

        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        h.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Бейдж качества
        hifi = QLabel("HIFI")
        hifi.setObjectName("hifiBadge")

        btn_lyrics = IconButton("≡", "Lyrics", "ctrlButton")
        btn_queue  = IconButton("⋮", "Queue",  "ctrlButton")

        # Иконка громкости
        btn_vol = IconButton("♪", "Volume", "ctrlButton")

        # Слайдер громкости
        self._vol_slider = SeekSlider(Qt.Orientation.Horizontal)
        self._vol_slider.setObjectName("volumeSlider")
        self._vol_slider.setRange(0, 100)
        self._vol_slider.setValue(72)
        self._vol_slider.setFixedWidth(80)
        self._vol_slider.seek_requested.connect(self.volume_changed)

        btn_fs = IconButton("⛶", "Fullscreen", "ctrlButton")

        h.addWidget(hifi)
        h.addWidget(btn_lyrics)
        h.addWidget(btn_queue)
        h.addWidget(btn_vol)
        h.addWidget(self._vol_slider)
        h.addWidget(btn_fs)
        return w

    # ── Публичный API ─────────────────────────────────────────────────────

    def update_track(self, track: Track) -> None:
        self._pb_title.setText(track.title)
        self._pb_artist.setText(track.artist)
        self._seekbar.setRange(0, track.duration_sec)
        self._total_time.setText(track.duration_str)
        self._pb_like.setChecked(track.is_liked)
        # Обложка — цвет из данных
        colors = {
            "AURORA":         ("#4A5AA7", "#7B5EA7"),
            "Khruangbin":     ("#C05A3A", "#F0A500"),
            "Still Woozy":    ("#3A8FA0", "#3BBFBF"),
            "Tame Impala":    ("#3DAA6E", "#3A8FA0"),
            "Bonobo":         ("#1A2A4A", "#4A90E2"),
            "Soccer Mommy":   ("#8A5EA7", "#4A90E2"),
            "Lorde":          ("#2A4A2A", "#3DAA6E"),
            "beabadoobee":    ("#C05A3A", "#F0A500"),
            "Glass Animals":  ("#1A4A3A", "#3BBFBF"),
            "Phoebe Bridgers":("#4A3A5A", "#8A5EA7"),
        }
        c1, c2 = colors.get(track.artist, ("#4A5AA7", "#7B5EA7"))
        self._pb_art.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {c1}, stop:1 {c2}); border-radius: 10px;"
        )

    def update_position(self, seconds: int) -> None:
        self._seekbar.setValue(seconds)
        m, s = divmod(seconds, 60)
        self._cur_time.setText(f"{m}:{s:02d}")

    def set_playing(self, playing: bool) -> None:
        self._btn_play.setText("⏸" if playing else "▶")
