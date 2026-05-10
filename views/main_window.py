# views/main_window.py
from __future__ import annotations
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QMessageBox, QGraphicsOpacityEffect, QApplication
)
from PyQt6.QtGui import QPixmap
from controllers.navigation_controller import NavigationController
from services.shop_service            import ShopService
from services.achievement_service     import AchievementService
from models.cart                      import Review
from views.sidebar                    import SidebarWidget
from views.shop_window                import ShopWindow
from views.product_details_view       import ProductDetailsView
from views.bank_view                  import BankView
from views.profile_view               import ProfileView
from views.admin_view                 import AdminView, AdminLoginDialog
from views.transfer_view              import TransferView
from views.payments_view              import PaymentsView
from views.analytics_view             import AnalyticsView
from views.gid_view                   import GidView
from views.code_view                  import CodeView
from views.notifications_view         import NotificationsView
from views.login_view                 import LoginView

from services.localization_service import L

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Kaspi.kz"); self.setMinimumSize(1100, 750); self.resize(1280, 850)
        self._shop_svc = ShopService(); self._ach_svc = AchievementService(self._shop_svc.db); self._nav = NavigationController(self)
        self._login = LoginView(); self._login.authenticated.connect(self._on_authenticated)
        self.setCentralWidget(self._login)

    def _on_authenticated(self):
        self._sidebar = SidebarWidget(); self._shop = ShopWindow(self._shop_svc); self._bank = BankView(self._shop_svc)
        self._profile = ProfileView(self._shop_svc); self._details = ProductDetailsView(); self._admin = AdminView(self._shop_svc)
        self._transfer = TransferView(self._shop_svc); self._gid = GidView(); self._code = CodeView(self._shop_svc); self._payments = PaymentsView(self._shop_svc)
        self._analytics = AnalyticsView(self._shop_svc); self._notes = NotificationsView(self._shop_svc)

        self._sidebar.theme_toggled.connect(self._on_theme_toggled)

        self._stack = QStackedWidget()
        widgets = [self._shop, self._bank, self._profile, self._details, self._admin, self._transfer, self._gid, self._code, self._payments, self._analytics, self._notes]
        for w in widgets: self._stack.addWidget(w)
        
        container = QWidget(); l = QHBoxLayout(container); l.setContentsMargins(0,0,0,0); l.setSpacing(0); l.addWidget(self._sidebar); l.addWidget(self._stack, stretch=1)
        self.setCentralWidget(container); self._connect_signals(); self.refresh_badges()

    def _on_theme_toggled(self, is_dark: bool):
        from pathlib import Path
        file = "dark_styles.qss" if is_dark else "styles.qss"
        path = Path(__file__).parent.parent / "resources" / file
        if path.exists(): QApplication.instance().setStyleSheet(path.read_text(encoding="utf-8"))

    def _connect_signals(self) -> None:
        self._sidebar.nav_clicked.connect(self._on_nav); self._nav.screen_changed.connect(self._on_nav_direct)
        self._shop.product_selected.connect(self._on_product_selected); self._details.back_clicked.connect(self._on_close_details)
        self._details.review_submitted.connect(self._on_review_submitted); self._details.add_to_cart_clicked.connect(self._on_add_to_cart)
        self._details.buy_gold_clicked.connect(self._on_buy_gold); self._details.buy_red_clicked.connect(self._on_buy_red)
        self._details.buy_installments_clicked.connect(self._on_buy_installments); self._details.product_selected.connect(self._on_product_selected)
        self._code.payment_successful.connect(self.refresh_badges)

    def refresh_badges(self): self._sidebar.set_notification_badge(self._shop_svc.db.get_unread_count())

    def _on_nav(self, name):
        mapping = {"Shop":0, "Bank":1, "Profile":2, "Transfer":5, "Gid":6, "Code":7, "Payments":8, "Analytics":9, "Notifications":10}
        self._ach_svc.check_all(); self.refresh_badges()
        if name == "Admin":
            d = AdminLoginDialog(self)
            if d.exec() and d.pass_in.text() == "admin123": self._admin.refresh_all(); self._nav.navigate(4)
            else: self._sidebar.select_item("Shop")
        elif name in mapping: 
            if name == "Bank": self._bank.refresh_data()
            if name == "Profile": self._profile.refresh_data()
            if name == "Analytics": self._analytics.refresh_data()
            if name == "Notifications": self._notes.refresh_data(); self.refresh_badges()
            self._nav.navigate(mapping[name])

    def _on_nav_direct(self, i): self._stack.setCurrentIndex(i)

    def _on_product_selected(self, p):
        self._shop_svc.db.log_recent_view(p.id); self._shop.refresh_recent()
        revs = self._shop_svc.db.get_reviews(p.name); p.reviews = [Review(r['user'], r.get('rating', 5), r['text'], r.get('image_path', ''), r.get('timestamp', '')) for r in revs]
        recs = self._shop_svc.get_recommendations(p); self._details.set_product(p, recs); self._nav.navigate(3)

    def _on_close_details(self): self._nav.navigate(0); self._sidebar.select_item("Shop"); self._shop.refresh_products()
    def _on_add_to_cart(self, p): self._shop_svc.add_to_cart(p); self._shop._refresh_cart()
    def _on_review_submitted(self, n, r): self._shop_svc.db.add_review(n, r.user, r.text, r.rating, r.image_path); self._ach_svc.check_all(); self.refresh_badges(); QMessageBox.information(self, "OK", "ОК")
    def _on_buy_gold(self, p):
        ok, msg, tid = self._shop_svc.db.process_payment_gold(p.price)
        if ok: self._after_buy(p.name, msg); self._on_close_details()
    def _on_buy_red(self, p):
        ok, msg, tid = self._shop_svc.db.process_payment_red(p.price)
        if ok: self._after_buy(p.name, msg); self._on_close_details()
    def _on_buy_installments(self, p):
        ok, msg, tid = self._shop_svc.db.process_payment_installments(p.price)
        if ok: self._after_buy(p.name, msg); self._on_close_details()
    def _after_buy(self, n, m): self._ach_svc.check_all(); self.refresh_badges(); QMessageBox.information(self, "Kaspi.kz", f"OK: {n}")
