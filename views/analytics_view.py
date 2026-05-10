# views/analytics_view.py
from __future__ import annotations
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar
from PyQt6.QtCore import Qt, QRect, QPoint, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from services.shop_service import ShopService
from services.localization_service import L
from views.base_view import BaseView

class PieChartWidget(QWidget):
    """Шығындар құрылымын дөңгелек диаграмма түрінде көрсету."""
    def __init__(self, data: dict[str, float], parent=None):
        super().__init__(parent); self.data = data; self.setMinimumHeight(220)
        self.colors = [QColor("#F14635"), QColor("#0089d0"), QColor("#1A1A1A"), QColor("#059669")]

    def paintEvent(self, event):
        if not self.data or sum(self.data.values()) == 0: return
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width(); h = self.height(); total = sum(self.data.values())
        rect = QRectF(20, 20, h - 40, h - 40) # Square for circle
        
        start_angle = 0
        for i, (label, val) in enumerate(self.data.items()):
            span = int((val / total) * 360 * 16)
            p.setBrush(self.colors[i % len(self.colors)])
            p.setPen(QPen(Qt.GlobalColor.white, 2))
            p.drawPie(rect, start_angle, span)
            
            # Legend
            lx = h + 10; ly = 40 + i * 30
            p.setBrush(self.colors[i % len(self.colors)]); p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(int(lx), int(ly), 12, 12, 4, 4)
            p.setPen(QColor("#4B5563")); p.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            p.drawText(int(lx + 20), int(ly + 11), f"{label}: {int((val/total)*100)}%")
            
            start_angle += span

class BarChartWidget(QWidget):
    def __init__(self, data: dict[str, float], parent=None):
        super().__init__(parent); self.data = data; self.setMinimumHeight(200)
    def paintEvent(self, event):
        if not self.data: return
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width(); h = self.height(); padding = 40; cw = w - 2*padding; ch = h - 2*padding
        mv = max(self.data.values()) if self.data.values() else 1; bw = cw / len(self.data) - 20
        for i, (label, val) in enumerate(self.data.items()):
            bh = (val / mv) * ch; x = padding + i * (bw + 20); y = h - padding - bh
            rect = QRect(int(x), int(y), int(bw), int(bh)); painter.setBrush(QColor("#0089d0") if i % 2 == 0 else QColor("#1A1A1A")); painter.setPen(Qt.PenStyle.NoPen); painter.drawRoundedRect(rect, 8, 8)
            painter.setPen(QColor("#4B5563")); painter.setFont(QFont("Inter", 9, QFont.Weight.Bold)); painter.drawText(QRect(int(x), h - padding + 5, int(bw), 20), Qt.AlignmentFlag.AlignCenter, label)
            painter.setPen(QColor("#1A1A1A")); painter.drawText(QRect(int(x), int(y) - 20, int(bw), 20), Qt.AlignmentFlag.AlignCenter, f"{int(val/1000)}k")

class LineChartWidget(QWidget):
    def __init__(self, amounts: np.ndarray, parent=None):
        super().__init__(parent); self.amounts = amounts; self.setMinimumHeight(200)
    def paintEvent(self, event):
        if len(self.amounts) < 2: return
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width(); h = self.height(); pad = 40; cw = w - 2*pad; ch = h - 2*pad
        mv = np.max(self.amounts) if len(self.amounts) > 0 else 1; points = []
        for i, val in enumerate(self.amounts):
            px = pad + i * (cw / (len(self.amounts) - 1)); py = h - pad - (val / mv) * ch; points.append(QPoint(int(px), int(py)))
        pen = QPen(QColor("#F14635"), 3); p.setPen(pen)
        for i in range(len(points)-1): p.drawLine(points[i], points[i+1])
        p.setBrush(QColor("#F14635")); p.setPen(Qt.PenStyle.NoPen)
        for pt in points: p.drawEllipse(pt, 4, 4)

class StatCard(QFrame):
    def __init__(self, title: str, value: str, icon: str, color: str = "#1A1A1A"):
        super().__init__()
        self.setStyleSheet(f"background: white; border-radius: 16px; border: 1px solid #EDEDED;"); self.setMinimumWidth(200)
        l = QVBoxLayout(self); l.setContentsMargins(20, 20, 20, 20); l.setSpacing(10); h = QHBoxLayout(); h.addWidget(QLabel(icon, styleSheet="font-size: 24px;")); h.addStretch(); l.addLayout(h)
        self.title_lbl = QLabel(title); self.title_lbl.setStyleSheet("color: #757575; font-size: 13px; font-weight: 600;"); self.val_lbl = QLabel(value); self.val_lbl.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 900;"); l.addWidget(self.title_lbl); l.addWidget(self.val_lbl)

class AnalyticsView(BaseView):
    def __init__(self, service: ShopService, parent: QWidget | None = None) -> None:
        self._service = service; super().__init__(parent); self.setObjectName("analytics_view"); self.refresh_data()
    def update_localization(self): self.set_title(L.tr("analytics")); self.refresh_data()
    def refresh_data(self):
        self.set_title(L.tr("analytics")); self.clear_layout(self._content_layout)
        txs = self._service.db.get_all_transactions()
        if not txs: self._content_layout.addWidget(QLabel("Нет данных", alignment=Qt.AlignmentFlag.AlignCenter)); return
        amounts = np.array([t['amount'] for t in txs]); exp_txs = [t for t in txs if t['amount'] < 0]; expenses = np.abs(np.array([t['amount'] for t in exp_txs]))
        
        # Row 1: Summary Stats
        s1 = QHBoxLayout(); s1.setSpacing(20); s1.addWidget(StatCard("Табыстар", f"{np.sum(amounts[amounts > 0]):,} ₸", "📈", "#059669"), stretch=1); s1.addWidget(StatCard("Шығындар", f"{np.sum(expenses):,} ₸", "📉", "#F14635"), stretch=1); self._content_layout.addLayout(s1)
        
        # Row 2: Charts
        charts_h = QHBoxLayout(); charts_h.setSpacing(20)
        
        # Pie Chart Section
        types = {"Gold": 0, "Red": 0, "Inst": 0}
        for t in exp_txs:
            if "Gold" in t['title']: types["Gold"] += abs(t['amount'])
            elif "Red" in t['title']: types["Red"] += abs(t['amount'])
            else: types["Inst"] += abs(t['amount'])
            
        pie_f = QFrame(); pie_f.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #EDEDED; padding: 20px;"); pl = QVBoxLayout(pie_f); pl.addWidget(QLabel("Шығындар құрылымы", styleSheet="font-weight:800; font-size:16px;"))
        pl.addWidget(PieChartWidget(types)); charts_h.addWidget(pie_f, stretch=1)
        
        # Trend Chart Section
        if len(expenses) >= 2:
            line_f = QFrame(); line_f.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #EDEDED; padding: 20px;"); ll = QVBoxLayout(line_f); ll.addWidget(QLabel("Динамика трат", styleSheet="font-weight:800; font-size:16px;"))
            ll.addWidget(LineChartWidget(expenses[-10:])); charts_h.addWidget(line_f, stretch=1)
            
        self._content_layout.addLayout(charts_h); self._content_layout.addStretch()
