# views/product_details_view.py
from __future__ import annotations
import numpy as np
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QScrollArea, QFrame, QLineEdit, QTextEdit, QFileDialog, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QLinearGradient, QFont
from models.cart import Product, Review

from services.localization_service import L

class RatingBar(QWidget):
    """Жұлдызшалар үлесін көрсететін прогресс-бар."""
    def __init__(self, star: int, percent: int, count: int):
        super().__init__()
        self.setFixedHeight(25)
        l = QHBoxLayout(self); l.setContentsMargins(0, 0, 0, 0); l.setSpacing(10)
        
        sl = QLabel(f"{star} ★"); sl.setFixedWidth(40); sl.setStyleSheet("color: #4B5563; font-weight: 700; font-size: 13px;")
        l.addWidget(sl)
        
        pb = QProgressBar(); pb.setMaximum(100); pb.setValue(percent); pb.setFixedHeight(8); pb.setTextVisible(False)
        pb.setStyleSheet("QProgressBar { background: #F3F4F6; border-radius: 4px; } QProgressBar::chunk { background: #FFC107; border-radius: 4px; }")
        l.addWidget(pb, stretch=1)
        
        cl = QLabel(str(count)); cl.setFixedWidth(30); cl.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        l.addWidget(cl)

class PriceTrendWidget(QWidget):
    def __init__(self, base_price: int, parent=None):
        super().__init__(parent); self.setMinimumHeight(120)
        np.random.seed(base_price % 100); changes = np.random.normal(0, base_price * 0.02, 30); self.history = base_price + np.cumsum(changes); self.min_price = int(np.min(self.history))
    def paintEvent(self, event):
        if len(self.history) < 2: return
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing); w = self.width(); h = self.height(); pad = 20; cw = w - 2*pad; ch = h - 2*pad
        mv = np.max(self.history); mn = np.min(self.history); diff = mv - mn if mv != mn else 1; points = []
        for i, v in enumerate(self.history): px = pad + i * (cw / (len(self.history) - 1)); py = h - pad - ((v - mn) / diff) * ch; points.append(QPoint(int(px), int(py)))
        grad = QLinearGradient(0, 0, 0, h); grad.setColorAt(0, QColor("#0089d030")); grad.setColorAt(1, QColor("#0089d000")); p.setBrush(grad); p.setPen(Qt.PenStyle.NoPen); poly = [QPoint(pad, h - pad)] + points + [QPoint(w - pad, h - pad)]; p.drawPolygon(poly)
        p.setPen(QPen(QColor("#0089d0"), 2))
        for i in range(len(points)-1): p.drawLine(points[i], points[i+1])

class RecommendationCard(QPushButton):
    selected = pyqtSignal(Product)
    def __init__(self, product: Product):
        super().__init__(); self.setFixedSize(180, 220); self.setCursor(Qt.CursorShape.PointingHandCursor); self.setStyleSheet("QPushButton { background: white; border: 1px solid #EDEDED; border-radius: 12px; } QPushButton:hover { border-color: #0089d0; }")
        l = QVBoxLayout(self); l.setContentsMargins(10, 10, 10, 10); l.setSpacing(5); img = QLabel(); img.setFixedSize(160, 100); img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if product.image_path: img.setPixmap(QPixmap(product.image_path).scaled(140, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else: img.setText("📦"); img.setStyleSheet("color: #d0d0d0; font-size: 30px;"); l.addWidget(img)
        l.addWidget(img); n = QLabel(product.name); n.setStyleSheet("font-size: 12px; font-weight: 600; color: #1A1A1A;"); n.setWordWrap(True); l.addWidget(n); p = QLabel(f"{product.price:,} ₸"); p.setStyleSheet("font-size: 14px; font-weight: 800; color: #1A1A1A;"); l.addWidget(p); l.addStretch(); self.clicked.connect(lambda: self.selected.emit(product))

class ReviewItemWidget(QFrame):
    def __init__(self, review: Review, parent: QWidget | None = None) -> None:
        super().__init__(parent); self.setObjectName("rev_item_kaspi"); self.setStyleSheet("background: white; border-bottom: 1px solid #EDEDED;")
        l = QVBoxLayout(self); l.setContentsMargins(0, 20, 0, 20); l.setSpacing(10); top = QHBoxLayout(); top.setSpacing(12); avatar = QLabel("👤"); avatar.setFixedSize(36, 36); avatar.setStyleSheet("background: #F8F9FB; border-radius: 18px; font-size: 18px;"); avatar.setAlignment(Qt.AlignmentFlag.AlignCenter); top.addWidget(avatar); ui = QVBoxLayout(); ui.setSpacing(2); name = QLabel(review.user); name.setStyleSheet("font-weight: 800; font-size: 14px; color: #1A1A1A;")
        sh = QHBoxLayout(); sh.setSpacing(2); r = getattr(review, 'rating', 5)
        for i in range(5): s = QLabel("★" if i < r else "☆"); s.setStyleSheet(f"color: {'#FFC107' if i < r else '#D1D5DB'}; font-size: 14px;"); sh.addWidget(s)
        sh.addStretch(); ui.addWidget(name); ui.addLayout(sh); top.addLayout(ui, stretch=1); date = QLabel(getattr(review, 'timestamp', "")); date.setStyleSheet("color: #9CA3AF; font-size: 12px;"); top.addWidget(date, alignment=Qt.AlignmentFlag.AlignTop); l.addLayout(top); text = QLabel(review.text); text.setWordWrap(True); text.setStyleSheet("font-size: 14px; line-height: 1.5; color: #374151;"); l.addWidget(text)
        if getattr(review, 'image_path', ""):
            img = QLabel(); pix = QPixmap(review.image_path)
            if not pix.isNull(): img.setPixmap(pix.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            l.addWidget(img)

class StarRatingSelector(QWidget):
    rating_changed = pyqtSignal(int)
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent); self._rating = 5; self.stars = []
        l = QHBoxLayout(self); l.setSpacing(5); l.setContentsMargins(0, 0, 0, 0)
        for i in range(1, 6):
            btn = QPushButton("★"); btn.setFixedSize(30, 30); btn.setCursor(Qt.CursorShape.PointingHandCursor); btn.setStyleSheet("border: none; background: transparent; font-size: 24px; color: #FFC107;"); btn.clicked.connect(lambda _, val=i: self.set_rating(val)); l.addWidget(btn); self.stars.append(btn)
        l.addStretch()
    def set_rating(self, val):
        self._rating = val
        for i, btn in enumerate(self.stars): btn.setStyleSheet(f"border: none; background: transparent; font-size: 24px; color: {'#FFC107' if i < val else '#D1D5DB'};")
        self.rating_changed.emit(val)
    def rating(self): return self._rating
    def reset(self): self.set_rating(5)

class ProductDetailsView(QWidget):
    back_clicked = pyqtSignal()
    review_submitted = pyqtSignal(str, Review)
    add_to_cart_clicked = pyqtSignal(Product)
    buy_gold_clicked = pyqtSignal(Product)
    buy_red_clicked = pyqtSignal(Product)
    buy_installments_clicked = pyqtSignal(Product)
    product_selected = pyqtSignal(Product)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent); self.setObjectName("details_view"); self._product = None; self._attached_img = ""; self.init_ui(); L.lang_changed.connect(self._update_texts)

    def _update_texts(self):
        self.back_btn.setText(L.tr("back"))
        if self._product: self.set_product(self._product, [])

    def init_ui(self) -> None:
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        header = QFrame(); header.setObjectName("details_header"); header.setFixedHeight(70); header.setStyleSheet("background: white; border-bottom: 1px solid #EDEDED;")
        h_lay = QHBoxLayout(header); h_lay.setContentsMargins(20, 0, 20, 0)
        self.back_btn = QPushButton(L.tr("back")); self.back_btn.setObjectName("close_btn"); self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor); self.back_btn.setStyleSheet("font-size: 16px; font-weight: 700; color: #1A1A1A; border: none; padding: 10px;"); self.back_btn.clicked.connect(self.back_clicked.emit)
        self.title_lbl = QLabel(L.tr("product_details")); self.title_lbl.setObjectName("header_title"); self.title_lbl.setStyleSheet("font-size: 18px; font-weight: 800;")
        h_lay.addWidget(self.back_btn); h_lay.addStretch(); h_lay.addWidget(self.title_lbl); h_lay.addStretch(); dummy = QWidget(); dummy.setFixedWidth(80); h_lay.addWidget(dummy); layout.addWidget(header)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setStyleSheet("background: #F8F9FB;")
        self.content = QWidget(); self.cl = QVBoxLayout(self.content); self.cl.setContentsMargins(40, 20, 40, 40); self.cl.setSpacing(30); scroll.setWidget(self.content); layout.addWidget(scroll)

    def set_product(self, product: Product, recommendations: list[Product] = []) -> None:
        self._product = product; self._attached_img = ""
        def clear_layout(layout):
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0); widget = item.widget()
                    if widget is not None: widget.deleteLater()
                    else:
                        sub_layout = item.layout()
                        if sub_layout: clear_layout(sub_layout)
        clear_layout(self.cl)

        top_container = QWidget(); top = QHBoxLayout(top_container); top.setSpacing(50); top.setContentsMargins(0,0,0,0)
        img_c = QFrame(); img_c.setObjectName("img_container"); img_c.setStyleSheet("#img_container { background: white; border-radius: 24px; border: 1px solid #EDEDED; }")
        img_l = QVBoxLayout(img_c); img = QLabel(); pix = QPixmap(product.image_path)
        if not pix.isNull(): img.setPixmap(pix.scaled(400, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        img.setAlignment(Qt.AlignmentFlag.AlignCenter); img_l.addWidget(img); top.addWidget(img_c, stretch=1)

        buy = QFrame(); buy.setObjectName("buy_card"); bv = QVBoxLayout(buy); buy.setFixedWidth(400); bv.setContentsMargins(30, 30, 30, 30); bv.setSpacing(15); buy.setStyleSheet("#buy_card { background: white; border-radius: 24px; border: 1px solid #EDEDED; }")
        bv.addWidget(QLabel(product.name, styleSheet="font-size: 20px; font-weight: 800; color: #1A1A1A;"))
        
        # --- Enhanced Rating ---
        revs = product.reviews; ratings = [r.rating for r in revs] if revs else []
        avg = np.mean(ratings) if ratings else 5.0
        rat_h = QHBoxLayout(); rat_h.setSpacing(5)
        for i in range(5):
            s = QLabel("★"); s.setStyleSheet(f"color: {'#FFC107' if i < int(avg) else '#D1D5DB'}; font-size: 16px;"); rat_h.addWidget(s)
        rat_h.addWidget(QLabel(f"<b>{avg:.1f}</b> ({len(revs)} пікір)", styleSheet="color: #4B5563; font-size: 14px;")); rat_h.addStretch(); bv.addLayout(rat_h)
        bv.addWidget(QLabel(f"{product.price:,}".replace(",", " ") + " ₸", objectName="big_price"))
        
        iv = QVBoxLayout(); inst_f = QFrame(); inst_f.setStyleSheet("background: #FFF9F9; border: 1px solid #FFEDED; border-radius: 12px;"); iv = QVBoxLayout(inst_f); iv.setContentsMargins(15,15,15,15); iv.addWidget(QLabel(f"<b>{L.tr('installments_prefix')}</b>", styleSheet="color: #F14635; font-size: 14px;")); iv.addWidget(QLabel(f"{int(product.price/12):,} ₸ / мес", styleSheet="color: #F14635; font-size: 18px; font-weight: 900;")); bv.addWidget(inst_f)
        red_p = QLabel(f"Kaspi Red 0-0-3\n3 айға {int(product.price/3):,} ₸-ден"); red_p.setStyleSheet("background: #F14635; color: white; border-radius: 8px; padding: 10px; font-weight: 700;"); bv.addWidget(red_p)
        bv.addSpacing(10); inst_btn = QPushButton(L.tr("buy_installments")); inst_btn.setFixedHeight(55); inst_btn.setStyleSheet("background: #F14635; font-size: 16px;"); inst_btn.clicked.connect(lambda: self.buy_installments_clicked.emit(product)); bv.addWidget(inst_btn)

        buy_h = QHBoxLayout(); buy_h.setSpacing(10); gb = QPushButton(L.tr("buy_gold")); gb.setFixedHeight(50); gb.setStyleSheet("background: #1A1A1A; color: white; border-radius: 12px; font-weight: 700;"); gb.clicked.connect(lambda: self.buy_gold_clicked.emit(product)); rb = QPushButton("Red"); rb.setFixedHeight(50); rb.setFixedWidth(80); rb.setStyleSheet("background: white; border: 2px solid #F14635; color: #F14635; border-radius: 12px; font-weight: 700;"); rb.clicked.connect(lambda: self.buy_red_clicked.emit(product)); buy_h.addWidget(gb, stretch=1); buy_h.addWidget(rb); bv.addLayout(buy_h)
        cb = QPushButton(L.tr("add_to_cart")); cb.setFixedHeight(50); cb.setStyleSheet("background: #F5F5F5; color: #1A1A1A; border: none;"); cb.clicked.connect(lambda: self.add_to_cart_clicked.emit(product)); bv.addWidget(cb); bv.addStretch(); top.addWidget(buy); self.cl.addWidget(top_container)

        # --- Rating Distribution ---
        rd_f = QFrame(); rd_f.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #EDEDED; padding: 25px;")
        rl = QVBoxLayout(rd_f); rl.addWidget(QLabel("Бағалар үлесі" if L.current_lang=="kk" else "Распределение оценок", styleSheet="font-size: 18px; font-weight: 800;"))
        
        # NumPy Calculation
        counts = [0] * 5
        if ratings:
            u, c = np.unique(ratings, return_counts=True)
            for val, count in zip(u, c):
                if 1 <= val <= 5: counts[val-1] = count
        
        total = len(ratings) if ratings else 1
        for i in range(5, 0, -1):
            rl.addWidget(RatingBar(i, int(counts[i-1]/total*100), counts[i-1]))
        self.cl.addWidget(rd_f)

        # Price Dynamics
        pdf = QFrame(); pdf.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #EDEDED; padding: 25px;"); pl = QVBoxLayout(pdf); pl.addWidget(QLabel("Динамика цены", styleSheet="font-size: 18px; font-weight: 800;")); chart = PriceTrendWidget(product.price); pl.addWidget(chart); self.cl.addWidget(pdf)

        if product.specs:
            sl = QLabel("Сипаттамалары"); sl.setStyleSheet("font-size: 22px; font-weight: 900;"); self.cl.addWidget(sl)
            sf = QFrame(); sv = QVBoxLayout(sf); sf.setStyleSheet("background: white; border-radius: 16px; border: 1px solid #EDEDED;")
            for k, v in product.specs.items():
                row = QHBoxLayout(); row.addWidget(QLabel(k, styleSheet="color:#6B7280;")); row.addStretch(); row.addWidget(QLabel(v, styleSheet="font-weight:600;")); sv.addLayout(row); ln = QFrame(); ln.setFixedHeight(1); ln.setStyleSheet("background:#F3F4F6;"); sv.addWidget(ln)
            self.cl.addWidget(sf)

        if recommendations:
            self.cl.addWidget(QLabel("Сізге тағы не ұнауы мүмкін", styleSheet="font-size: 22px; font-weight: 900;"))
            rh = QHBoxLayout(); rh.setSpacing(15)
            for rp in recommendations:
                w = RecommendationCard(rp); w.selected.connect(self.product_selected.emit); rh.addWidget(w)
            rh.addStretch(); self.cl.addLayout(rh)

        self.cl.addWidget(QLabel("Пікірлер", styleSheet="font-size: 22px; font-weight: 900;"))
        rf = QFrame(); rv = QVBoxLayout(rf); rf.setStyleSheet("background: white; border-radius: 16px; border: 1px solid #EDEDED; padding: 20px;")
        rv.addWidget(QLabel("Пікір қалдырыңыз", styleSheet="font-weight: 700;")); self.star_sel = StarRatingSelector(); rv.addWidget(self.star_sel); self.review_in = QTextEdit(); self.review_in.setPlaceholderText("Ойыңызды жазыңыз..."); self.review_in.setFixedHeight(80); rv.addWidget(self.review_in); self.submit_btn = QPushButton("Жіберу"); self.submit_btn.setStyleSheet("background: #1A1A1A; color: white; border-radius: 8px; font-weight: 700;"); self.submit_btn.clicked.connect(self._on_submit_review); rv.addWidget(self.submit_btn); self.cl.addWidget(rf)
        if not product.reviews: self.cl.addWidget(QLabel("Әлі пікірлер жоқ", styleSheet="color:#9CA3AF;"))
        else:
            for r in product.reviews: self.cl.addWidget(ReviewItemWidget(r))
        self.cl.addStretch()

    def _on_attach_img(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if f: self._attached_img = f
    def _on_submit_review(self):
        t = self.review_in.toPlainText().strip()
        if t and self._product:
            r = Review("Диас", self.star_sel.rating(), t); r.image_path = self._attached_img; r.timestamp = datetime.now().strftime("%d.%m.%Y %H:%M"); self.review_submitted.emit(self._product.name, r); self.review_in.clear(); self.star_sel.reset()
