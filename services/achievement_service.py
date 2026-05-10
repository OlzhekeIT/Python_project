# services/achievement_service.py
from __future__ import annotations
from services.database_service import DatabaseService

class AchievementService:
    """Марапаттар логикасын басқару сервисі."""
    def __init__(self, db: DatabaseService):
        self.db = db

    def check_all(self):
        """Барлық марапаттарды тексеру."""
        user = self.db.get_user_data()
        sales = self.db.get_sales_data()
        reviews_res = self.db._execute("SELECT COUNT(*) as cnt FROM reviews", fetch=True)
        reviews = reviews_res[0]['cnt'] if reviews_res else 0
        txs = self.db.get_all_transactions()
        
        # 1. Millionaire
        if user['balance'] >= 1000000:
            self._unlock("millionaire", "Миллионер", "Сіздің теңгеріміңіз 1 000 000 ₸-ден асты!")
            
        # 2. First Buy
        if len(sales) > 0:
            self._unlock("first_buy", "Алғашқы сатып алу", "Құттықтаймыз! Сіз алғашқы тауарыңызды алдыңыз.")
            
        # 3. Reviewer
        if reviews > 0:
            self._unlock("reviewer", "Сыншы", "Пікір қалдырғаныңыз үшін рахмет!")
            
        # 4. Saver (Бонустар көп болса немесе теңгерім жоғары болса)
        if user['bonuses'] >= 10000 or user['balance'] >= 2000000:
            self._unlock("saver", "Үнемшіл", "Сіз керемет үнемшілсіз!")

        # 5. Master of Bonus (Егер бонус конвертацияланса - транзакциялардан табамыз)
        if any("Конвертация бонусов" in t['title'] for t in txs):
            self._unlock("master_bonus", "Бонус шебері", "Сіз бонустарды сәтті пайдаландыңыз!")

    def _unlock(self, aid: str, title: str, msg: str):
        achs = self.db.get_achievements()
        for a in achs:
            if a['id'] == aid and not a['is_unlocked']:
                self.db.unlock_achievement(aid)
                self.db.add_notification(f"Жаңа марапат: {title}", msg, "SUCCESS")
