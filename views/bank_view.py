# views/bank_view.py
from __future__ import annotations
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QProgressBar, QPushButton, QMessageBox, QInputDialog, QLineEdit, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen
from services.shop_service import ShopService
from services.localization_service import L
from views.base_view import BaseView

class CurrencyRatesWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #EDEDED;")
        l = QVBoxLayout(self); l.setContentsMargins(25, 25, 25, 25); l.setSpacing(15)
        l.addWidget(QLabel(L.tr("currency_rates"), styleSheet="font-weight: 800; font-size: 16px; color: #1A1A1A;"))
        
        # NumPy Simulation
        currencies = [("🇺🇸 USD", 445), ("🇪🇺 EUR", 485), ("🇷🇺 RUB", 4.8)]
        for name, base in currencies:
            rate = base + np.random.normal(0, base * 0.005)
            row = QHBoxLayout()
            row.addWidget(QLabel(name, styleSheet="font-weight: 700; color: #4B5563;"))
            row.addStretch()
            
            # Buy / Sell simulation
            buy = rate * 0.99
            sell = rate * 1.01
            
            row.addWidget(QLabel(f"{buy:.2f}", styleSheet="color: #1A1A1A; font-weight: 800;"))
            row.addWidget(QLabel(f"{sell:.2f}", styleSheet="color: #1A1A1A; font-weight: 800;"))
            
            trend = "▲" if np.random.random() > 0.5 else "▼"
            t_color = "#059669" if trend == "▲" else "#F14635"
            row.addWidget(QLabel(trend, styleSheet=f"color: {t_color}; font-weight: 900;"))
            l.addLayout(row)

class SparklineWidget(QWidget):
    def __init__(self, history: list[float], parent=None):
        super().__init__(parent); self.history = history; self.setFixedSize(120, 40)
    def paintEvent(self, event):
        if len(self.history) < 2: return
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width(); h = self.height(); pad = 5; cw = w - 2*pad; ch = h - 2*pad
        vals = np.array(self.history); mv = np.max(vals); mn = np.min(vals); diff = mv - mn if mv != mn else 1
        points = []
        for i, v in enumerate(vals):
            px = pad + i * (cw / (len(vals) - 1)); py = h - pad - ((v - mn) / diff) * ch; points.append(QPoint(int(px), int(py)))
        p.setPen(QPen(QColor(255, 255, 255, 180), 2))
        for i in range(len(points)-1): p.drawLine(points[i], points[i+1])

class ReceiptDialog(QDialog):
    def __init__(self, t: dict, parent=None):
        super().__init__(parent); self.setWindowTitle("Чек"); self.setFixedSize(380, 500); self.setStyleSheet("background: white; border-radius: 20px;")
        l = QVBoxLayout(self); l.setContentsMargins(30, 30, 30, 30); l.setSpacing(15)
        h = QLabel("Kaspi.kz"); h.setStyleSheet("font-size: 24px; font-weight: 900; color: #F14635;"); h.setAlignment(Qt.AlignmentFlag.AlignCenter); l.addWidget(h)
        l.addWidget(QLabel("Квитанция об операции", styleSheet="color: #6B7280; font-size: 14px;"), alignment=Qt.AlignmentFlag.AlignCenter)
        def row(t, v, b=False):
            h = QHBoxLayout(); h.addWidget(QLabel(t, styleSheet="color:#6B7280;")); h.addStretch(); h.addWidget(QLabel(v, styleSheet=f"font-weight:{'800' if b else '600'}; color:#1A1A1A;")); return h
        l.addLayout(row("Статус:", "Успешно", True)); l.addLayout(row("Дата:", t['timestamp'])); l.addLayout(row("Операция:", t['title']))
        l.addLayout(row("Сумма:", f"{t['amount']:,} ₸", True)); l.addLayout(row("Номер:", f"TX-{t['id']:06d}")); l.addStretch()
        sb = QPushButton("📄 Сақтау"); sb.setFixedHeight(50); sb.setStyleSheet("background:#F3F4F6; border-radius:12px; font-weight:700;"); sb.clicked.connect(lambda: self._save(t)); l.addWidget(sb)
        cb = QPushButton("Жабу"); cb.setFixedHeight(50); cb.setStyleSheet("background:#1A1A1A; color:white; border-radius:12px; font-weight:700;"); cb.clicked.connect(self.accept); l.addWidget(cb)
    def _save(self, t):
        p = f"receipt_{t['id']}.txt"; open(p, "w", encoding="utf-8").write(f"TX-{t['id']}\n{t['title']}\n{t['amount']} ₸"); QMessageBox.information(self, "OK", f"Saved: {p}")

class TransactionItemWidget(QPushButton):
    def __init__(self, t: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent); self.setCursor(Qt.CursorShape.PointingHandCursor); self.setStyleSheet("QPushButton { background: white; border-radius: 12px; border: 1px solid #EDEDED; text-align: left; } QPushButton:hover { border-color: #0089d0; }")
        l = QHBoxLayout(self); l.setContentsMargins(15, 12, 15, 12); l.setSpacing(15)
        icon = "💰" if t['amount'] > 0 else "🛍️"; il = QLabel(icon); il.setStyleSheet("font-size: 20px; background: #F8F9FB; border-radius: 10px; padding: 5px;"); l.addWidget(il)
        info = QVBoxLayout(); info.setSpacing(2); tl = QLabel(t['title']); tl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1A1A1A;"); ts = QLabel(t['timestamp']); ts.setStyleSheet("font-size: 12px; color: #757575;"); info.addWidget(tl); info.addWidget(ts); l.addLayout(info, stretch=1)
        as_ = f"{t['amount']:,} ₸"; al = QLabel(("+" if t['amount'] > 0 else "") + as_); color = "#059669" if t['amount'] > 0 else "#1A1A1A"; al.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {color};"); l.addWidget(al)

class BankView(BaseView):
    def __init__(self, service: ShopService, parent: QWidget | None = None) -> None:
        self._service = service; self._history_query = ""; super().__init__(parent); self.setObjectName("bank_view"); self.refresh_data()
    def update_localization(self): self.set_title(L.tr("bank")); self.refresh_data()
    def refresh_data(self):
        self.set_title(L.tr("bank")); self.clear_layout(self._content_layout)
        ud = self._service.db.get_user_data(); txs = self._service.db.get_all_transactions()
        
        acc_h = QHBoxLayout(); acc_h.setSpacing(20)
        # Gold Card
        card = QFrame(); card.setObjectName("bank_card"); card.setFixedSize(420, 240); card.setStyleSheet("#bank_card { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F14635, stop:1 #C62828); border-radius: 24px; border: none; }")
        cvc = QVBoxLayout(card); cvc.setContentsMargins(35, 30, 35, 30); cvc.setSpacing(15)
        
        top = QHBoxLayout()
        gold_title = QLabel("Kaspi Gold")
        gold_title.setStyleSheet("color: white; font-size: 24px; font-weight: 900; background: transparent; border: none;")
        top.addWidget(gold_title)
        top.addStretch()
        
        chip = QFrame(); chip.setFixedSize(55, 40); chip.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFD700, stop:1 #FFA000); border-radius:8px; border: none;")
        top.addWidget(chip); cvc.addLayout(top); cvc.addStretch()
        
        mid = QHBoxLayout()
        balance_lbl = QLabel(f"{ud['balance']:,} ₸".replace(","," "))
        balance_lbl.setStyleSheet("color: white; font-size: 42px; font-weight: 1000; background: transparent; border: none;")
        mid.addWidget(balance_lbl)
        mid.addStretch()
        
        if len(txs) >= 2:
            bal = ud['balance']; hist = [bal]
            for t in txs[:10]: bal -= t['amount']; hist.insert(0, bal)
            mid.addWidget(SparklineWidget(hist))
        cvc.addLayout(mid)
        
        actions = QHBoxLayout()
        tb = QPushButton(L.tr("top_up"))
        tb.setStyleSheet("background: rgba(255,255,255,0.25); color: white; border-radius: 12px; font-weight: 800; border: none; padding: 10px 20px;")
        tb.clicked.connect(self._on_top_up); actions.addWidget(tb)
        
        dep_btn = QPushButton("На Депозит")
        dep_btn.setStyleSheet("background: rgba(255,255,255,0.25); color: white; border-radius: 12px; font-weight: 800; border: none; padding: 10px 20px;")
        dep_btn.clicked.connect(self._on_move_to_deposit); actions.addWidget(dep_btn)
        actions.addStretch(); cvc.addLayout(actions)
        
        card_num = QLabel("•••• 4455")
        card_num.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 14px; background: transparent; border: none;")
        cvc.addWidget(card_num); acc_h.addWidget(card)

        # Deposit Card
        dcard = QFrame(); dcard.setObjectName("bank_card"); dcard.setFixedSize(420, 240); dcard.setStyleSheet("#bank_card { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1A1A1A, stop:1 #4B5563); border-radius: 24px; border: none; }")
        dv = QVBoxLayout(dcard); dv.setContentsMargins(35, 30, 35, 30); dv.setSpacing(15)
        
        dtop = QHBoxLayout()
        dep_title = QLabel("Kaspi Депозит")
        dep_title.setStyleSheet("color: white; font-size: 24px; font-weight: 900; background: transparent; border: none;")
        dtop.addWidget(dep_title)
        dtop.addStretch()
        
        perc_lbl = QLabel("14%")
        perc_lbl.setStyleSheet("color: #10B981; font-weight: 900; font-size: 18px; background: transparent; border: none;")
        dtop.addWidget(perc_lbl); dv.addLayout(dtop); dv.addStretch()
        
        dbal_lbl = QLabel(f"{ud['deposit_balance']:,} ₸".replace(","," "))
        dbal_lbl.setStyleSheet("color: white; font-size: 42px; font-weight: 1000; background: transparent; border: none;")
        dv.addWidget(dbal_lbl)
        
        dactions = QHBoxLayout()
        wd_btn = QPushButton("Вывести")
        wd_btn.setStyleSheet("background: rgba(255,255,255,0.15); color: white; border-radius: 12px; font-weight: 800; border: none; padding: 10px 20px;")
        wd_btn.clicked.connect(self._on_withdraw); dactions.addWidget(wd_btn)
        dactions.addStretch(); dv.addLayout(dactions)
        
        if ud['deposit_balance'] > 0:
            prog_lbl = QLabel(f"Прогноз прибыли (12 мес): +{int(ud['deposit_balance']*0.14):,} ₸")
            prog_lbl.setStyleSheet("color: #10B981; font-weight: 700; font-size: 13px; background: transparent; border: none;")
            dv.addWidget(prog_lbl)
        else:
            dv.addStretch()
        acc_h.addWidget(dcard); acc_h.addStretch(); self._content_layout.addLayout(acc_h)

        # Row 2: Goal + Currency
        r2 = QHBoxLayout(); r2.setSpacing(20)
        # Savings Goal
        gf = QFrame(); gf.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #EDEDED; padding: 25px;"); gl = QVBoxLayout(gf); gl.setSpacing(15); goal_val = ud.get('goal_amount', 1500000); goal_name = ud.get('goal_name', 'iPhone 17 Pro Max'); perc = min(100, int((ud['balance'] / goal_val) * 100))
        
        gt_lbl = QLabel(f"<b>{goal_name}</b>")
        gt_lbl.setStyleSheet("font-size: 16px; color: #1A1A1A; border: none;")
        gl.addWidget(gt_lbl)
        
        pb = QProgressBar(); pb.setMaximum(100); pb.setValue(perc); pb.setFixedHeight(12); pb.setStyleSheet("QProgressBar { background: #F3F4F6; border-radius: 6px; border: none; } QProgressBar::chunk { background: #059669; border-radius: 6px; }"); pb.setTextVisible(False); gl.addWidget(pb)
        days = str(int((goal_val - ud['balance']) / 5000)) if ud['balance'] < goal_val else "0"
        
        info = QHBoxLayout()
        cur_goal_lbl = QLabel(f"{ud['balance']:,} / {goal_val:,} ₸")
        cur_goal_lbl.setStyleSheet("color: #6B7280; font-weight: 600; border: none;")
        info.addWidget(cur_goal_lbl)
        info.addStretch()
        
        days_lbl = QLabel(f"Осталось: ~<b>{days}</b> күн")
        days_lbl.setStyleSheet("color: #059669; border: none;")
        info.addWidget(days_lbl); gl.addLayout(info); r2.addWidget(gf, stretch=1)
        
        # Currency Rates (New)
        cur_w = CurrencyRatesWidget(); r2.addWidget(cur_w, stretch=1); self._content_layout.addLayout(r2)

        # Kaspi Red
        red_f = QFrame(); red_f.setObjectName("info_section"); rv = QVBoxLayout(red_f); rv.setContentsMargins(30, 30, 30, 30); rv.setSpacing(15)
        rt = QHBoxLayout()
        red_lim_lbl = QLabel(L.tr("available_limit"))
        red_lim_lbl.setStyleSheet("font-weight:600; color: #1A1A1A; border: none;")
        rt.addWidget(red_lim_lbl)
        rt.addStretch()
        
        red_val_lbl = QLabel(f"{ud['red_limit']:,} ₸")
        red_val_lbl.setStyleSheet("color:#F14635; font-size:20px; font-weight:900; border: none;")
        rt.addWidget(red_val_lbl); rv.addLayout(rt)
        
        rp = QProgressBar(); rp.setMaximum(1000000); rp.setValue(ud['red_limit']); rp.setFixedHeight(10); rp.setStyleSheet("QProgressBar { background: #F3F4F6; border-radius: 5px; border: none; } QProgressBar::chunk { background:#F14635; border-radius: 5px; }"); rv.addWidget(rp)
        lb = QPushButton(L.tr("change_limit")); lb.setFixedWidth(180); lb.setStyleSheet("background: #F3F4F6; color: #1A1A1A; border-radius: 12px; font-weight: 700; padding: 8px; border: none;"); lb.clicked.connect(self._on_change_limit); rv.addWidget(lb, alignment=Qt.AlignmentFlag.AlignRight); self._content_layout.addWidget(red_f)

        # History
        hl = QHBoxLayout(); hl.addWidget(QLabel("Тарих", objectName="section_label")); hl.addStretch(); eb = QPushButton("📄 Экспорт"); eb.setStyleSheet("color:#059669; border:none; font-weight:700;"); eb.clicked.connect(self._on_export); hl.addWidget(eb); self.hist_search = QLineEdit(); self.hist_search.setPlaceholderText("Іздеу..."); self.hist_search.setFixedWidth(200); self.hist_search.textChanged.connect(self._on_history_search); hl.addWidget(self.hist_search); self._content_layout.addLayout(hl)
        self.history_v = QVBoxLayout(); self.history_v.setSpacing(10); self._content_layout.addLayout(self.history_v); self._render_history(); self._content_layout.addStretch()

    def _on_move_to_deposit(self):
        a, ok = QInputDialog.getInt(self, "Депозит", "Сомасы:", min=1000)
        if ok: s, m = self._service.db.move_to_deposit(a); self.refresh_data()
    def _on_withdraw(self):
        a, ok = QInputDialog.getInt(self, "Депозит", "Шығару:", min=1000)
        if ok: s, m = self._service.db.withdraw_from_deposit(a); self.refresh_data()
    def _render_history(self):
        while self.history_v.count():
            w = self.history_v.takeAt(0).widget()
            if w: w.deleteLater()
        txs = self._service.db.get_transactions(limit=100); filtered = [t for t in txs if self._history_query.lower() in t['title'].lower()]
        for t in filtered:
            btn = TransactionItemWidget(t); btn.clicked.connect(lambda _, item=t: self._show_receipt(item)); self.history_v.addWidget(btn)
    def _show_receipt(self, t): d = ReceiptDialog(t, self); d.exec()
    def _on_export(self): p = self._service.export_history(); QMessageBox.information(self, "OK", f"Saved to {p}")
    def _on_history_search(self, t): self._history_query = t; self._render_history()
    def _on_top_up(self):
        a, ok = QInputDialog.getInt(self, L.tr("top_up"), L.tr("amount"), min=100, max=1000000, value=10000)
        if ok: self._service.db.top_up_balance(a); self.refresh_data()
    def _on_change_limit(self):
        a, ok = QInputDialog.getInt(self, L.tr("change_limit"), L.tr("amount"), min=10000, max=1000000, value=150000)
        if ok: s, m, tid = self._service.db.change_red_limit(a); self.refresh_data()
    def _on_change_goal(self):
        n, ok1 = QInputDialog.getText(self, "Мақсат", "Атауы:"); amt, ok2 = QInputDialog.getInt(self, "Мақсат", "Сомасы:", min=1000)
        if ok1 and ok2: self._service.db.update_goal(n, amt); self.refresh_data()
