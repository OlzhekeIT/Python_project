# models/cart.py
from dataclasses import dataclass, field

@dataclass
class Review:
    """Пікір моделі."""
    user: str
    rating: int
    text: str

@dataclass
class Product:
    """Тауар моделі: телефонның толық сипаттамасы мен пікірлері бар."""
    name: str
    price: int
    image_path: str = ""
    brand: str = ""
    category: str = "Смартфоны"
    specs: dict[str, str] = field(default_factory=dict)
    reviews: list[Review] = field(default_factory=list)

class Cart:
    def __init__(self) -> None:
        self.items: list[Product] = []

    def add_product(self, product: Product) -> None:
        self.items.append(product)

    def remove_product(self, product: Product) -> None:
        if product in self.items:
            self.items.remove(product)

    def clear(self):
        self.items = []

    def get_total(self) -> int:
        return sum(item.price for item in self.items)

    @property
    def items_count(self) -> int:
        return len(self.items)
