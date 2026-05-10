# services/localization_service.py
from PyQt6.QtCore import QObject, pyqtSignal

class LocalizationService(QObject):
    lang_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._current_lang = "ru"
        
        self._strings = {
            "ru": {
                "shop": "Магазин", "bank": "Мой Банк", "payments": "Платежи", "transfer": "Переводы",
                "qr": "Kaspi QR", "gid": "Kaspi Gid", "profile": "Профиль", "admin": "Админ-панель",
                "analytics": "Аналитика", "notifications": "Сообщения", "search_placeholder": "Поиск в Магазине...",
                "search": "Поиск", "all_products": "Все товары", "cart": "Корзина", "clear_cart": "Очистить корзину",
                "back": "← Назад", "product_details": "Детали товара", "buy_gold": "Купить сразу",
                "buy_red": "Купить в Kaspi Red", "buy_installments": "Оформить рассрочку",
                "installments_prefix": "Рассрочка 0-0-12", "add_to_cart": "В корзину", "top_up": "Пополнить",
                "change_limit": "Изменить лимит", "debt": "Задолженность", "available_limit": "Доступный лимит",
                "bonuses": "Бонусы", "repay": "Погасить", "pay": "Оплатить", "transfer_title": "Пополнение Kaspi Gold",
                "amount": "Сумма (₸)", "recipient": "Кому (Номер телефона или карта)", "transfer_btn": "Перевести",
                "success": "Успех", "error": "Ошибка", "admin_login_title": "Вход в Админ-панель",
                "admin_pass_placeholder": "Введите пароль", "admin_login_btn": "Войти", "admin_title": "Админ-панель",
                "admin_name_ph": "Название", "admin_price_ph": "Цена", "admin_brand_ph": "Бренд",
                "admin_cat_ph": "Категория", "admin_add_btn": "Добавить", "admin_delete": "Удалить",
                "theme_dark": "Темная тема", "theme_light": "Светлая тема",
                "currency_rates": "Курсы валют", "currency_buy": "Покупка", "currency_sell": "Продажа"
            },
            "kk": {
                "shop": "Магазин", "bank": "Менің Банкім", "payments": "Төлемдер", "transfer": "Аударымдар",
                "qr": "Kaspi QR", "gid": "Kaspi Гид", "profile": "Профиль", "admin": "Админ-панель",
                "analytics": "Аналитика", "notifications": "Хабарламалар", "search_placeholder": "Дүкеннен іздеу...",
                "search": "Іздеу", "all_products": "Барлық тауарлар", "cart": "Себет", "clear_cart": "Себетті тазалау",
                "back": "← Артқа", "product_details": "Тауар туралы мәлімет", "buy_gold": "Қазір сатып алу",
                "buy_red": "Kaspi Red-пен алу", "buy_installments": "Рассрочкаға алу",
                "installments_prefix": "Рассрочка 0-0-12", "add_to_cart": "Себетке қосу", "top_up": "Толтыру",
                "change_limit": "Лимитті өзгерту", "debt": "Қарыз", "available_limit": "Доступный лимит",
                "bonuses": "Бонустар", "repay": "Өтеу", "pay": "Төлеу", "transfer_title": "Kaspi Gold-ты толтыру",
                "amount": "Сомасы (₸)", "recipient": "Кімге (Телефон нөмірі немесе Карта)", "transfer_btn": "Аудару",
                "success": "Сәтті", "error": "Қате", "admin_login_title": "Админ-панельге кіру",
                "admin_pass_placeholder": "Құпия сөз", "admin_login_btn": "Кіру", "admin_title": "Админ-панель",
                "admin_name_ph": "Атауы", "admin_price_ph": "Бағасы", "admin_brand_ph": "Бренд",
                "admin_cat_ph": "Категория", "admin_add_btn": "Қосу", "admin_delete": "Өшіру",
                "theme_dark": "Түнгі режим", "theme_light": "Күндізгі режим",
                "currency_rates": "Валюта бағамдары", "currency_buy": "Сатып алу", "currency_sell": "Сату"
            }
        }

    def set_language(self, lang: str):
        if lang in self._strings and lang != self._current_lang:
            self._current_lang = lang; self.lang_changed.emit()

    def tr(self, key: str) -> str:
        return self._strings[self._current_lang].get(key, key)

    @property
    def current_lang(self): return self._current_lang

L = LocalizationService()
