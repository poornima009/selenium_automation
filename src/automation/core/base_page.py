from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from automation.config.settings import Settings, get_settings
from automation.core.dialogs import (
    confirm_action,
    dialog_text,
    visible_dialog,
    wait_loading_gone,
)
from automation.core.logger import get_logger
from automation.core.waits import wait_for_url_contains, wait_for_url_not_contains, wait_for_visible

logger = get_logger(__name__)

_ACTION_TOP = 88
_ACTION_BOTTOM = 48
_SCROLL_STEP = 360


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

    def click(self, selector: str, *, force: bool = False) -> None:
        logger.info("Clicking %s", selector)
        self.wait_for_visible(selector)
        target = self.locator(selector)
        self.click_action(target, force=force)

    def click_action(self, target: Locator, *, force: bool = False) -> None:
        self.scroll_action_into_view(target)
        target.click(force=force)

    def scroll_up(self) -> None:
        logger.info("Scrolling up")
        self.page.mouse.wheel(0, -_SCROLL_STEP)

    def scroll_down(self) -> None:
        logger.info("Scrolling down")
        self.page.mouse.wheel(0, _SCROLL_STEP)

    def scroll_action_into_view(self, target: Locator) -> None:
        logger.info("Scrolling to next action")
        for _ in range(8):
            target.evaluate("el => el.scrollIntoView({block: 'center', inline: 'nearest'})")
            box = target.bounding_box()
            if box is None or self._is_in_click_band(box):
                return
            if box["y"] < _ACTION_TOP:
                self.scroll_up()
            else:
                self.scroll_down()

    def _is_in_click_band(self, box: dict) -> bool:
        height = self.page.viewport_size["height"] if self.page.viewport_size else 800
        top = box["y"]
        bottom = box["y"] + box["height"]
        return top >= _ACTION_TOP and bottom <= height - _ACTION_BOTTOM

    def hover(self, selector: str) -> None:
        logger.info("Hovering %s", selector)
        self.wait_for_visible(selector)
        self.locator(selector).hover()

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

    def press_escape(self) -> None:
        self.page.keyboard.press("Escape")

    def close_menu(self) -> None:
        portal = self.page.locator(".dropdown-portal")
        if portal.count() == 0 or not portal.first.is_visible():
            return
        logger.info("Closing leftover menu")
        self.press_escape()
        if portal.count() == 0 or not portal.first.is_visible():
            return
        logger.info("Disabling leftover menu portal")
        portal.evaluate_all(
            "nodes => nodes.forEach(n => { n.style.pointerEvents = 'none'; n.style.visibility = 'hidden'; })"
        )

    def wait_for_hidden(self, selector: str) -> None:
        self.page.locator(selector).first.wait_for(
            state="hidden", timeout=self.settings.default_timeout_ms
        )

    def labeled_control(self, label: str) -> Locator:
        return (
            self.page.locator("label")
            .filter(has_text=re.compile(rf"^{re.escape(label)}"))
            .locator("xpath=ancestor::div[contains(@class,'MuiFormControl')][1]")
            .locator("input, textarea")
            .first
        )

    def fill_labeled(self, label: str, value: str) -> None:
        logger.info("Filling labeled field %s", label)
        field = self.labeled_control(label)
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill(value)

    def select_autocomplete(self, selector: str, option: str) -> None:
        logger.info("Selecting %s on %s", option, selector)
        self.click(selector)
        self.fill(selector, option)
        choice = self.page.locator("[role='option']").filter(has_text=option).first
        choice.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        choice.click()

    def select_first_labeled(self, label: str) -> None:
        logger.info("Selecting first option for %s", label)
        field = self.labeled_control(label)
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click()
        choice = self.page.locator("[role='option']").first
        choice.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        choice.click()

    def alert_is_visible(self, timeout_ms: int = 8000) -> bool:
        return self.is_visible("[role='alert']", timeout_ms)

    def alert_text(self, timeout_ms: int = 8000) -> str:
        if not self.alert_is_visible(timeout_ms):
            return ""
        return self.get_text("[role='alert']")

    def visible_dialog(self) -> Locator | None:
        return visible_dialog(self.page)

    def dialog_text(self) -> str:
        return dialog_text(self.page)

    def wait_loading_gone(self) -> None:
        wait_loading_gone(self.page, self.settings.default_timeout_ms)

    def confirm_action(
        self,
        labels: tuple[str, ...] | None = None,
        remark: str | None = None,
    ) -> bool:
        if labels is None:
            return confirm_action(
                self.page, self.settings.default_timeout_ms, remark=remark
            )
        return confirm_action(
            self.page, self.settings.default_timeout_ms, labels, remark
        )
