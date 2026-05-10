# views/sidebar.py
from __future__ import annotations
from PyQt6.QtCore import pyqtSignal, Qt, QRect
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtGui import QPainter, QColor
from services.localization_service import L

class NavButton(QPushButton):
    def __init__(self, icon: str, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCheckable(True); self.setObjectName("navButton"); self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._name = name; self._badge_count = 0
        layout = QHBoxLayout(self); layout.setContentsMargins(15, 10, 15, 10); layout.setSpacing(15)
        self.icon_lbl = QLabel(icon); self.icon_lbl.setStyleSheet("font-size: 18px; background: transparent;")
        self.text_lbl = QLabel(L.tr(self._name.lower())); self.text_lbl.setObjectName("nav_text")
        layout.addWidget(self.icon_lbl); layout.addWidget(self.text_lbl); layout.addStretch()
        L.lang_changed.connect(self.update_text)

    def set_badge(self, count: int):
        self._badge_count = count; self.update()

    def update_text(self): self.text_lbl.setText(L.tr(self._name.lower()))

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._badge_count > 0:
            painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor("#F14635")); painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(35, 10, 10, 10)

class SidebarWidget(QFrame):
    nav_clicked = pyqtSignal(str)
    theme_toggled = pyqtSignal(bool) # True = Dark

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent); self._is_dark = False
        self.setObjectName("sidebar"); self.setFixedWidth(260); self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self); layout.setContentsMargins(15, 40, 15, 30); layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout(); logo = QLabel("Kaspi.kz"); logo.setObjectName("logo_label"); header.addWidget(logo); header.addStretch()
        
        # Theme Toggle
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(40, 30); self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setStyleSheet("background: #F3F4F6; border-radius: 8px; font-size: 14px; border: none;")
        self.theme_btn.clicked.connect(self._on_theme_clicked); header.addWidget(self.theme_btn)
        
        # Lang Switch
        self.lang_kk = QPushButton("KK"); self.lang_kk.setCheckable(True); self.lang_kk.setFixedSize(40, 30)
        self.lang_ru = QPushButton("RU"); self.lang_ru.setCheckable(True); self.lang_ru.setFixedSize(40, 30); self.lang_ru.setChecked(True)
        ls = "QPushButton { font-size: 11px; font-weight: 800; border-radius: 8px; background: #F3F4F6; border: none; } QPushButton:checked { background: #1A1A1A; color: white; }"
        self.lang_kk.setStyleSheet(ls); self.lang_ru.setStyleSheet(ls)
        self.lang_kk.clicked.connect(lambda: self._set_lang("kk")); self.lang_ru.clicked.connect(lambda: self._set_lang("ru"))
        header.addWidget(self.lang_kk); header.addWidget(self.lang_ru); layout.addLayout(header)

        self.buttons: dict[str, NavButton] = {}
        menu = [("🛒", "Shop"), ("🏦", "Bank"), ("📊", "Analytics"), ("🔔", "Notifications"), ("💳", "Payments"), ("💸", "Transfer"), ("📱", "Code"), ("ℹ️", "Gid"), ("👤", "Profile"), ("⚙️", "Admin")]
        for icon, name in menu:
            btn = NavButton(icon, name); btn.setMinimumHeight(55); btn.clicked.connect(lambda _, n=name: self._on_btn_clicked(n))
            layout.addWidget(btn); self.buttons[name] = btn
        self.buttons["Shop"].setChecked(True); layout.addStretch()

    def set_notification_badge(self, c: int):
        if "Notifications" in self.buttons: self.buttons["Notifications"].set_badge(c)

    def _set_lang(self, lang):
        L.set_language(lang); self.lang_kk.setChecked(lang == "kk"); self.lang_ru.setChecked(lang == "ru")

    def _on_theme_clicked(self):
        self._is_dark = not self._is_dark
        self.theme_btn.setText("☀️" if self._is_dark else "🌙")
        self.theme_toggled.emit(self._is_dark)

    def _on_btn_clicked(self, name: str) -> None:
        for btn_name, btn in self.buttons.items(): btn.setChecked(btn_name == name)
        self.nav_clicked.emit(name)

    def select_item(self, name: str) -> None:
        if name in self.buttons: self._on_btn_clicked(name)
