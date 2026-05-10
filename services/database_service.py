# services/database_service.py
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from contextlib import closing
from services.localization_service import L

class DatabaseService:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "resources" / "data" / "kaspi_market_v5.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self.init_db()

    def _execute(self, query, params=(), fetch=False):
        cursor = self._conn.cursor()
        res = cursor.execute(query, params)
        if fetch: data = [dict(row) for row in res.fetchall()]
        else:
            self._conn.commit()
            data = cursor.lastrowid
        return data

    def init_db(self):
        cursor = self._conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price INTEGER NOT NULL, brand TEXT, category TEXT DEFAULT 'Смартфоны', image_path TEXT, specs TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_account (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 1500000, bonuses INTEGER DEFAULT 5400, red_limit INTEGER DEFAULT 150000, red_debt INTEGER DEFAULT 0, name TEXT DEFAULT 'Диас', phone TEXT DEFAULT '+7 (707) *** ** 55', goal_name TEXT DEFAULT 'iPhone 17 Pro Max', goal_amount INTEGER DEFAULT 1500000, avatar_path TEXT DEFAULT '', deposit_balance INTEGER DEFAULT 0)''')
        cursor.execute('CREATE TABLE IF NOT EXISTS cart (product_id INTEGER PRIMARY KEY, quantity INTEGER DEFAULT 1)')
        try: cursor.execute('ALTER TABLE cart ADD COLUMN quantity INTEGER DEFAULT 1')
        except: pass
        cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT, user TEXT, text TEXT, image_path TEXT, timestamp TEXT, rating INTEGER DEFAULT 5)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, amount INTEGER, type TEXT, timestamp TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS favorites (product_id INTEGER PRIMARY KEY)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, p_name TEXT, price INTEGER, category TEXT, timestamp TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, message TEXT, type TEXT, timestamp TEXT, is_read INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS recent_views (product_id INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS achievements (id TEXT PRIMARY KEY, title TEXT, is_unlocked INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS promo_codes (code TEXT PRIMARY KEY, discount_percent INTEGER)''')
        cursor.execute("INSERT OR IGNORE INTO promo_codes (code, discount_percent) VALUES ('KASPI10', 10)")
        cursor.execute("INSERT OR IGNORE INTO promo_codes (code, discount_percent) VALUES ('SALE20', 20)")
        cursor.execute("INSERT OR IGNORE INTO user_account (id, balance, bonuses, red_limit, red_debt, name, phone, goal_name, goal_amount, avatar_path, deposit_balance) VALUES (1, 1500000, 5400, 150000, 0, 'Диас', '+7 (707) *** ** 55', 'iPhone 17 Pro Max', 1500000, '', 0)")
        self._conn.commit()

    def get_all_products(self, search="", filter_val="Все", filter_type="category", min_p=0, max_p=9999999):
        # Қауіпсіздік үшін бағана атын тексеру
        col = "category" if filter_type == "category" else "brand"
        query = f"SELECT p.*, (f.product_id IS NOT NULL) as is_favorite FROM products p LEFT JOIN favorites f ON p.id = f.product_id WHERE p.name LIKE ? AND p.price >= ? AND p.price <= ?"
        params = [f"%{search}%", min_p, max_p]
        if filter_val != "Все":
            if filter_val == "Favorites": query += " AND f.product_id IS NOT NULL"
            else: query += f" AND p.{col} = ?"; params.append(filter_val)
        return self._execute(query, params, fetch=True)

    def add_notification(self, title, message, n_type="INFO"):
        ts = datetime.now().strftime("%d.%m.%Y %H:%M")
        self._execute("INSERT INTO notifications (title, message, type, timestamp, is_read) VALUES (?, ?, ?, ?, 0)", (title, message, n_type, ts))

    def process_payment_gold_custom(self, amount, bonus_amt):
        u = self.get_user_data()
        if u['balance'] < amount: return False, "Low balance", 0
        tid = self.log_transaction("Покупка (Gold)", -amount, "OUT")
        self._execute("UPDATE user_account SET balance = balance - ?, bonuses = bonuses + ? WHERE id = 1", (amount, bonus_amt))
        self.add_notification("Бонустар есептелді", f"{bonus_amt:,} бонус алдыңыз!", "SUCCESS")
        return True, "ОК", tid

    def update_goal(self, name, amount):
        self._execute("UPDATE user_account SET goal_name = ?, goal_amount = ? WHERE id = 1", (name, amount))
        self.add_notification("Мақсат жаңартылды", name)

    def move_to_deposit(self, amount):
        u = self.get_user_data()
        if u['balance'] < amount: return False, "Low balance", 0
        self._execute("UPDATE user_account SET balance = balance - ?, deposit_balance = deposit_balance + ? WHERE id = 1", (amount, amount))
        tid = self.log_transaction("Перевод на Депозит", -amount, "OUT")
        return True, "ОК", tid

    def withdraw_from_deposit(self, amount):
        u = self.get_user_data()
        if u['deposit_balance'] < amount: return False, "Low balance", 0
        self._execute("UPDATE user_account SET balance = balance + ?, deposit_balance = deposit_balance - ? WHERE id = 1", (amount, amount))
        tid = self.log_transaction("Перевод с Депозита", amount, "IN")
        return True, "ОК", tid

    def get_user_data(self):
        res = self._execute("SELECT * FROM user_account WHERE id = 1", fetch=True)
        return res[0] if res else {"balance":0, "bonuses":0, "red_limit":150000, "red_debt":0}

    def validate_promo(self, code):
        res = self._execute("SELECT discount_percent FROM promo_codes WHERE code = ?", (code.upper(),), fetch=True)
        return res[0]['discount_percent'] if res else 0

    def log_transaction(self, title, amount, t_type):
        ts = datetime.now().strftime("%d.%m.%Y %H:%M"); return self._execute("INSERT INTO transactions (title, amount, type, timestamp) VALUES (?, ?, ?, ?)", (title, amount, t_type, ts))

    def top_up_balance(self, a):
        tid = self.log_transaction("Пополнение Gold", a, "IN")
        self._execute("UPDATE user_account SET balance = balance + ? WHERE id = 1", (a,))
        return True, "ОК", tid

    def process_general_payment(self, a, t):
        u = self.get_user_data()
        if u['balance'] < a: return False, "Low balance", 0
        tid = self.log_transaction(t, -a, "OUT")
        self._execute("UPDATE user_account SET balance = balance - ?, bonuses = bonuses + ? WHERE id = 1", (a, int(a*0.01)))
        return True, "ОК", tid

    def process_payment_gold(self, a): return self.process_payment_gold_custom(a, int(a*0.01))

    def process_payment_red(self, a):
        tid = self.log_transaction("Покупка (Red)", -a, "RED")
        self._execute("UPDATE user_account SET red_limit = red_limit - ?, red_debt = red_debt + ? WHERE id = 1", (a, a))
        return True, "ОК", tid

    def process_payment_installments(self, a):
        tid = self.log_transaction("Рассрочка", -a, "INST")
        self._execute("UPDATE user_account SET red_limit = red_limit - ?, red_debt = red_debt + ? WHERE id = 1", (a, a))
        return True, "ОК", tid

    def process_transfer(self, r, a):
        u = self.get_user_data()
        if u['balance'] < a: return False, "Low balance", 0
        tid = self.log_transaction(f"Перевод: {r}", -a, "OUT")
        self._execute("UPDATE user_account SET balance = balance - ? WHERE id = 1", (a,))
        return True, "ОК", tid

    def get_sales_data(self): return self._execute("SELECT * FROM sales", fetch=True)
    def get_transactions(self, limit=20): return self._execute(f"SELECT * FROM transactions ORDER BY id DESC LIMIT {limit}", fetch=True)
    def get_all_transactions(self): return self._execute("SELECT * FROM transactions", fetch=True)
    def add_product(self, n, p, b, i, s, c): self._execute("INSERT INTO products (name, price, brand, image_path, specs, category) VALUES (?, ?, ?, ?, ?, ?)", (n, p, b, i, s, c))
    def delete_product(self, pid): self._execute("DELETE FROM products WHERE id = ?", (pid,))
    def toggle_favorite(self, pid):
        with closing(sqlite3.connect(self.db_path)) as conn:
            exists = conn.execute("SELECT 1 FROM favorites WHERE product_id = ?", (pid,)).fetchone()
            if exists: conn.execute("DELETE FROM favorites WHERE product_id = ?", (pid,)); res = False
            else: conn.execute("INSERT INTO favorites (product_id) VALUES (?)", (pid,)); res = True
            conn.commit(); return res
    def update_avatar(self, path): self._execute("UPDATE user_account SET avatar_path = ? WHERE id = 1", (path,))
    def update_profile(self, name, phone): self._execute("UPDATE user_account SET name = ?, phone = ? WHERE id = 1", (name, phone))
    def repay_red_debt(self, a): self._execute("UPDATE user_account SET balance = balance - ?, red_limit = red_limit + ?, red_debt = red_debt - ? WHERE id = 1", (a, a, a)); self.log_transaction("Погашение Red", -a, "OUT"); return True, "ОК"
    def add_review(self, p, u, t, r=5, i=""): ts = datetime.now().strftime("%d.%m.%Y %H:%M"); self._execute("INSERT INTO reviews (product_name, user, text, image_path, timestamp, rating) VALUES (?, ?, ?, ?, ?, ?)", (p, u, t, i, ts, r))
    def get_reviews(self, p): return self._execute("SELECT * FROM reviews WHERE product_name = ? ORDER BY id DESC", (p,), fetch=True)
    def add_to_cart(self, pid):
        with closing(sqlite3.connect(self.db_path)) as conn:
            exists = conn.execute("SELECT quantity FROM cart WHERE product_id = ?", (pid,)).fetchone()
            if exists: conn.execute("UPDATE cart SET quantity = quantity + 1 WHERE product_id = ?", (pid,))
            else: conn.execute("INSERT INTO cart (product_id, quantity) VALUES (?, 1)", (pid,))
            conn.commit()
    def get_cart_items(self): return self._execute("SELECT p.*, c.quantity FROM products p JOIN cart c ON p.id = c.product_id", fetch=True)
    def clear_cart(self): self._execute("DELETE FROM cart")
    def delete_from_cart(self, pid): self._execute("DELETE FROM cart WHERE product_id = ?", (pid,))
    def update_cart_quantity(self, pid, delta):
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute("UPDATE cart SET quantity = quantity + ? WHERE product_id = ?", (delta, pid))
            conn.execute("DELETE FROM cart WHERE quantity <= 0"); conn.commit()
    def unlock_achievement(self, aid): self._execute("UPDATE achievements SET is_unlocked = 1 WHERE id = ?", (aid,))
    def get_achievements(self): return self._execute("SELECT * FROM achievements", fetch=True)
    def log_recent_view(self, pid): self._execute("INSERT OR REPLACE INTO recent_views (product_id, timestamp) VALUES (?, CURRENT_TIMESTAMP)", (pid,)); self._execute("DELETE FROM recent_views WHERE product_id NOT IN (SELECT product_id FROM recent_views ORDER BY timestamp DESC LIMIT 5)")
    def get_recent_views(self): return self._execute("SELECT p.*, (f.product_id IS NOT NULL) as is_favorite FROM recent_views r JOIN products p ON r.product_id = p.id LEFT JOIN favorites f ON p.id = f.product_id ORDER BY r.timestamp DESC", fetch=True)
    def convert_bonuses(self):
        u = self.get_user_data(); a = u['bonuses']
        if a > 0: self._execute("UPDATE user_account SET balance = balance + ?, bonuses = 0 WHERE id = 1", (a,)); self.log_transaction("Конвертация бонусов", a, "IN"); return True, "ОК"
        return False, "No bonus"
    def get_unread_count(self):
        res = self._execute("SELECT COUNT(*) as cnt FROM notifications WHERE is_read = 0", fetch=True)
        return res[0]['cnt'] if res else 0
    def mark_notifications_read(self): self._execute("UPDATE notifications SET is_read = 1")
    def get_notifications(self, limit=50): return self._execute(f"SELECT * FROM notifications ORDER BY id DESC LIMIT {limit}", fetch=True)
    def log_sale(self, pid, name, price, cat):
        ts = datetime.now().strftime("%d.%m.%Y"); self._execute("INSERT INTO sales (product_id, p_name, price, category, timestamp) VALUES (?, ?, ?, ?, ?)", (pid, name, price, cat, ts))
    def get_transaction_by_id(self, tid):
        res = self._execute("SELECT * FROM transactions WHERE id = ?", (tid,), fetch=True)
        return res[0] if res else None
