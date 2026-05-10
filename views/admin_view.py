# views/admin_view.py
from __future__ import annotations
import json
import numpy as np
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt
from services.shop_service import ShopService
from services.localization_service import L
from views.base_view import BaseView
from views.analytics_view import BarChartWidget

class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle(L.tr("admin_login_title")); self.setFixedSize(350, 220); self.setStyleSheet("background: white; border-radius: 16px;")
        l = QVBoxLayout(self); l.setContentsMargins(30, 30, 30, 30); l.setSpacing(15); l.addWidget(QLabel(L.tr("admin_pass_placeholder")+":", styleSheet="font-weight:700; color:#1A1A1A;"))
        self.pass_in = QLineEdit(); self.pass_in.setEchoMode(QLineEdit.EchoMode.Password); self.pass_in.setFixedHeight(50); self.pass_in.setStyleSheet("padding:10px 15px; border:1.5px solid #E5E7EB; border-radius:10px; font-size:16px;"); l.addWidget(self.pass_in)
        self.btn = QPushButton(L.tr("admin_login_btn")); self.btn.setFixedHeight(50); self.btn.setStyleSheet("background: #1A1A1A; color: white; border-radius: 10px; font-weight: 800;"); self.btn.clicked.connect(self.accept); l.addWidget(self.btn)

class AdminDashboard(QWidget):
    def __init__(self, service: ShopService):
        super().__init__(); self._service = service; self.l = QVBoxLayout(self); self.refresh()
    def refresh(self):
        while self.l.count():
            w = self.l.takeAt(0).widget()
            if w: w.deleteLater()
        data = self._service.db.get_sales_data()
        if not data: self.l.addWidget(QLabel("Нет данных", alignment=Qt.AlignmentFlag.AlignCenter)); return
        prices = np.array([d['price'] for d in data]); h = QHBoxLayout(); h.setSpacing(20)
        def card(t, v, c):
            f = QFrame(); f.setStyleSheet(f"background:white; border-radius:16px; border:1px solid #EDEDED; padding:20px;")
            vl = QVBoxLayout(f); vl.addWidget(QLabel(t, styleSheet="color:#757575; font-size:13px;")); vl.addWidget(QLabel(v, styleSheet=f"color:{c}; font-size:22px; font-weight:900;")); return f
        h.addWidget(card("Общая выручка", f"{np.sum(prices):,} ₸", "#059669"))
        names = [d['p_name'] for d in data]; u, c = np.unique(names, return_counts=True); h.addWidget(card("Топ продаж", str(u[np.argmax(c)]), "#1A1A1A")); self.l.addLayout(h)
        cats = [d['category'] for d in data]; uc, cc = np.unique(cats, return_counts=True); chart_data = {str(cat): float(count) for cat, count in zip(uc, cc)}
        f = QFrame(); f.setStyleSheet("background:white; border-radius:20px; border:1px solid #EDEDED; padding:25px;"); cl = QVBoxLayout(f); cl.addWidget(QLabel("Продажи по категориям", styleSheet="font-weight:800; font-size:18px;"))
        cl.addWidget(BarChartWidget(chart_data)); self.l.addWidget(f); self.l.addStretch()

class AdminView(BaseView):
    def __init__(self, service: ShopService, parent: QWidget | None = None) -> None:
        self._service = service; self._search_query = ""
        super().__init__(parent); self.setObjectName("admin_view"); self.refresh_all()

    def update_localization(self): self.set_title(L.tr("admin")); self.refresh_all()

    def refresh_all(self):
        self.set_title(L.tr("admin")); self.clear_layout(self._content_layout)
        self.tabs = QTabWidget(); self.tabs.setStyleSheet("QTabWidget::pane { border:1px solid #EDEDED; border-radius:12px; background:white; } QTabBar::tab { background:#F8F9FB; padding:12px 30px; font-weight:700; } QTabBar::tab:selected { background:white; color:#0089d0; }")
        
        p_tab = QWidget(); pl = QVBoxLayout(p_tab); pl.setContentsMargins(30, 30, 30, 30); pl.setSpacing(20)
        
        # Form
        form = QFrame(); form.setStyleSheet("background:#F9FAFB; border-radius:16px; border:1px solid #E5E7EB;"); fv = QVBoxLayout(form); fv.setContentsMargins(20, 20, 20, 20); fv.setSpacing(12)
        self.name_in = QLineEdit(); self.name_in.setPlaceholderText(L.tr("admin_name_ph")); self.price_in = QLineEdit(); self.price_in.setPlaceholderText(L.tr("admin_price_ph"))
        self.brand_in = QLineEdit(); self.brand_in.setPlaceholderText(L.tr("admin_brand_ph")); self.cat_box = QComboBox(); self.cat_box.addItems(["Смартфоны", "Ноутбуки", "Аксессуары"])
        h1 = QHBoxLayout(); h1.addWidget(self.name_in, 2); h1.addWidget(self.price_in, 1); fv.addLayout(h1); h2 = QHBoxLayout(); h2.addWidget(self.brand_in, 1); h2.addWidget(self.cat_box, 1); fv.addLayout(h2)
        self.add_btn = QPushButton(L.tr("admin_add_btn")); self.add_btn.setFixedHeight(45); self.add_btn.setStyleSheet("background:#00a260; color:white; font-weight:800;"); self.add_btn.clicked.connect(self._add_product); fv.addWidget(self.add_btn); pl.addWidget(form)
        
        # Demo Button
        demo_btn = QPushButton("🚀 Генерация Демо-данных (для презентации)"); demo_btn.setFixedHeight(45); demo_btn.setStyleSheet("background: #1A1A1A; color: white; border-radius: 12px; font-weight: 700;")
        demo_btn.clicked.connect(self._generate_demo_data); pl.addWidget(demo_btn)
        
        # Search for table
        sh = QHBoxLayout(); self.table_search = QLineEdit(); self.table_search.setPlaceholderText("Поиск товаров..."); self.table_search.setFixedHeight(40); self.table_search.setStyleSheet("padding:5px 15px; border:1px solid #E5E7EB; border-radius:10px;")
        self.table_search.textChanged.connect(self._on_table_search); sh.addWidget(self.table_search); pl.addLayout(sh)
        
        self.table = QTableWidget(); self.table.setColumnCount(5); self.table.setHorizontalHeaderLabels(["ID", "Название", "Цена", "Категория", "Действие"]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); pl.addWidget(self.table)
        
        self.dash = AdminDashboard(self._service)
        self.tabs.addTab(p_tab, "Товары"); self.tabs.addTab(self.dash, "Аналитика")
        self._content_layout.addWidget(self.tabs); self.refresh_table()

    def _on_table_search(self, t): self._search_query = t; self.refresh_table()

    def refresh_table(self):
        prods = self._service.get_all_products(search=self._search_query, filter_val="Все")
        self.table.setRowCount(len(prods))
        for i, p in enumerate(prods):
            self.table.setItem(i, 0, QTableWidgetItem(str(p.id))); self.table.setItem(i, 1, QTableWidgetItem(p.name))
            self.table.setItem(i, 2, QTableWidgetItem(f"{p.price:,} ₸")); self.table.setItem(i, 3, QTableWidgetItem(p.category))
            db = QPushButton(L.tr("admin_delete")); db.setStyleSheet("background:#FEEBEA; color:#F14635; font-weight:700;"); db.clicked.connect(lambda _, pid=p.id: (self._service.db.delete_product(pid), self.refresh_table())); self.table.setCellWidget(i, 4, db)

    def _add_product(self):
        n = self.name_in.text(); p = self.price_in.text(); b = self.brand_in.text(); c = self.cat_box.currentText()
        if n and p.isdigit(): self._service.db.add_product(n, int(p), b, "", "{}", c); self.refresh_table(); self.name_in.clear(); self.price_in.clear(); self.brand_in.clear(); QMessageBox.information(self, "OK", "ОК")

    def _generate_demo_data(self):
        reply = QMessageBox.question(self, "Demo", "Бұл барлық қазіргі деректерді өшіріп, жаңа демо-деректер жасайды. Жалғастырамыз ба?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db = self._service.db
            # Clear tables
            db._execute("DELETE FROM transactions"); db._execute("DELETE FROM sales"); db._execute("DELETE FROM reviews")
            db._execute("UPDATE user_account SET balance = 1500000, deposit_balance = 500000, bonuses = 12500 WHERE id = 1")
            
            # Generate 50 transactions using NumPy
            np.random.seed(42)
            titles = ["Покупка: Magnum", "Перевод Арману", "Starbucks", "Аптека", "Invictus Fitness", "Доставка еды", "Төлем: Коммуналдық", "Қайырымдылық"]
            categories = ["Gold", "Red", "Inst", "Gold", "Gold", "Gold", "Gold", "Gold"]
            
            for i in range(50):
                title = np.random.choice(titles); amt = -int(np.random.uniform(500, 25000)); t_type = np.random.choice(["OUT", "RED", "INST"])
                # Custom dates over last 30 days
                date = (datetime.now() - timedelta(days=int(np.random.uniform(0, 30)))).strftime("%d.%m.%Y %H:%M")
                db._execute("INSERT INTO transactions (title, amount, type, timestamp) VALUES (?, ?, ?, ?)", (f"{categories[titles.index(title)]}: {title}", amt, t_type, date))
                # Log some sales for BI dashboard
                db.log_sale(1, title, abs(amt), "Смартфоны" if i % 3 == 0 else "Ноутбуки")
            
            QMessageBox.information(self, "OK", "Демо-деректер сәтті жасалды! Енді Аналитика бөлімін тексеріп көріңіз.")
            self.refresh_all()
