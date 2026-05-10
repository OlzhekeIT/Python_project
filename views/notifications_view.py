# views/notifications_view.py
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
from PyQt6.QtCore import Qt
from views.base_view import BaseView
from services.localization_service import L
from services.shop_service import ShopService

class NotificationItemWidget(QFrame):
    def __init__(self, n: dict):
        super().__init__()
        self.setObjectName("info_section")
        is_read = n.get('is_read', 0)
        bg = "white" if is_read else "#F1F9FF"
        self.setStyleSheet(f"background: {bg}; border-radius: 16px; border: 1px solid #EDEDED;")
        
        l = QVBoxLayout(self); l.setContentsMargins(20, 20, 20, 20); l.setSpacing(8)
        
        h = QHBoxLayout(); h.setSpacing(12)
        icon = "🔔"
        if "Счет" in n['title'] or "пополнен" in n['title']: icon = "💰"
        elif "Платеж" in n['title'] or "Покупка" in n['title']: icon = "🛍️"
        elif "Лимит" in n['title']: icon = "⚙️"
        
        icon_lbl = QLabel(icon); icon_lbl.setStyleSheet("font-size: 22px;")
        h.addWidget(icon_lbl)
        
        title = QLabel(n['title']); title.setStyleSheet("font-size: 16px; font-weight: 800; color: #1A1A1A;")
        h.addWidget(title, stretch=1)
        
        ts = QLabel(n['timestamp']); ts.setStyleSheet("font-size: 12px; color: #757575;")
        h.addWidget(ts, alignment=Qt.AlignmentFlag.AlignTop)
        l.addLayout(h)
        
        msg = QLabel(n['message']); msg.setWordWrap(True); msg.setStyleSheet("font-size: 14px; color: #4B5563; line-height: 1.4;")
        l.addWidget(msg)

class NotificationsView(BaseView):
    def __init__(self, service: ShopService, parent: QWidget | None = None) -> None:
        self._service = service
        super().__init__(parent)
        self.setObjectName("notifications_view")
        self.refresh_data()

    def update_localization(self):
        self.set_title(L.tr("notifications") if "notifications" in L._strings[L.current_lang] else "Сообщения")
        self.refresh_data()

    def refresh_data(self):
        self.set_title("Сообщения" if L.current_lang=="ru" else "Хабарламалар")
        self.clear_layout(self._content_layout)
        
        notes = self._service.db.get_notifications()
        if not notes:
            self._content_layout.addStretch()
            empty = QLabel("У вас нет новых сообщений" if L.current_lang=="ru" else "Сізде жаңа хабарламалар жоқ")
            empty.setStyleSheet("color: #9CA3AF; font-size: 16px;")
            self._content_layout.addWidget(empty, alignment=Qt.AlignmentFlag.AlignCenter)
            self._content_layout.addStretch()
            return
            
        for n in notes:
            self._content_layout.addWidget(NotificationItemWidget(n))
        
        self._content_layout.addStretch()
        self._service.db.mark_notifications_read()
