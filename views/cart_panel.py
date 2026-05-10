# views/cart_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea, QFrame
from PyQt6.QtCore import Qt
from models.cart import Cart

class CartItemWidget(QFrame):
    """Себеттегі тауардың визуалды блогы."""
    def __init__(self, name: str, price: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("cartItem")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        info = QVBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setObjectName("cartItemTitle")
        
        price_lbl = QLabel(f"{price} ₸")
        price_lbl.setObjectName("cartItemPrice")
        
        info.addWidget(name_lbl)
        info.addWidget(price_lbl)
        
        layout.addLayout(info)
        layout.addStretch()

class CartPanel(QWidget):
    """Себет панелі: оң жақта бекітілген тізім."""
    def __init__(self, cart: Cart, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cart = cart
        self.setObjectName("cartPanel")
        self.init_ui()

    def init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Тақырып
        title = QLabel("Себет")
        title.setObjectName("cartTitle")
        self.layout.addWidget(title)

        # Тізім (ScrollArea)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("cartScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.list_container = QWidget()
        self.list_container.setObjectName("cartList")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setSpacing(8)
        
        self.scroll.setWidget(self.list_container)
        self.layout.addWidget(self.scroll, stretch=1)

        # Футер (Жалпы сома + Сатып алу)
        footer = QWidget()
        footer.setObjectName("cartFooter")
        footer_layout = QVBoxLayout(footer)
        
        total_header = QLabel("Жалпы сома")
        total_header.setObjectName("cartTotalLabel")
        
        self.total_val = QLabel("0 ₸")
        self.total_val.setObjectName("cartTotalValue")
        
        footer_layout.addWidget(total_header)
        footer_layout.addWidget(self.total_val)
        
        checkout_btn = QPushButton("Тапсырыс беру")
        checkout_btn.setObjectName("checkoutBtn")
        checkout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        footer_layout.addWidget(checkout_btn)
        
        self.layout.addWidget(footer)
        
        self.refresh()

    def refresh(self) -> None:
        """Тізімді жаңарту."""
        # Ескі элементтерді тазалау
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Жаңа элементтерді қосу
        for item in self._cart.items:
            self.list_layout.addWidget(CartItemWidget(item.name, item.price))
        
        self.total_val.setText(f"{self._cart.get_total()} ₸")
