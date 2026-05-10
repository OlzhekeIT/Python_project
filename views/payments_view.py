# views/payments_view.py
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QLineEdit, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt
from services.shop_service import ShopService
from services.localization_service import L
from views.base_view import BaseView

class PaymentsView(BaseView):
    def __init__(self, service: ShopService, parent: QWidget | None = None) -> None:
        self._service = service
        self._search_query = ""
        super().__init__(parent)
        self.setObjectName("payments_view")
        self._current_category_ru = ""
        self.refresh_ui()

    def update_localization(self):
        self.refresh_ui()

    def refresh_ui(self) -> None:
        self.set_title(L.tr("payments"))
        self.clear_layout(self._content_layout)
        
        # Search Bar for categories
        search_c = QFrame(); search_c.setFixedHeight(50); search_c.setStyleSheet("background: white; border: 1px solid #E5E7EB; border-radius: 12px;")
        sl = QHBoxLayout(search_c); sl.setContentsMargins(15, 0, 15, 0)
        self.search_in = QLineEdit(); self.search_in.setPlaceholderText("Поиск услуг..." if L.current_lang=="ru" else "Қызметтерді іздеу...")
        self.search_in.setFrame(False); self.search_in.textChanged.connect(self._on_search_changed)
        sl.addWidget(self.search_in); self._content_layout.addWidget(search_c)
        
        # Grid of categories
        self.grid_widget = QWidget(); self.grid = QGridLayout(self.grid_widget); self.grid.setSpacing(20); self.grid.setContentsMargins(0,0,0,0)
        self._render_grid()
        self._content_layout.addWidget(self.grid_widget)
        
        # Hidden Form
        self.form_frame = QFrame(); self.form_frame.setObjectName("info_section"); self.form_frame.setVisible(False)
        self.form_frame.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #EDEDED;")
        fv = QVBoxLayout(self.form_frame); fv.setContentsMargins(35, 35, 35, 35); fv.setSpacing(20)
        self.form_title = QLabel("", styleSheet="font-size: 20px; font-weight: 800; color: #111827;"); fv.addWidget(self.form_title)
        style = "padding: 15px; border: 1px solid #E5E7EB; border-radius: 12px; font-size: 16px; background: #F9FAFB;"
        self.account_in = QLineEdit(); self.account_in.setStyleSheet(style); fv.addWidget(self.account_in)
        self.amount_in = QLineEdit(); self.amount_in.setPlaceholderText(L.tr("amount")); self.amount_in.setStyleSheet(style); fv.addWidget(self.amount_in)
        pb = QPushButton(L.tr("pay")); pb.setFixedHeight(55); pb.setStyleSheet("background: #f14635; color: white; border-radius: 12px; font-weight: 800;"); pb.clicked.connect(self._process_payment)
        fv.addWidget(pb); self._content_layout.addWidget(self.form_frame)
        self._content_layout.addStretch()

    def _render_grid(self):
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w: w.deleteLater()
            
        all_cats = [
            ("📱", "Мобильная связь", "Ұялы байланыс"),
            ("🏠", "Коммуналка", "Коммуналдық қызметтер"),
            ("🌐", "Интернет и ТВ", "Интернет және ТВ"),
            ("🎓", "Образование", "Білім"),
            ("🚗", "Штрафы и налоги", "Айыппұлдар мен салықтар"),
            ("🏥", "Медицина", "Медицина"),
        ]
        
        filtered = [c for c in all_cats if self._search_query.lower() in c[1].lower() or self._search_query.lower() in c[2].lower()]
        
        for i, (icon, ru, kk) in enumerate(filtered):
            btn = QPushButton(); btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("QPushButton { background: white; border: 1px solid #EDEDED; border-radius: 16px; } QPushButton:hover { border-color: #0089d0; }")
            bl = QVBoxLayout(btn); bl.setContentsMargins(20, 25, 20, 25); bl.setSpacing(12)
            il = QLabel(icon); il.setStyleSheet("font-size: 36px; color: #1A1A1A; background: transparent; border: none;"); il.setAlignment(Qt.AlignmentFlag.AlignCenter); bl.addWidget(il)
            title = ru if L.current_lang == "ru" else kk
            tl = QLabel(title); tl.setStyleSheet("font-size: 14px; font-weight: 700; color: #1A1A1A; background: transparent; border: none;"); tl.setAlignment(Qt.AlignmentFlag.AlignCenter); tl.setWordWrap(True); bl.addWidget(tl)
            btn.clicked.connect(lambda _, r=ru: self._open_payment_form(r))
            self.grid.addWidget(btn, i // 3, i % 3)

    def _on_search_changed(self, text):
        self._search_query = text; self._render_grid()

    def _open_payment_form(self, category_ru: str):
        self._current_category_ru = category_ru
        disp = category_ru
        if L.current_lang == "kk":
            m = {"Мобильная связь": "Ұялы байланыс", "Коммуналка": "Коммуналдық қызметтер", "Интернет и ТВ": "Интернет және ТВ", "Образование": "Білім", "Штрафы и налоги": "Айыппұлдар мен салықтар", "Медицина": "Медицина"}
            disp = m.get(category_ru, category_ru)
        self.form_title.setText(f"{L.tr('pay')}: {disp}")
        self.account_in.setPlaceholderText(L.tr("recipient")); self.account_in.clear(); self.amount_in.clear(); self.form_frame.setVisible(True)

    def _process_payment(self):
        acc = self.account_in.text(); amt = self.amount_in.text()
        if not acc or not amt.isdigit(): QMessageBox.warning(self, "Қате", "Мәліметтерді дұрыс енгізіңіз"); return
        ok, msg = self._service.db.process_general_payment(int(amt), self._current_category_ru)
        if ok: QMessageBox.information(self, "Kaspi.kz", msg); self.form_frame.setVisible(False)
        else: QMessageBox.warning(self, "Қате", msg)
