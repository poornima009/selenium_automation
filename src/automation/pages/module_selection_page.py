from __future__ import annotations

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


class ModuleSelectionPage(BasePage):
    HEADING = "text=Welcome to NYGGS"
    CARD = ".menu-card"
    CARD_TITLE = ".menu-card h3"
    LOGOUT = "img.logout_button"

    def wait_until_loaded(self) -> "ModuleSelectionPage":
        self.wait_for_visible(self.HEADING)
        self.wait_for_visible(self.CARD)
        return self

    def is_loaded(self) -> bool:
        if "modulesSelection" not in self.get_url():
            return False
        return self.is_visible(self.HEADING)

    def module_names(self) -> list[str]:
        return self.get_all_texts(self.CARD_TITLE)

    def has_module(self, name: str) -> bool:
        return name in self.module_names()

    def open_module(self, name: str) -> None:
        logger.info("Opening module %s", name)
        self.click(f'.menu-card:has(h3:text-is("{name}"))')

    def logout(self) -> None:
        self.click(self.LOGOUT)
