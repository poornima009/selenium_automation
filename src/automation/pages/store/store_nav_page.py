from __future__ import annotations

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


class StoreNavPage(BasePage):
    """Hover-and-click Store top menu. Works for every tile and nested child."""

    CURRENT_SITE = ".current-site-name"
    PARENT = 'li.nav-item:has(.nav-item-name-div:text-is("{name}"))'
    CHILD = '.dropdown-portal .nested-nav-item:has(span:text-is("{name}"))'

    def wait_until_ready(self) -> "StoreNavPage":
        self.wait_for_visible(self.CURRENT_SITE)
        self.wait_for_visible(self.PARENT.format(name="Dashboard"))
        return self

    def parent_names(self) -> list[str]:
        return self.get_all_texts("li.nav-item .nav-item-name-div")

    def open_path(self, *names: str) -> None:
        if not names:
            raise ValueError("open_path requires at least one menu name")
        logger.info("Opening Store path %s", " > ".join(names))
        if len(names) == 1:
            self.click(self.PARENT.format(name=names[0]))
            return
        self.hover(self.PARENT.format(name=names[0]))
        self.wait_for_visible(self.CHILD.format(name=names[1]))
        for name in names[1:-1]:
            self.hover(self.CHILD.format(name=name))
        self._click_nested(names[-1])
        self.wait_until_ready()

    def _click_nested(self, name: str) -> None:
        item = self.page.locator(self.CHILD.format(name=name)).first
        item.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        scroller = self.page.locator(".dropdown-content, .dropdown-portal").first
        for _ in range(12):
            box = item.bounding_box()
            height = self.page.viewport_size["height"] if self.page.viewport_size else 800
            if box and 0 < box["y"] < height - 20:
                break
            scroller.evaluate("el => { el.scrollTop += 140; }")
        logger.info("Clicking nested menu %s", name)
        item.evaluate("el => el.click()")
