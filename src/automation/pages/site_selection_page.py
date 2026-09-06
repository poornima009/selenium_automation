from __future__ import annotations

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


class SiteSelectionPage(BasePage):
    """Shared /selectsite picker used by Store and other product apps."""

    SEARCH = "textarea[placeholder='Search Site...']"
    SITE_TITLE = ".cardBody h6"
    CURRENT_SITE = ".current-site-name"

    def wait_until_loaded(self) -> "SiteSelectionPage":
        self.wait_for_url_contains("selectsite")
        self.wait_for_visible(self.SEARCH)
        self.wait_for_visible(self.SITE_TITLE)
        return self

    def is_loaded(self) -> bool:
        if "selectsite" not in self.get_url():
            return False
        return self.is_visible(self.SEARCH)

    def search(self, query: str) -> "SiteSelectionPage":
        logger.info("Searching site %s", query)
        self.fill(self.SEARCH, query)
        return self

    def visible_site_names(self) -> list[str]:
        return self.get_all_texts(self.SITE_TITLE)

    def has_site(self, name: str) -> bool:
        return name in self.visible_site_names()

    def select(self, name: str) -> None:
        logger.info("Selecting site %s", name)
        self.click(f'.cardBody:has(h6:text-is("{name}")) button:has-text("Access")')
        self.wait_for_url_not_contains("selectsite")

    def current_site_label(self) -> str:
        return self.get_text(self.CURRENT_SITE)
