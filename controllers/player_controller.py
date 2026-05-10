# controllers/player_controller.py
# Логика воспроизведения. Не содержит ни одного UI-виджета.
# Общается с видами через сигналы Qt.

from __future__ import annotations

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from models.track import Track


class PlayerController(QObject):
    """
    Управляет состоянием плеера:
      - текущий трек, очередь, позиция
      - play / pause / next / prev / seek / volume
    Все изменения состояния публикуются через сигналы.
    """

    # ── Сигналы ───────────────────────────────────────────────────────────
    track_changed   = pyqtSignal(Track)          # новый трек стал текущим
    position_changed = pyqtSignal(int)           # позиция в секундах
    playback_changed = pyqtSignal(bool)          # True = играет, False = пауза
    queue_changed   = pyqtSignal(list)           # обновился список очереди
    volume_changed  = pyqtSignal(int)            # громкость 0–100
    liked_changed   = pyqtSignal(Track, bool)    # трек, новое значение is_liked

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._queue:    list[Track] = []
        self._index:    int = 0
        self._position: int = 0          # секунды
        self._playing:  bool = False
        self._volume:   int = 72
        self._shuffle:  bool = False
        self._repeat:   bool = False

        # Таймер имитирует прогресс трека (раз в секунду)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    # ── Публичный API ─────────────────────────────────────────────────────

    def load_queue(self, tracks: list[Track], start_index: int = 0) -> None:
        """Загружает новую очередь и начинает воспроизведение с start_index."""
        self._queue = list(tracks)
        self._index = max(0, min(start_index, len(tracks) - 1))
        self._position = 0
        self.queue_changed.emit(self._queue)
        if self._queue:
            self._emit_track()
            self.play()

    def play(self) -> None:
        if not self._queue:
            return
        self._playing = True
        self._timer.start()
        self.playback_changed.emit(True)

    def pause(self) -> None:
        self._playing = False
        self._timer.stop()
        self.playback_changed.emit(False)

    def toggle_play(self) -> None:
        if self._playing:
            self.pause()
        else:
            self.play()

    def next_track(self) -> None:
        if not self._queue:
            return
        self._index = (self._index + 1) % len(self._queue)
        self._position = 0
        self._emit_track()
        if self._playing:
            self._timer.start()

    def prev_track(self) -> None:
        if not self._queue:
            return
        # Если прошло > 3 с — перемотать в начало, иначе — предыдущий трек
        if self._position > 3:
            self._position = 0
            self.position_changed.emit(0)
        else:
            self._index = (self._index - 1) % len(self._queue)
            self._position = 0
            self._emit_track()

    def seek(self, seconds: int) -> None:
        if not self._queue:
            return
        dur = self.current_track.duration_sec
        self._position = max(0, min(seconds, dur))
        self.position_changed.emit(self._position)

    def set_volume(self, value: int) -> None:
        self._volume = max(0, min(100, value))
        self.volume_changed.emit(self._volume)

    def toggle_like(self) -> None:
        if not self._queue:
            return
        t = self.current_track
        t.is_liked = not t.is_liked
        self.liked_changed.emit(t, t.is_liked)

    # ── Свойства ──────────────────────────────────────────────────────────

    @property
    def current_track(self) -> Track | None:
        if self._queue:
            return self._queue[self._index]
        return None

    @property
    def is_playing(self) -> bool:
        return self._playing

    @property
    def position(self) -> int:
        return self._position

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def queue(self) -> list[Track]:
        return list(self._queue)

    # ── Внутреннее ───────────────────────────────────────────────────────

    def _tick(self) -> None:
        if not self._queue:
            return
        dur = self.current_track.duration_sec
        self._position += 1
        self.position_changed.emit(self._position)
        if self._position >= dur:
            self.next_track()

    def _emit_track(self) -> None:
        track = self.current_track
        if track:
            self.track_changed.emit(track)
            self.position_changed.emit(self._position)
