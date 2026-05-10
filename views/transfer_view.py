# views/transfer_view.py
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QLineEdit, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt
from services.shop_service import ShopService
from services.localization_service import L
from views.base_view import BaseView

class TransferView(BaseView):
    def __init__(self, service: ShopService, parent: QWidget | None = None) -> None:
        self._service = service
        super().__init__(parent)
        self.setObjectName("transfer_view")
        self.refresh_ui()

    def update_localization(self): self.refresh_ui()

    def refresh_ui(self) -> None:
        self.set_title(L.tr("transfer"))
        self.clear_layout(self._content_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #EDEDED; border-radius: 12px; background: white; }
            QTabBar::tab { background: #F8F9FB; padding: 12px 30px; font-weight: 700; border-top-left-radius: 8px; border-top-right-radius: 8px; }
            QTabBar::tab:selected { background: white; color: #0089d0; }
        """)

        # Tab 1: Top-up
        top_up_w = QWidget(); tl = QVBoxLayout(top_up_w); tl.setContentsMargins(30, 30, 30, 30); tl.setSpacing(20)
        tl.addWidget(QLabel(L.tr("transfer_title"), styleSheet="font-size: 18px; font-weight: 800;"))
        
        style = "padding: 15px; border: 1px solid #E5E7EB; border-radius: 12px; font-size: 16px; background: #F9FAFB;"
        self.amt_in = QLineEdit(); self.amt_in.setPlaceholderText(L.tr("amount")); self.amt_in.setStyleSheet(style); tl.addWidget(self.amt_in)
        
        btn = QPushButton(L.tr("top_up")); btn.setFixedHeight(50); btn.setStyleSheet("background: #00a260; color: white; border-radius: 12px; font-weight: 800;")
        btn.clicked.connect(self._on_top_up); tl.addWidget(btn); tl.addStretch()

        # Tab 2: Send Money
        send_w = QWidget(); sl = QVBoxLayout(send_w); sl.setContentsMargins(30, 30, 30, 30); sl.setSpacing(20)
        sl.addWidget(QLabel("Перевод клиенту Kaspi" if L.current_lang=="ru" else "Kaspi клиентіне аударым", styleSheet="font-size: 18px; font-weight: 800;"))
        
        self.phone_in = QLineEdit(); self.phone_in.setPlaceholderText(L.tr("recipient")); self.phone_in.setStyleSheet(style); sl.addWidget(self.phone_in)
        self.send_amt_in = QLineEdit(); self.send_amt_in.setPlaceholderText(L.tr("amount")); self.send_amt_in.setStyleSheet(style); sl.addWidget(self.send_amt_in)
        
        sbtn = QPushButton(L.tr("transfer_btn")); sbtn.setFixedHeight(50); sbtn.setStyleSheet("background: #f14635; color: white; border-radius: 12px; font-weight: 800;")
        sbtn.clicked.connect(self._on_send); sl.addWidget(sbtn); sl.addStretch()

        self.tabs.addTab(top_up_w, "Пополнение" if L.current_lang=="ru" else "Толтыру")
        self.tabs.addTab(send_w, "Перевод" if L.current_lang=="ru" else "Аударым")
        
        self._content_layout.addWidget(self.tabs)
        self._content_layout.addStretch()

    def _on_top_up(self):
        a = self.amt_in.text()
        if a.isdigit() and int(a) > 0:
            self._service.db.top_up_balance(int(a))
            QMessageBox.information(self, "Kaspi.kz", L.tr("success"))
            self.amt_in.clear()
        else: QMessageBox.warning(self, "Қате", "Соманы дұрыс енгізіңіз")

    def _on_send(self):
        p = self.phone_in.text(); a = self.send_amt_in.text()
        if p and a.isdigit() and int(a) > 0:
            ok, msg = self._service.db.process_transfer(p, int(a))
            if ok:
                QMessageBox.information(self, "Kaspi.kz", msg)
                self.phone_in.clear(); self.send_amt_in.clear()
            else: QMessageBox.warning(self, "Қате", msg)
        else: QMessageBox.warning(self, "Қате", "Мәліметтерді толық енгізіңіз")
