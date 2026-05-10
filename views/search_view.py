# views/search_view.py
# Экран «Search & Browse»: строка поиска, кнопки сортировки, таблица треков.
# Содержит только UI — никакой бизнес-логики.

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel,
)

from models.track import Track


class SearchView(QWidget):
    """
    Экран поиска и сортировки библиотеки.
    Сигналы:
      search_requested(str)  — пользователь вводит текст
      sort_requested(str)    — кнопка сортировки (ключ: title/artist/album/duration)
      track_selected(object) — двойной клик по строке (Track-объект)
    """

    search_requested = pyqtSignal(str)
    sort_requested   = pyqtSignal(str)
    track_selected   = pyqtSignal(object)   # передаёт Track

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("searchView")
        self._displayed: list[Track] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 18, 28, 18)
        root.setSpacing(14)

        root.addWidget(self._build_header())
        root.addWidget(self._build_controls())
        root.addWidget(self._build_table(), stretch=1)

    # ── Секции ───────────────────────────────────────────────────────────

    def _build_header(self) -> QWidget:
        w = QWidget()
        w.setObjectName("searchHeader")
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("Search & Browse")
        lbl.setObjectName("centralTitle")

        self._count_lbl = QLabel("")
        self._count_lbl.setObjectName("searchResultCount")

        h.addWidget(lbl)
        h.addStretch()
        h.addWidget(self._count_lbl)
        return w

    def _build_controls(self) -> QWidget:
        w = QWidget()
        w.setObjectName("searchControls")
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        self._input = QLineEdit()
        self._input.setObjectName("searchInput")
        self._input.setPlaceholderText("Поиск по названию, артисту, альбому…")
        self._input.textChanged.connect(self.search_requested)
        h.addWidget(self._input, stretch=1)

        for label, key in [
            ("Title ↕", "title"),
            ("Artist ↕", "artist"),
            ("Album ↕", "album"),
            ("Duration ↕", "duration"),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("sortButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self.sort_requested.emit(k))
            h.addWidget(btn)

        return w

    def _build_table(self) -> QTableWidget:
        self._table = QTableWidget()
        self._table.setObjectName("searchTable")
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["#", "Title", "Artist", "Album", "Duration"])

        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)

        self._table.setColumnWidth(0, 40)
        self._table.setColumnWidth(4, 72)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.doubleClicked.connect(self._on_double_clicked)

        return self._table

    # ── Публичный API ─────────────────────────────────────────────────────

    def set_tracks(self, tracks: list[Track]) -> None:
        """Заполняет таблицу переданным списком треков."""
        self._displayed = list(tracks)
        self._table.setRowCount(len(tracks))
        for row, track in enumerate(tracks):
            for col, text in enumerate([
                str(row + 1),
                track.title,
                track.artist,
                track.album,
                track.duration_str,
            ]):
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col == 0:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
                    )
                elif col == 4:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                self._table.setItem(row, col, item)
        self._count_lbl.setText(f"{len(tracks)} tracks")

    # ── Внутреннее ───────────────────────────────────────────────────────

    def _on_double_clicked(self, index) -> None:
        row = index.row()
        if 0 <= row < len(self._displayed):
            self.track_selected.emit(self._displayed[row])