from __future__ import annotations

from playwright.sync_api import Locator, Page

from automation.config.settings import Settings, get_settings
from automation.core.logger import get_logger
from automation.core.waits import wait_for_url_contains, wait_for_url_not_contains, wait_for_visible

logger = get_logger(__name__)


class BasePage:
    """Shared UI actions. Page objects subclass this; tests do not call Playwright."""

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self.page = page
        self.settings = settings or get_settings()

    def goto(self, url: str) -> None:
        logger.info("Opening %s", url)
        self.page.goto(url, wait_until="domcontentloaded")

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector).first

    def wait_for_visible(self, selector: str) -> None:
        wait_for_visible(self.page, selector, self.settings.default_timeout_ms)

    def fill(self, selector: str, value: str) -> None:
        logger.info("Filling %s", selector)
        self.wait_for_visible(selector)
        self.locator(selector).fill(value)

    def click(self, selector: str) -> None:
        logger.info("Clicking %s", selector)
        self.wait_for_visible(selector)
        self.locator(selector).click()

    def get_text(self, selector: str) -> str:
        self.wait_for_visible(selector)
        return (self.locator(selector).inner_text() or "").strip()

    def get_all_texts(self, selector: str) -> list[str]:
        self.wait_for_visible(selector)
        return [text.strip() for text in self.page.locator(selector).all_inner_texts() if text.strip()]

    def is_visible(self, selector: str, timeout_ms: int = 5000) -> bool:
        try:
            wait_for_visible(self.page, selector, timeout_ms)
            return True
        except Exception:
            return False

    def get_url(self) -> str:
        return self.page.url

    def wait_for_url_contains(self, text: str) -> None:
        wait_for_url_contains(self.page, text, self.settings.default_timeout_ms)

    def wait_for_url_not_contains(self, text: str) -> None:
        wait_for_url_not_contains(self.page, text, self.settings.default_timeout_ms)

    def press_enter(self, selector: str) -> None:
        self.wait_for_visible(selector)
        self.locator(selector).press("Enter")

    def alert_is_visible(self, timeout_ms: int = 8000) -> bool:
        return self.is_visible("[role='alert']", timeout_ms)

    def alert_text(self, timeout_ms: int = 8000) -> str:
        if not self.alert_is_visible(timeout_ms):
            return ""
        return self.get_text("[role='alert']")
