# services/shop_service.py
import json
import numpy as np
from models.cart import Product, Review
from services.database_service import DatabaseService

class ShopService:
    """Дүкен сервисі: SQLite базасымен жұмыс істейді."""
    def __init__(self) -> None:
        self.db = DatabaseService()
        self._ensure_initial_products()
        # Белсенді бонус категориясы (Проектке динамика қосу)
        self.bonus_category = "Смартфоны" 

    def get_bonus_percent(self, category: str) -> int:
        return 5 if category == self.bonus_category else 1

    def _ensure_initial_products(self):
        if not self.db.get_all_products():
            initial = [
                ("iPhone 17 Pro", 650000, "Apple", "resources/images/Phone/iphone17.png", {"Экран": "6.7' OLED", "CPU": "A19"}, "Смартфоны"),
                ("Samsung S24 Ultra", 700000, "Samsung", "resources/images/Phone/s24ultra.png", {"Экран": "6.8' AMOLED", "CPU": "Snapdragon"}, "Смартфоны"),
                ("Vivo X100", 450000, "Vivo", "resources/images/Phone/vivo.png", {"Экран": "6.78' AMOLED", "CPU": "Dimensity"}, "Смартфоны"),
                ("MacBook Pro M3", 1200000, "Apple", "", {"Экран": "14' Liquid Retina", "CPU": "M3 Pro"}, "Ноутбуки"),
                ("Asus ROG Strix", 850000, "Asus", "", {"Экран": "16' IPS", "CPU": "Intel i9"}, "Ноутбуки"),
                ("AirPods Pro 2", 120000, "Apple", "", {"Тип": "Внутриканальные", "Шумоподавление": "Активное"}, "Аксессуары")
            ]
            for name, price, brand, img, specs, cat in initial:
                self.db.add_product(name, price, brand, img, json.dumps(specs), cat)

    def get_all_products(self, search="", filter_val="Все", filter_type="category", sort_by="default", min_p=0, max_p=9999999) -> list[Product]:
        if filter_val == "Popular": return self.get_popular_products()
        raw_products = self.db.get_all_products(search, filter_val, filter_type, min_p, max_p)
        products = []
        for p in raw_products:
            prod = Product(name=p['name'], price=p['price'], brand=p['brand'], category=p.get('category', 'Смартфоны'), image_path=p['image_path'], specs=json.loads(p['specs']) if p['specs'] else {})
            prod.id = p['id']; prod.is_favorite = bool(p.get('is_favorite', 0))
            raw_reviews = self.db.get_reviews(p['name']); prod.reviews = [Review(r['user'], r.get('rating', 5), r['text']) for r in raw_reviews]
            products.append(prod)
        if sort_by == "price_asc": products.sort(key=lambda x: x.price)
        elif sort_by == "price_desc": products.sort(key=lambda x: x.price, reverse=True)
        elif sort_by == "rating": products.sort(key=lambda x: sum(r.rating for r in x.reviews)/len(x.reviews) if x.reviews else 0, reverse=True)
        return products

    def get_popular_products(self) -> list[Product]:
        sales = self.db.get_sales_data()
        if not sales: return self.get_all_products(filter_val="Все")
        p_names = [s['p_name'] for s in sales]; unique, counts = np.unique(p_names, return_counts=True)
        top_names = unique[np.argsort(-counts)]; all_prods = self.get_all_products(filter_val="Все"); popular = []
        for name in top_names:
            for p in all_prods:
                if p.name == name: popular.append(p); break
        for p in all_prods:
            if p not in popular: popular.append(p)
        return popular[:12]

    def get_recent_products(self) -> list[Product]:
        raw = self.db.get_recent_views()
        return [Product(name=p['name'], price=p['price'], image_path=p['image_path']) for p in raw]

    def get_recommendations(self, product: Product) -> list[Product]:
        all_prods = self.get_all_products(filter_val=product.category, filter_type="category")
        return [p for p in all_prods if getattr(p, 'id', 0) != getattr(product, 'id', -1)][:4]

    def toggle_favorite(self, pid: int) -> bool: return self.db.toggle_favorite(pid)
    def add_to_cart(self, product: Product) -> None:
        pid = getattr(product, 'id', None)
        if pid: self.db.add_to_cart(pid)
    def update_cart_quantity(self, pid: int, delta: int): self.db.update_cart_quantity(pid, delta)
    def get_cart_items(self) -> list[Product]:
        raw = self.db.get_cart_items()
        products = []
        for r in raw:
            p = Product(name=r['name'], price=r['price'], image_path=r['image_path'], category=r.get('category', 'Смартфоны'))
            p.id = r['id']; p.quantity = r.get('quantity', 1); products.append(p)
        return products
    def add_review(self, product_name: str, review: Review) -> None: self.db.add_review(product_name, review.user, review.text, review.rating, review.image_path)
    def get_cart_text(self) -> str:
        items = self.get_cart_items(); total = sum(i.price * i.quantity for i in items)
        return f"Себетте: {sum(i.quantity for i in items)} тауар\nЖалпы сома: {total:,} ₸"
    def clear_cart(self): self.db.clear_cart()
    def remove_from_cart(self, pid: int): self.db.delete_from_cart(pid)
    def export_history(self) -> str:
        txs = self.db.get_all_transactions(); path = "kaspi_history.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write("=== KASPI.KZ HISTORY ===\n")
            for t in txs: f.write(f"[{t['timestamp']}] {t['title']} | {t['amount']:,} ₸\n")
        return path

    def process_checkout(self, method: str, discount: int = 0) -> tuple[bool, str, int]:
        items = self.get_cart_items()
        if not items: return False, "Себет бос", 0
        
        total_price = 0
        total_bonus = 0
        
        for p in items:
            p_total = p.price * p.quantity
            if discount > 0: p_total = int(p_total * (1 - discount / 100))
            total_price += p_total
            
            # Динамикалық бонус есептеу
            bp = self.get_bonus_percent(p.category)
            total_bonus += int(p_total * (bp / 100))

        if method == "gold": ok, m, tid = self.db.process_payment_gold_custom(total_price, total_bonus)
        elif method == "red": ok, m, tid = self.db.process_payment_red(total_price)
        else: ok, m, tid = self.db.process_payment_installments(total_price)
        
        if ok:
            for p in items: 
                for _ in range(p.quantity): self.db.log_sale(getattr(p, 'id', 0), p.name, p.price, p.category)
            self.clear_cart()
        return ok, m, tid
