# views/seek_slider.py
# Кастомный слайдер с тонкой дорожкой и акцентным заполнением.
# Стилизуется через QSS; форма переопределяется здесь минимально.

from __future__ import annotations

from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtWidgets import QSlider, QStyleOptionSlider, QStyle


class SeekSlider(QSlider):
    """
    Тонкий слайдер прогресса/громкости.
    Рисует собственную дорожку и ручку вместо нативного виджета,
    чтобы добиться точного визуального соответствия макету.
    Акцентные цвета берутся из QSS-свойств через palette() — 
    все конкретные цвета задаются в styles.qss.
    """

    seek_requested = pyqtSignal(int)   # пользователь хочет перемотать

    # Цвета ручки/трека задаются здесь как fallback;
    # QSS перекрывает их через subcontrol styling.
    _TRACK_H   = 4     # высота дорожки, px
    _THUMB_R   = 6     # радиус ручки, px

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal,
                 parent=None) -> None:
        super().__init__(orientation, parent)
        self.setMouseTracking(True)
        self._hovered = False

    # ── Переопределение отрисовки ─────────────────────────────────────────

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        groove = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, opt,
            QStyle.SubControl.SC_SliderGroove, self
        )

        # Позиция ручки (0..1)
        span = self.maximum() - self.minimum()
        ratio = (self.value() - self.minimum()) / span if span else 0

        track_y  = groove.center().y()
        track_x0 = groove.left() + self._THUMB_R
        track_x1 = groove.right() - self._THUMB_R
        track_w  = track_x1 - track_x0

        fill_x = int(track_x0 + ratio * track_w)

        h = self._TRACK_H + (2 if self._hovered else 0)

        # Фоновая дорожка
        bg_color = self.palette().color(self.palette().ColorRole.Mid)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(
            QRect(track_x0, track_y - h // 2, track_w, h), h // 2, h // 2
        )

        # Заполненная часть (акцент)
        acc_color = self.palette().color(self.palette().ColorRole.Highlight)
        painter.setBrush(QBrush(acc_color))
        filled_w = fill_x - track_x0
        if filled_w > 0:
            painter.drawRoundedRect(
                QRect(track_x0, track_y - h // 2, filled_w, h), h // 2, h // 2
            )

        # Ручка
        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QPen(acc_color, 2))
        painter.drawEllipse(
            fill_x - self._THUMB_R, track_y - self._THUMB_R,
            self._THUMB_R * 2, self._THUMB_R * 2
        )

    def enterEvent(self, event) -> None:  # noqa: N802
        self._hovered = True
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        self._hovered = False
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        super().mousePressEvent(event)
        self._jump_to(event.position().x())

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        super().mouseMoveEvent(event)
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._jump_to(event.position().x())

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        super().mouseReleaseEvent(event)
        self.seek_requested.emit(self.value())

    def _jump_to(self, x: float) -> None:
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        groove = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, opt,
            QStyle.SubControl.SC_SliderGroove, self
        )
        x0 = groove.left() + self._THUMB_R
        x1 = groove.right() - self._THUMB_R
        ratio = max(0.0, min(1.0, (x - x0) / (x1 - x0)))
        val = int(self.minimum() + ratio * (self.maximum() - self.minimum()))
        self.setValue(val)
