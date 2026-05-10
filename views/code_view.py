# views/code_view.py
from __future__ import annotations
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QDialog, QMessageBox, QHBoxLayout, QTabWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from views.base_view import BaseView
from services.localization_service import L
from services.shop_service import ShopService

class QRConfirmDialog(QDialog):
    def __init__(self, merchant: str, amount: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kaspi QR")
        self.setFixedSize(360, 400); self.setStyleSheet("background: white; border-radius: 20px;")
        l = QVBoxLayout(self); l.setContentsMargins(30, 30, 30, 30); l.setSpacing(20)
        logo = QLabel("Kaspi.kz"); logo.setStyleSheet("color: #F14635; font-size: 24px; font-weight: 900;"); logo.setAlignment(Qt.AlignmentFlag.AlignCenter); l.addWidget(logo)
        title = QLabel("Подтвердите оплату" if L.current_lang=="ru" else "Төлемді растаңыз")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1A1A1A;"); title.setAlignment(Qt.AlignmentFlag.AlignCenter); l.addWidget(title)
        info = QFrame(); info.setStyleSheet("background: #F9FAFB; border-radius: 12px; padding: 20px;"); iv = QVBoxLayout(info); iv.setSpacing(10)
        iv.addWidget(QLabel(merchant, styleSheet="font-size: 16px; font-weight: 800; color: #1A1A1A;")); iv.addWidget(QLabel(f"{amount:,} ₸", styleSheet="font-size: 24px; font-weight: 900; color: #1A1A1A;")); l.addWidget(info)
        l.addStretch(); btn = QPushButton("Подтвердить" if L.current_lang=="ru" else "Растау")
        btn.setFixedHeight(55); btn.setStyleSheet("background: #0089d0; color: white; border-radius: 12px; font-weight: 800; font-size: 16px;"); btn.clicked.connect(self.accept); l.addWidget(btn)
        cancel = QPushButton("Отмена" if L.current_lang=="ru" else "Бас тарту"); cancel.setStyleSheet("color: #6B7280; border: none; font-weight: 600;"); cancel.clicked.connect(self.reject); l.addWidget(cancel)

class CodeView(BaseView):
    payment_successful = pyqtSignal()
    def __init__(self, service: ShopService, parent: QWidget | None = None) -> None:
        self._service = service
        super().__init__(parent)
        self.setObjectName("code_view")
        self.refresh_data()

    def update_localization(self): self.refresh_data()

    def refresh_data(self):
        self.set_title("Kaspi QR")
        self.clear_layout(self._content_layout)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #EDEDED; border-radius: 12px; background: white; } QTabBar::tab { background: #F8F9FB; padding: 12px 30px; font-weight: 700; } QTabBar::tab:selected { background: white; color: #0089d0; }")
        
        # --- Tab 1: Scan (Existing) ---
        scan_w = QWidget(); sl = QVBoxLayout(scan_w); sl.setContentsMargins(30, 30, 30, 30); sl.setSpacing(20)
        sl.addStretch()
        qr_f = QFrame(); qr_f.setFixedSize(300, 300); qr_f.setStyleSheet("background: white; border: 1px solid #E5E7EB; border-radius: 20px;")
        qv = QVBoxLayout(qr_f); qp = QLabel("QR"); qp.setStyleSheet("font-size: 100px; color: #F14635; font-weight: 900;"); qp.setAlignment(Qt.AlignmentFlag.AlignCenter); qv.addWidget(qp)
        sl.addWidget(qr_f, alignment=Qt.AlignmentFlag.AlignCenter)
        info = QLabel("Сканируйте QR-код" if L.current_lang=="ru" else "QR-кодты сканерлеңіз"); info.setStyleSheet("font-size: 16px; color: #4B5563; font-weight: 600;"); info.setAlignment(Qt.AlignmentFlag.AlignCenter); sl.addWidget(info)
        sim_btn = QPushButton("Симулировать покупку"); sim_btn.setFixedHeight(50); sim_btn.setStyleSheet("background: #F3F4F6; border-radius: 10px; font-weight: 700;"); sim_btn.clicked.connect(self._simulate_scan); sl.addWidget(sim_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        sl.addStretch()
        
        # --- Tab 2: My QR (New) ---
        my_w = QWidget(); ml = QVBoxLayout(my_w); ml.setContentsMargins(30, 30, 30, 30); ml.setSpacing(20)
        ml.addStretch()
        user = self._service.db.get_user_data()
        ul = QLabel(user['name']); ul.setStyleSheet("font-size: 22px; font-weight: 900; color: #1A1A1A;"); ul.setAlignment(Qt.AlignmentFlag.AlignCenter); ml.addWidget(ul)
        ph = QLabel(user['phone']); ph.setStyleSheet("font-size: 14px; color: #6B7280;"); ph.setAlignment(Qt.AlignmentFlag.AlignCenter); ml.addWidget(ph)
        
        my_qr_f = QFrame(); my_qr_f.setFixedSize(300, 300); my_qr_f.setStyleSheet("background: white; border: 2px solid #1A1A1A; border-radius: 20px;")
        mqv = QVBoxLayout(my_qr_f); mqp = QLabel("QR"); mqp.setStyleSheet("font-size: 100px; color: #1A1A1A; font-weight: 900;"); mqp.setAlignment(Qt.AlignmentFlag.AlignCenter); mqv.addWidget(mqp)
        ml.addWidget(my_qr_f, alignment=Qt.AlignmentFlag.AlignCenter)
        
        recv_btn = QPushButton("Симулировать входящий перевод"); recv_btn.setFixedHeight(50); recv_btn.setStyleSheet("background: #0089d0; color: white; border-radius: 10px; font-weight: 700;"); recv_btn.clicked.connect(self._simulate_receive); ml.addWidget(recv_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        ml.addStretch()
        
        self.tabs.addTab(scan_w, "Kaspi QR")
        self.tabs.addTab(my_w, "Мой QR" if L.current_lang=="ru" else "Менің QR-ым")
        self._content_layout.addWidget(self.tabs)

    def _simulate_scan(self):
        merchants = ["Coffee Day", "Magnum", "Sulpak", "Starbucks"]; m = random.choice(merchants); a = random.randint(1000, 50000)
        d = QRConfirmDialog(m, a, self)
        if d.exec():
            ok, msg, tid = self._service.db.process_general_payment(a, f"QR: {m}")
            if ok: QMessageBox.information(self, "OK", "Төлем сәтті!"); self.payment_successful.emit()
            else: QMessageBox.warning(self, "Қате", msg)

    def _simulate_receive(self):
        names = ["Arman", "Aisulu", "Bakyt", "Damir"]; n = random.choice(names); a = random.randint(5000, 100000)
        self._service.db.top_up_balance(a)
        self._service.db.log_transaction(f"Перевод от {n}", a, "IN")
        self._service.db.add_notification("Кіріс аударым", f"{n} сізге {a:,} ₸ аударды", "SUCCESS")
        QMessageBox.information(self, "Kaspi.kz", f"{n}-дан {a:,} ₸ аударым келді!")
        self.payment_successful.emit()
