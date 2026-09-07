from __future__ import annotations

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


class StoreNavPage(BasePage):
    """Hover-and-click Store top menu. Works for every tile and nested child."""

    CURRENT_SITE = ".current-site-name"
    PARENT = 'li.nav-item:has(.nav-item-name-div:text-is("{name}"))'
    BRANCH = '.dropdown-portal .nested-nav-item:has(span:text-is("{name}"))'
    LEAF = (
        '.dropdown-portal .nested-nav-item:has(span:text-is("{name}"))'
        ":not(:has(.nested-nav-item))"
    )
    DASHBOARD = "Dashboard"

    def prepare(self) -> None:
        self._close_dialog()
        self.close_menu()

    def go_home(self) -> None:
        logger.info("Returning to Store Dashboard")
        self._close_dialog()
        self.close_menu()
        self._open_dashboard()

    def wait_until_ready(self) -> "StoreNavPage":
        self.wait_for_visible(self.CURRENT_SITE)
        self.wait_for_visible(self.PARENT.format(name=self.DASHBOARD))
        return self

    def parent_names(self) -> list[str]:
        return self.get_all_texts("li.nav-item .nav-item-name-div")

    def open_path(self, *names: str) -> None:
        if not names:
            raise ValueError("open_path requires at least one menu name")
        logger.info("Opening Store path %s", " > ".join(names))
        self._close_dialog()
        if names[0] != self.DASHBOARD:
            self._open_dashboard()
        if names == (self.DASHBOARD,):
            return
        if len(names) == 1:
            self.click(self.PARENT.format(name=names[0]), force=True)
            self.wait_until_ready()
            return
        self.hover(self.PARENT.format(name=names[0]))
        self.wait_for_visible(self.BRANCH.format(name=names[1]))
        for name in names[1:-1]:
            self.hover(self.BRANCH.format(name=name))
        self._click_nested(names[-1])
        self.wait_until_ready()
        self.close_menu()

    def _open_dashboard(self) -> None:
        logger.info("Resetting Store menu from Dashboard")
        self.click(self.PARENT.format(name=self.DASHBOARD), force=True)
        self.wait_until_ready()

    def _close_dialog(self) -> None:
        if self.visible_dialog() is None:
            return
        logger.info("Closing dialog before menu navigation")
        self.press_escape()

    def _click_nested(self, name: str) -> None:
        item = self.page.locator(self.LEAF.format(name=name)).first
        item.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        scroller = self.page.locator(".dropdown-content, .dropdown-portal").last
        for _ in range(12):
            box = item.bounding_box()
            height = self.page.viewport_size["height"] if self.page.viewport_size else 800
            if box and 0 < box["y"] < height - 20:
                break
            scroller.evaluate("el => { el.scrollTop += 140; }")
        logger.info("Clicking nested menu %s", name)
        item.click(force=True)
