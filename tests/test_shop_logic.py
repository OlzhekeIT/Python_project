# tests/test_shop_logic.py
import unittest
import os
import sqlite3
import json
from pathlib import Path
from services.database_service import DatabaseService
from services.shop_service import ShopService
from models.cart import Product

class TestShopLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = Path("tests/test_kaspi.db")
        if cls.test_db_path.exists():
            try: os.remove(cls.test_db_path)
            except: pass
            
    def setUp(self):
        self.db = DatabaseService()
        self.db.db_path = self.test_db_path
        self.db.init_db()
        # Тікелей байланыс арқылы тазалау
        with sqlite3.connect(self.test_db_path) as conn:
            conn.execute("DELETE FROM products")
            conn.execute("DELETE FROM transactions")
            conn.execute("DELETE FROM cart")
            conn.execute("DELETE FROM sales")
            conn.commit()
            
        self.service = ShopService()
        self.service.db = self.db

    def test_cart_quantity_logic(self):
        # Тауар қосу
        self.db.add_product("Item", 1000, "X", "", "{}", "Смартфоны")
        prods = self.service.get_all_products()
        p = prods[0]
        
        self.service.add_to_cart(p)
        self.service.add_to_cart(p) # Екінші рет қосу -> quantity=2 болуы керек
        
        items = self.service.get_cart_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].quantity, 2)
        
        # Санын азайту
        self.service.update_cart_quantity(p.id, -1)
        items = self.service.get_cart_items()
        self.assertEqual(items[0].quantity, 1)
        
        # 0-ге дейін азайту -> себеттен өшуі керек
        self.service.update_cart_quantity(p.id, -1)
        items = self.service.get_cart_items()
        self.assertEqual(len(items), 0)

    def test_promo_code_logic(self):
        self.db.add_product("Phone", 100000, "Apple", "", "{}", "Смартфоны")
        p = self.service.get_all_products()[0]
        self.service.add_to_cart(p)
        
        # KASPI10 кодын тексеру (10% жеңілдік)
        ok, msg, tid = self.service.process_checkout("gold", discount=10)
        self.assertTrue(ok)
        
        # Транзакцияны тексеру
        t = self.db.get_transaction_by_id(tid)
        # 100,000 - 10% = 90,000
        self.assertEqual(abs(t['amount']), 90000)

    def test_multi_unit_sales_logging(self):
        self.db.add_product("Monitor", 50000, "LG", "", "{}", "Аксессуары")
        p = self.service.get_all_products()[0]
        self.service.add_to_cart(p)
        self.db.update_cart_quantity(p.id, 2) # 3 дана (1 бастапқы + 2 қосымша)
        
        # 3 дананы сатып алу
        self.service.process_checkout("gold")
        
        sales = self.db.get_sales_data()
        # 3 жеке жазба болуы керек (талдау үшін)
        self.assertEqual(len(sales), 3)

if __name__ == "__main__":
    unittest.main()
