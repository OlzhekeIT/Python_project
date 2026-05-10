# views/gid_view.py
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit, QPushButton, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal
from views.base_view import BaseView
from services.localization_service import L
class ChatBubble(QFrame):
    def __init__(self, text: str, is_user: bool):
        super().__init__()
        bg_color = '#0089d0' if is_user else 'white'
        txt_color = 'white' if is_user else '#1A1A1A'
        self.setStyleSheet(f"background: {bg_color}; border-radius: 15px; border: {'none' if is_user else '1px solid #EDEDED'};")
        l = QVBoxLayout(self); l.setContentsMargins(15, 10, 15, 10)
        t = QLabel(text); t.setWordWrap(True)
        t.setStyleSheet(f"color: {txt_color}; font-size: 14px; font-weight: 500; background: transparent; border: none;")
        l.addWidget(t)
        # Ensure minimum width and handle long text
        self.setMinimumWidth(50)
        width = t.fontMetrics().horizontalAdvance(text) + 40 if len(text) < 60 else 450
        self.setFixedWidth(min(450, max(100, width)))

class GidView(BaseView):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent); self.setObjectName("gid_view"); self.refresh_data()

    def update_localization(self): self.refresh_data()

    def refresh_data(self):
        self.set_title(L.tr("gid"))
        self.clear_layout(self._content_layout)
        
        # Chat Display Area
        chat_scroll = QScrollArea(); chat_scroll.setWidgetResizable(True); chat_scroll.setFrameShape(QFrame.Shape.NoFrame)
        chat_scroll.setStyleSheet("background: #F8F9FB; border: none;")
        self.chat_content = QWidget(); self.chat_content.setStyleSheet("background: transparent;")
        self.chat_v = QVBoxLayout(self.chat_content); self.chat_v.setContentsMargins(20, 20, 20, 20); self.chat_v.setSpacing(15); self.chat_v.addStretch()
        chat_scroll.setWidget(self.chat_content); self._content_layout.addWidget(chat_scroll, stretch=1)
        
        # Initial Message
        welcome = "Сәлеметсіз бе! Мен Kaspi Guide көмекшісімін. Қандай сұрағыңыз бар?" if L.current_lang=="kk" else "Здравствуйте! Я помощник Kaspi Guide. Какой у вас вопрос?"
        self._add_bubble(welcome, False)
        
        # Input Area
        input_f = QFrame(); input_f.setFixedHeight(80); input_f.setStyleSheet("background: white; border-top: 1px solid #EDEDED;")
        il = QHBoxLayout(input_f); il.setContentsMargins(20, 0, 20, 0); il.setSpacing(15)
        
        self.chat_in = QLineEdit()
        self.chat_in.setPlaceholderText("Сұрақ қойыңыз..." if L.current_lang=="kk" else "Задайте вопрос...")
        self.chat_in.setStyleSheet("padding: 12px 20px; border: 1.5px solid #E5E7EB; border-radius: 20px; background: #F9FAFB; font-size: 14px; color: #1A1A1A;")
        self.chat_in.returnPressed.connect(self._on_send)
        
        send_btn = QPushButton("➔"); send_btn.setFixedSize(45, 45); send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.setStyleSheet("background: #F14635; color: white; border-radius: 22px; font-size: 20px; font-weight: 800; border: none;")
        send_btn.clicked.connect(self._on_send)
        
        il.addWidget(self.chat_in); il.addWidget(send_btn); self._content_layout.addWidget(input_f)

    def _add_bubble(self, text: str, is_user: bool):
        b = ChatBubble(text, is_user)
        h = QHBoxLayout(); h.addStretch() if is_user else None; h.addWidget(b); h.addStretch() if not is_user else None
        self.chat_v.insertLayout(self.chat_v.count()-1, h)

    def _on_send(self):
        text = self.chat_in.text().strip()
        if not text: return
        self._add_bubble(text, True); self.chat_in.clear()
        
        # Simple Logic
        resp = "Кешіріңіз, мен бұл сұрақты түсінбедім. Маманға хабарласып көріңіз." if L.current_lang=="kk" else "Извините, я не понял вопрос. Попробуйте связаться со специалистом."
        t = text.lower()
        if "баланс" in t or "ақша" in t or "деньги" in t: resp = "Теңгеріміңізді «Менің Банкім» бөлімінен көре аласыз." if L.current_lang=="kk" else "Вы можете увидеть свой баланс в разделе «Мой Банк»."
        elif "бонус" in t: resp = "Әр сатып алу үшін 1% бонус беріледі. Оны «Профиль» бөлімінен аударуға болады." if L.current_lang=="kk" else "За каждую покупку начисляется 1% бонусов. Их можно перевести в разделе «Профиль»."
        elif "red" in t: resp = "Kaspi Red арқылы кез келген тауарды 3 айға бөліп төлеуге болады." if L.current_lang=="kk" else "С Kaspi Red вы можете оплатить любой товар в рассрочку на 3 месяца."
        elif "сәлем" in t or "привет" in t: resp = "Сәлем! Мен сізге көмектесуге дайынмын." if L.current_lang=="kk" else "Привет! Я готов вам помочь."
        
        self._add_bubble(resp, False)
