# views/profile_view.py
from __future__ import annotations
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QHBoxLayout, QScrollArea, QLineEdit, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen
from services.shop_service import ShopService
from services.localization_service import L
from views.base_view import BaseView

class AvatarWidget(QWidget):
    clicked = pyqtSignal()
    def __init__(self, path: str = ""):
        super().__init__()
        self.setFixedSize(120, 120); self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.path = path

    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        # Circle Background
        painter.setBrush(QColor("#F3F4F6")); painter.setPen(QPen(QColor("#E5E7EB"), 2))
        painter.drawEllipse(rect)
        
        if self.path:
            pix = QPixmap(self.path)
            if not pix.isNull():
                painter.setBrush(QBrush(pix.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)))
                painter.drawEllipse(rect)
        else:
            painter.setPen(QColor("#9CA3AF"))
            f = self.font(); f.setPointSize(40); painter.setFont(f)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "👤")

    def mousePressEvent(self, event): self.clicked.emit()

class AchievementBadge(QFrame):
    def __init__(self, title: str, is_unlocked: bool):
        super().__init__()
        bg = "#FFFFFF" if is_unlocked else "#F9FAFB"; border = "#EDEDED" if is_unlocked else "#E5E7EB"
        self.setStyleSheet(f"background: {bg}; border: 1px solid {border}; border-radius: 12px;")
        self.setFixedWidth(150); self.setFixedHeight(90)
        l = QVBoxLayout(self); l.setContentsMargins(8, 8, 8, 8); l.setSpacing(2)
        icon = QLabel("🏅" if is_unlocked else "🔒"); icon.setStyleSheet("font-size: 20px;"); icon.setAlignment(Qt.AlignmentFlag.AlignCenter); l.addWidget(icon)
        t = QLabel(title); t.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {'#1A1A1A' if is_unlocked else '#9CA3AF'};"); t.setWordWrap(True); t.setAlignment(Qt.AlignmentFlag.AlignCenter); l.addWidget(t)

class ProfileView(BaseView):
    def __init__(self, service: ShopService, parent: QWidget | None = None) -> None:
        self._service = service; self._edit_mode = False
        super().__init__(parent); self.setObjectName("profile_view"); self.refresh_data()

    def update_localization(self): self.set_title(L.tr("profile")); self.refresh_data()

    def refresh_data(self):
        self.set_title(L.tr("profile")); self.clear_layout(self._content_layout)
        user = self._service.db.get_user_data()
        
        # --- Top Section (Avatar + Name) ---
        top = QHBoxLayout(); top.setSpacing(30)
        self.avatar = AvatarWidget(user.get('avatar_path', "")); self.avatar.clicked.connect(self._change_avatar); top.addWidget(self.avatar)
        
        u_info = QVBoxLayout(); u_info.setSpacing(5)
        if not self._edit_mode:
            name_h = QHBoxLayout(); name_h.addWidget(QLabel(user['name'], styleSheet="font-size:28px; font-weight:900; color:#1A1A1A;")); name_h.addStretch()
            eb = QPushButton("✎"); eb.setFixedSize(30, 30); eb.setStyleSheet("background:#F3F4F6; border-radius:15px; border:none;"); eb.clicked.connect(self._toggle_edit); name_h.addWidget(eb); u_info.addLayout(name_h)
            u_info.addWidget(QLabel(user['phone'], styleSheet="color:#757575; font-size:16px;"))
        else:
            self.name_in = QLineEdit(user['name']); self.name_in.setStyleSheet("font-size:20px; padding:8px; border:1px solid #0089d0; border-radius:8px;")
            self.phone_in = QLineEdit(user['phone']); self.phone_in.setStyleSheet("font-size:16px; padding:8px; border:1px solid #E5E7EB; border-radius:8px;")
            u_info.addWidget(self.name_in); u_info.addWidget(self.phone_in)
            sb = QPushButton("Сақтау" if L.current_lang=="kk" else "Сохранить"); sb.setFixedHeight(35); sb.setStyleSheet("background:#1A1A1A; color:white; border-radius:8px;"); sb.clicked.connect(self._save_profile); u_info.addWidget(sb)
        u_info.addStretch(); top.addLayout(u_info, stretch=1); self._content_layout.addLayout(top)

        # --- Credit Score (NumPy Logic) ---
        cs_f = QFrame(); cs_f.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #EDEDED; padding: 20px;")
        cl = QHBoxLayout(cs_f)
        
        # Calculate Score using NumPy
        balance = user['balance']; debt = user['red_debt']; limit = user['red_limit']
        # Weights: Balance (40%), Debt Ratio (40%), Transactions (20%)
        b_score = min(400, (balance / 2000000) * 400)
        d_ratio = (limit - debt) / limit if limit > 0 else 1.0
        d_score = d_ratio * 400
        total_score = int(300 + b_score + d_score * 0.5) # Range ~300-850
        
        score_v = QVBoxLayout(); score_v.addWidget(QLabel("Кредиттік рейтинг" if L.current_lang=="kk" else "Кредитный рейтинг", styleSheet="color:#757575; font-weight:600; font-size:13px;"))
        sl = QLabel(str(total_score)); color = "#059669" if total_score > 700 else "#D97706" if total_score > 500 else "#F14635"
        sl.setStyleSheet(f"font-size: 36px; font-weight: 1000; color: {color};"); score_v.addWidget(sl)
        cl.addLayout(score_v); cl.addStretch()
        
        status = "Өте жақсы" if total_score > 750 else "Жақсы" if total_score > 600 else "Орташа"
        if L.current_lang == "ru": status = "Отличный" if total_score > 750 else "Хороший" if total_score > 600 else "Средний"
        cl.addWidget(QLabel(status, styleSheet=f"background: {color}20; color: {color}; padding: 10px 20px; border-radius: 20px; font-weight: 800;"))
        self._content_layout.addWidget(cs_f)

        # --- Bonuses ---
        bf = QFrame(); bf.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #059669, stop:1 #10B981); border-radius: 20px; border: none; padding: 25px;")
        bl = QHBoxLayout(bf); bv = QVBoxLayout(); bv.addWidget(QLabel("Kaspi Бонустар", styleSheet="color:white; opacity:0.8; font-weight:600;")); bv.addWidget(QLabel(f"{user['bonuses']:,} B", styleSheet="color:white; font-size:32px; font-weight:900;")); bl.addLayout(bv, stretch=1)
        if user['bonuses'] > 0:
            cb = QPushButton("Пайдалану"); cb.setFixedSize(120, 45); cb.setStyleSheet("background:white; color:#059669; border-radius:12px; font-weight:800;"); cb.clicked.connect(self._on_convert); bl.addWidget(cb)
        self._content_layout.addWidget(bf)

        # --- Achievements ---
        self._content_layout.addWidget(QLabel("Марапаттар" if L.current_lang=="kk" else "Достижения", styleSheet="font-size:18px; font-weight: 800;"))
        as_ = QScrollArea(); as_.setWidgetResizable(True); as_.setFixedHeight(120); as_.setFrameShape(QFrame.Shape.NoFrame); as_.setStyleSheet("background:transparent;")
        aw = QWidget(); al = QHBoxLayout(aw); al.setContentsMargins(0, 0, 0, 0); al.setSpacing(15)
        for a in self._service.db.get_achievements(): al.addWidget(AchievementBadge(a['title'], bool(a['is_unlocked'])))
        al.addStretch(); as_.setWidget(aw); self._content_layout.addWidget(as_)

        # --- Menu ---
        menu = QFrame(); mv = QVBoxLayout(menu); menu.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #EDEDED;"); mv.setContentsMargins(10, 10, 10, 10); mv.setSpacing(0)
        items = [("📦 " + ("Тапсырыстарым" if L.current_lang=="kk" else "Мои заказы")), ("⭐ " + ("Таңдаулылар" if L.current_lang=="kk" else "Избранное")), ("⚙️ " + ("Баптаулар" if L.current_lang=="kk" else "Настройки"))]
        for i, item in enumerate(items):
            btn = QPushButton(item); btn.setCursor(Qt.CursorShape.PointingHandCursor); btn.setStyleSheet("QPushButton { text-align:left; padding:18px; font-size:15px; border:none; background:transparent; font-weight:600; } QPushButton:hover { background: #F8F9FB; border-radius:12px; }"); mv.addWidget(btn)
            if i < len(items)-1: line = QFrame(); line.setFixedHeight(1); line.setStyleSheet("background:#F3F4F6;"); mv.addWidget(line)
        self._content_layout.addWidget(menu); self._content_layout.addStretch()

    def _toggle_edit(self): self._edit_mode = True; self.refresh_data()
    def _save_profile(self):
        n = self.name_in.text().strip(); p = self.phone_in.text().strip()
        if n: self._service.db.update_profile(n, p); self._edit_mode = False; self.refresh_data()
    def _change_avatar(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Avatar", "", "Images (*.png *.jpg *.jpeg)")
        if f: self._service.db.update_avatar(f); self.refresh_data()
    def _on_convert(self):
        ok, msg = self._service.db.convert_bonuses()
        if ok: QMessageBox.information(self, "Бонус", msg); self.refresh_data()
