# controllers/navigation_controller.py
from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal

class NavigationController(QObject):
    """Экрандар арасындағы навигацияны басқару."""
    screen_changed = pyqtSignal(int)

    SCREEN_SHOP            = 0
    SCREEN_BANK            = 1
    SCREEN_PROFILE         = 2
    SCREEN_PRODUCT_DETAILS = 3
    SCREEN_ADMIN           = 4
    SCREEN_TRANSFER        = 5
    SCREEN_GID             = 6
    SCREEN_CODE            = 7
    SCREEN_PAYMENTS        = 8
    SCREEN_ANALYTICS       = 9
    SCREEN_NOTIFICATIONS   = 10

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._current = self.SCREEN_SHOP

    def navigate(self, screen: int) -> None:
        if self._current != screen:
            self._current = screen
            self.screen_changed.emit(screen)

    def go_shop(self) -> None:
        self.navigate(self.SCREEN_SHOP)

    def go_bank(self) -> None:
        self.navigate(self.SCREEN_BANK)

    def go_profile(self) -> None:
        self.navigate(self.SCREEN_PROFILE)

    def go_details(self) -> None:
        self.navigate(self.SCREEN_PRODUCT_DETAILS)

    def go_admin(self) -> None:
        self.navigate(self.SCREEN_ADMIN)

    @property
    def current(self) -> int:
        return self._current
