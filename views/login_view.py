# views/login_view.py
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class LoginView(QWidget):
    authenticated = pyqtSignal()
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("login_view")
        self.setStyleSheet("background: white;")
        self._pin = ""
        self._correct_pin = "0000"
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 100, 0, 100); layout.setSpacing(40)
        
        logo = QLabel("Kaspi.kz"); logo.setStyleSheet("color: #F14635; font-size: 42px; font-weight: 1000;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(logo)
        
        self.title = QLabel("Введите код доступа" if True else "Құпия кодты енгізіңіз")
        self.title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1A1A1A;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.title)
        
        # PIN Dots
        self.dots_h = QHBoxLayout(); self.dots_h.setSpacing(20); self.dots_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dots = []
        for _ in range(4):
            d = QFrame(); d.setFixedSize(16, 16); d.setStyleSheet("background: #E5E7EB; border-radius: 8px;")
            self.dots_h.addWidget(d); self.dots.append(d)
        layout.addLayout(self.dots_h)
        
        # Keypad
        grid = QGridLayout(); grid.setSpacing(20); grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nums = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "⌫"]
        for i, n in enumerate(nums):
            if n == "": continue
            btn = QPushButton(n); btn.setFixedSize(80, 80)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            style = "QPushButton { border: 2px solid #F3F4F6; border-radius: 40px; font-size: 24px; font-weight: 700; color: #1A1A1A; background: white; } QPushButton:hover { background: #F8F9FB; border-color: #E5E7EB; } QPushButton:pressed { background: #F3F4F6; }"
            if n == "⌫": style = "QPushButton { border: none; font-size: 24px; color: #9CA3AF; }"
            btn.setStyleSheet(style)
            btn.clicked.connect(lambda _, val=n: self._on_key_clicked(val))
            grid.addWidget(btn, i // 3, i % 3)
        layout.addLayout(grid); layout.addStretch()

    def _on_key_clicked(self, val):
        if val == "⌫":
            if len(self._pin) > 0: self._pin = self._pin[:-1]
        else:
            if len(self._pin) < 4: self._pin += val
            
        self._update_dots()
        
        if len(self._pin) == 4:
            if self._pin == self._correct_pin: self.authenticated.emit()
            else:
                self._pin = ""; self._update_dots()
                self.title.setText("Неверный код. Попробуйте еще раз")
                self.title.setStyleSheet("font-size: 18px; font-weight: 700; color: #F14635;")

    def _update_dots(self):
        for i, d in enumerate(self.dots):
            color = "#1A1A1A" if i < len(self._pin) else "#E5E7EB"
            d.setStyleSheet(f"background: {color}; border-radius: 8px;")
