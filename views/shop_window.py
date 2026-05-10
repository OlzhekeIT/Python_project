# views/shop_window.py
from __future__ import annotations
from typing import Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QScrollArea, QFrame, QGridLayout, QGraphicsDropShadowEffect, QLineEdit,
    QMessageBox, QComboBox, QDialog, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPixmap
from services.shop_service import ShopService
from models.cart import Product

from services.localization_service import L

class ProductCard(QFrame):
    clicked = pyqtSignal(Product)
    fav_clicked = pyqtSignal(Product)
    def __init__(self, product: Product, on_add: Callable[[Product], None], parent: QWidget | None = None) -> None:
        super().__init__(parent); self._product = product; self.setObjectName("product_card_kaspi"); self.setFixedSize(250, 420); self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("#product_card_kaspi { background: white; border-radius: 12px; border: 1px solid #f0f0f0; } #product_card_kaspi:hover { border: 1px solid #0089d0; }")
        l = QVBoxLayout(self); l.setContentsMargins(15, 15, 15, 15); l.setSpacing(10)
        fh = QHBoxLayout(); fh.addStretch(); self.fav_btn = QPushButton("❤️" if getattr(product, 'is_favorite', False) else "🤍"); self.fav_btn.setFixedSize(32, 32); self.fav_btn.setStyleSheet("background: transparent; border: none; font-size: 20px;"); self.fav_btn.clicked.connect(lambda: self.fav_clicked.emit(product)); fh.addWidget(self.fav_btn); l.addLayout(fh)
        il = QLabel(); il.setFixedHeight(160); il.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if product.image_path: il.setPixmap(QPixmap(product.image_path).scaled(200, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else: il.setText("📦"); il.setStyleSheet("font-size: 50px; color: #d0d0d0;")
        l.addWidget(il); nl = QLabel(product.name); nl.setStyleSheet("font-size: 14px; color: #333; height: 40px;"); nl.setWordWrap(True); l.addWidget(nl)
        pl = QLabel(f"{product.price:,} ₸"); pl.setStyleSheet("font-size: 20px; font-weight: 800;"); l.addWidget(pl)
        rl = QLabel(f"Kaspi Red 0-0-3 • {int(product.price/3):,} ₸"); rl.setStyleSheet("font-size: 12px; color: #f14635; background: #fff5f5; padding: 4px; border-radius: 4px;"); l.addWidget(rl); l.addStretch()
        self.add_btn = QPushButton(L.tr("add_to_cart")); self.add_btn.setFixedHeight(40); self.add_btn.setStyleSheet("background: #00a260; color: white; border-radius: 8px; font-weight: 700;"); self.add_btn.clicked.connect(lambda: on_add(product)); l.addWidget(self.add_btn)
    def update_fav_icon(self, is_fav: bool): self.fav_btn.setText("❤️" if is_fav else "🤍")
    def mousePressEvent(self, e) -> None:
        if not self.add_btn.underMouse() and not self.fav_btn.underMouse(): self.clicked.emit(self._product)

class CartItemWidget(QFrame):
    quantity_changed = pyqtSignal(int, int)
    def __init__(self, product: Product, parent: QWidget | None = None) -> None:
        super().__init__(parent); self.setStyleSheet("background: #F8F9FB; border-radius: 12px; border: 1px solid #EDEDED;")
        l = QVBoxLayout(self); l.setContentsMargins(12, 12, 12, 12); l.setSpacing(10)
        top = QHBoxLayout(); top.setSpacing(10); img = QLabel(); img.setFixedSize(45, 45); img.setStyleSheet("background: white; border-radius: 6px;")
        if product.image_path: img.setPixmap(QPixmap(product.image_path).scaled(45, 45, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top.addWidget(img); info = QVBoxLayout(); info.setSpacing(2); name = QLabel(product.name); name.setStyleSheet("font-size: 13px; font-weight: 600;"); price = QLabel(f"{product.price:,} ₸"); price.setStyleSheet("font-size: 12px; color: #F14635; font-weight: 700;"); info.addWidget(name); info.addWidget(price); top.addLayout(info, stretch=1); l.addLayout(top)
        controls = QHBoxLayout(); controls.setSpacing(10); btn_s = "QPushButton { background: white; border: 1px solid #E5E7EB; border-radius: 6px; font-weight: 800; font-size: 16px; }"; m_btn = QPushButton("-"); m_btn.setFixedSize(30, 30); m_btn.setStyleSheet(btn_s); m_btn.clicked.connect(lambda: self.quantity_changed.emit(product.id, -1)); p_btn = QPushButton("+"); p_btn.setFixedSize(30, 30); p_btn.setStyleSheet(btn_s); p_btn.clicked.connect(lambda: self.quantity_changed.emit(product.id, 1)); qty_lbl = QLabel(str(getattr(product, 'quantity', 1))); qty_lbl.setStyleSheet("font-size: 15px; font-weight: 800; color: #1A1A1A;"); controls.addWidget(m_btn); controls.addWidget(qty_lbl); controls.addWidget(p_btn); controls.addStretch(); l.addLayout(controls)

class PromoBannerWidget(QFrame):
    def __init__(self):
        super().__init__(); self.setFixedHeight(180); self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F14635, stop:1 #FB7185); border-radius: 20px;")
        self.l = QVBoxLayout(self); self.l.setContentsMargins(40, 0, 40, 0); self.l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title = QLabel("Kaspi Red 0-0-3"); self.title.setStyleSheet("color: white; font-size: 28px; font-weight: 900;")
        self.desc = QLabel("Покупайте сейчас, платите потом"); self.desc.setStyleSheet("color: white; font-size: 16px; opacity: 0.9;")
        self.l.addWidget(self.title); self.l.addWidget(self.desc); self.banners = [("Kaspi Red 0-0-3", "Покупайте сейчас, платите потом", "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F14635, stop:1 #FB7185)"), ("Рассрочка 0-0-12", "Все товары до 12 месяцев", "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A1A1A, stop:1 #4B5563)")]
        self.idx = 0; self.timer = QTimer(self); self.timer.timeout.connect(self.next_banner); self.timer.start(5000)
    def next_banner(self): self.idx = (self.idx + 1) % len(self.banners); t, d, g = self.banners[self.idx]; self.title.setText(t); self.desc.setText(d); self.setStyleSheet(f"background: {g}; border-radius: 20px;")

class RecentItemWidget(QPushButton):
    selected = pyqtSignal(Product)
    def __init__(self, p: Product):
        super().__init__(); self.setCursor(Qt.CursorShape.PointingHandCursor); self.setStyleSheet("QPushButton { text-align: left; padding: 10px; border: none; border-radius: 10px; background: #F9FAFB; } QPushButton:hover { background: #F1F9FF; }")
        l = QHBoxLayout(self); l.setSpacing(10); l.setContentsMargins(5, 5, 5, 5); img = QLabel(); img.setFixedSize(40, 40); img.setStyleSheet("background: white; border-radius: 5px;")
        if p.image_path: img.setPixmap(QPixmap(p.image_path).scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        l.addWidget(img); name = QLabel(p.name); name.setStyleSheet("font-size: 12px; color: #4B5563;"); name.setWordWrap(True); l.addWidget(name, stretch=1); self.clicked.connect(lambda: self.selected.emit(p))

class CheckoutDialog(QDialog):
    def __init__(self, total_amt: int, service: ShopService, parent=None):
        super().__init__(parent); self._service = service; self._base_total = total_amt; self.discount_percent = 0
        self.setWindowTitle("Төлем"); self.setFixedSize(400, 520); self.setStyleSheet("background: white; border-radius: 20px;")
        l = QVBoxLayout(self); l.setContentsMargins(30, 30, 30, 30); l.setSpacing(20)
        self.total_lbl = QLabel(f"Жалпы: {total_amt:,} ₸", styleSheet="font-size: 22px; font-weight: 800; color: #1A1A1A;"); l.addWidget(self.total_lbl)
        ph = QHBoxLayout(); self.promo_in = QLineEdit(); self.promo_in.setPlaceholderText("Промокод (KASPI10)"); self.promo_in.setFixedHeight(45); self.promo_in.setStyleSheet("padding: 10px; border: 1px solid #E5E7EB; border-radius: 8px;"); pb = QPushButton("OK"); pb.setFixedSize(50, 45); pb.setStyleSheet("background: #1A1A1A; color: white; border-radius: 8px;"); pb.clicked.connect(self._check_promo); ph.addWidget(self.promo_in); ph.addWidget(pb); l.addLayout(ph)
        l.addWidget(QLabel("Төлем әдісін таңдаңыз", styleSheet="font-size: 16px; font-weight: 700; color: #1A1A1A;"))
        self.group = QButtonGroup(self); self.method_id = "gold"; methods = [("gold", "Kaspi Gold", "Төлем"), ("red", "Kaspi Red", "3 ай"), ("installments", "Рассрочка", "12 ай")]
        for mid, title, desc in methods:
            f = QFrame(); f.setStyleSheet("background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 12px;"); fv = QVBoxLayout(f); rb = QRadioButton(title); rb.setStyleSheet("font-weight:700;"); self.group.addButton(rb)
            if mid == "gold": rb.setChecked(True)
            rb.clicked.connect(lambda _, m=mid: setattr(self, 'method_id', m)); fv.addWidget(rb); fv.addWidget(QLabel(desc, styleSheet="color:#6B7280; margin-left:25px;")); l.addWidget(f)
        l.addStretch(); self.pay_btn = QPushButton("Төлеу"); self.pay_btn.setFixedHeight(55); self.pay_btn.setStyleSheet("background: #0089d0; color: white; border-radius: 12px; font-weight: 800;"); self.pay_btn.clicked.connect(self.accept); l.addWidget(self.pay_btn)
    def _check_promo(self):
        code = self.promo_in.text().strip(); disc = self._service.db.validate_promo(code)
        if disc > 0: self.discount_percent = disc; nt = int(self._base_total * (1 - disc / 100)); self.total_lbl.setText(f"Жалпы: <span style='text-decoration: line-through; color: #9CA3AF;'>{self._base_total:,}</span> <span style='color: #059669;'>{nt:,} ₸</span>"); self.promo_in.setDisabled(True); self.promo_in.setStyleSheet("background: #F0FDF4; border: 1px solid #BBF7D0; color: #166534; padding: 10px; border-radius: 8px;")
        else: QMessageBox.warning(self, "Қате", "Промокод қате")

class ShopWindow(QWidget):
    product_selected = pyqtSignal(Product)
    def __init__(self, service: ShopService, parent: QWidget | None = None) -> None:
        super().__init__(parent); self._service = service; self._search_query = ""; self._filter_val = "Все"; self._filter_type = "category"; self._sort_by = "default"
        self.setObjectName("shop_window"); self.init_ui(); L.lang_changed.connect(self._update_texts)

    def _update_texts(self):
        self.search_in.setPlaceholderText(L.tr("search_placeholder")); self.search_btn.setText(L.tr("search"))
        self.cart_title_lbl.setText(L.tr("cart")); self.checkout_btn.setText("Рәсімдеу"); self.recent_label.setText("Жақында қаралғандар"); self._refresh_cart(); self.refresh_recent(); self._render_categories()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        header = QFrame(); header.setFixedHeight(100); header.setStyleSheet("background: white; border-bottom: 1px solid #EDEDED;"); header_lay = QHBoxLayout(header); header_lay.setContentsMargins(40, 0, 40, 0); header_lay.setSpacing(15)
        sc = QFrame(); sc.setFixedHeight(50); sc.setFixedWidth(500); sc.setStyleSheet("background: #F8F9FB; border: 1px solid #E0E0E0; border-radius: 8px;"); sl = QHBoxLayout(sc); self.search_in = QLineEdit(); self.search_in.setPlaceholderText(L.tr("search_placeholder")); self.search_in.setFrame(False); sl.addWidget(self.search_in); self.search_btn = QPushButton(L.tr("search")); self.search_btn.setFixedSize(100, 50); self.search_btn.setStyleSheet("background: #0089d0; color: white; border-radius: 8px; font-weight: 700;"); self.search_btn.clicked.connect(self.refresh_products); header_lay.addWidget(sc); header_lay.addWidget(self.search_btn)
        self.sort_box = QComboBox(); self.sort_box.setFixedWidth(200); self.sort_box.setFixedHeight(50); self.sort_box.addItems(["Сначала дешевле", "Сначала дороже", "По рейтингу"]); self.sort_box.currentIndexChanged.connect(self._on_sort_changed); header_lay.addWidget(self.sort_box); header_lay.addStretch(); main_layout.addWidget(header)
        
        content = QHBoxLayout(); sidebar = QFrame(); sidebar.setFixedWidth(280); sidebar.setStyleSheet("background: white; border-right: 1px solid #EDEDED;"); self.side_lay = QVBoxLayout(sidebar); self.side_lay.setContentsMargins(30, 30, 30, 30); self.side_lay.setSpacing(15); 
        cat_title = QLabel("Категориялар"); cat_title.setStyleSheet("font-size:18px; font-weight:800; color:#1A1A1A;"); self.side_lay.addWidget(cat_title)
        self.cat_v = QVBoxLayout(); self.cat_v.setSpacing(10); self.side_lay.addLayout(self.cat_v)
        self._render_categories()
        
        pl = QHBoxLayout(); self.min_in = QLineEdit("от"); self.max_in = QLineEdit("до"); self.min_in.textChanged.connect(self.refresh_products); self.max_in.textChanged.connect(self.refresh_products); pl.addWidget(self.min_in); pl.addWidget(self.max_in); self.side_lay.addLayout(pl)
        self.recent_label = QLabel("Жақында қаралғандар", styleSheet="font-weight:800; font-size:14px; color:#1A1A1A;"); self.side_lay.addWidget(self.recent_label); self.recent_v = QVBoxLayout(); self.recent_v.setSpacing(8); self.side_lay.addLayout(self.recent_v); self.side_lay.addStretch(); content.addWidget(sidebar)
        grid_area = QWidget(); gl = QVBoxLayout(grid_area); gl.setContentsMargins(40, 40, 40, 0); gl.setSpacing(30); self.banner = PromoBannerWidget(); gl.addWidget(self.banner); scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setStyleSheet("background: #F8F9FB;"); scroll_content = QWidget(); self.grid_layout = QGridLayout(scroll_content); self.grid_layout.setSpacing(30); scroll.setWidget(scroll_content); gl.addWidget(scroll); content.addWidget(grid_area, stretch=1)
        self.cart_panel = QFrame(); self.cart_panel.setFixedWidth(340); self.cart_panel.setStyleSheet("background: white; border-left: 1px solid #EDEDED;"); cart_lay = QVBoxLayout(self.cart_panel); self.cart_title_lbl = QLabel(L.tr("cart"), objectName="shop_title"); cart_lay.addWidget(self.cart_title_lbl); self.cart_v = QVBoxLayout(); self.cart_v.addStretch(); cs = QScrollArea(); cs.setWidgetResizable(True); cw = QWidget(); cw.setLayout(self.cart_v); cs.setWidget(cw); cart_lay.addWidget(cs); self.cart_summary = QLabel(); self.cart_summary.setStyleSheet("font-size:16px; font-weight:700; border-top:1px solid #EEE; padding-top:10px;"); self.checkout_btn = QPushButton("Рәсімдеу"); self.checkout_btn.setFixedHeight(50); self.checkout_btn.setStyleSheet("background:#0089d0; color:white; border-radius:12px; font-weight:800;"); self.checkout_btn.clicked.connect(self._on_checkout); cart_lay.addWidget(self.cart_summary); cart_lay.addWidget(self.checkout_btn); content.addWidget(self.cart_panel); main_layout.addLayout(content); self.refresh_products(); self._refresh_cart(); self.refresh_recent()

    def _render_categories(self):
        while self.cat_v.count(): self.cat_v.takeAt(0).widget().deleteLater()
        self.cat_group = []
        cats = [("all_products", "Барлық"), ("Popular", "Танымал 🔥"), ("Смартфоны", "Смартфондар"), ("Ноутбуки", "Ноутбуктер"), ("Аксессуары", "Аксессуарлар"), ("Favorites", "Таңдаулылар ❤️")]
        for ru, kk in cats:
            name = kk if L.current_lang=="kk" else ru
            if ru == self._service.bonus_category: name += " (5% 🔥)"
            btn = QPushButton(name); btn.setCheckable(True); btn.setObjectName("cat_btn"); btn.clicked.connect(lambda _, r=ru: self._on_filter_clicked(r))
            if ru == self._filter_val: btn.setChecked(True)
            self.cat_v.addWidget(btn); self.cat_group.append(btn)

    def refresh_products(self) -> None:
        self._search_query = self.search_in.text(); min_p = int(self.min_in.text()) if self.min_in.text().isdigit() else 0; max_p = int(self.max_in.text()) if self.max_in.text().isdigit() else 9999999
        while self.grid_layout.count(): self.grid_layout.takeAt(0).widget().deleteLater()
        for i, p in enumerate(self._service.get_all_products(self._search_query, self._filter_val, self._filter_type, self._sort_by, min_p, max_p)):
            card = ProductCard(p, self._on_add_clicked); card.clicked.connect(self.product_selected.emit); card.fav_clicked.connect(self._on_fav_clicked); self.grid_layout.addWidget(card, i // 3, i % 3)

    def refresh_recent(self):
        while self.recent_v.count(): self.recent_v.takeAt(0).widget().deleteLater()
        for p in self._service.get_recent_products():
            w = RecentItemWidget(p); w.selected.connect(self.product_selected.emit); self.recent_v.addWidget(w)
    def _on_fav_clicked(self, p): is_fav = self._service.toggle_favorite(p.id); self.sender().update_fav_icon(is_fav)
    def _on_filter_clicked(self, v): self._filter_val = v; [b.setChecked(False) for b in self.cat_group]; self.sender().setChecked(True); self.refresh_products()
    def _on_sort_changed(self, i): self._sort_by = {0:"price_asc", 1:"price_desc", 2:"rating"}.get(i, "default"); self.refresh_products()
    def _on_add_clicked(self, p): self._service.add_to_cart(p); self._refresh_cart()
    def _refresh_cart(self):
        while self.cart_v.count() > 1:
            w = self.cart_v.takeAt(0).widget()
            if w: w.deleteLater()
        for i, p in enumerate(self._service.get_cart_items()):
            w = CartItemWidget(p); w.quantity_changed.connect(self._on_qty_changed)
            self.cart_v.insertWidget(i, w)
        self.cart_summary.setText(self._service.get_cart_text())
    def _on_qty_changed(self, pid: int, delta: int): self._service.update_cart_quantity(pid, delta); self._refresh_cart()
    def _on_checkout(self):
        items = self._service.get_cart_items()
        if not items: return
        d = CheckoutDialog(sum(i.price * i.quantity for i in items), self._service, self)
        if d.exec():
            ok, msg, tid = self._service.process_checkout(d.method_id, d.discount_percent)
            if ok: QMessageBox.information(self, "Kaspi.kz", msg); self._refresh_cart()
            else: QMessageBox.warning(self, "Қате", msg)
