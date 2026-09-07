from __future__ import annotations

from automation.core.base_page import BasePage


class StoreWorkspacePage(BasePage):
    """Assertions shared by every Store screen after site access."""

    CURRENT_SITE = ".current-site-name"
    DASHBOARD_MARK = "text=Billing Status"
    TABLE = "table, .MuiTable-root"
    ADD = (
        "button:has-text('Add'), button:has-text('Create'), "
        "button:has-text('New'), a:has-text('Add')"
    )
    SEARCH = (
        "input[placeholder*='Search'], textarea[placeholder*='Search'], "
        "input[type='search']"
    )
    BACK = "button:has-text('Back'), button:has-text('Cancel'), button:has-text('Close')"

    def wait_until_ready(self) -> "StoreWorkspacePage":
        self.wait_for_visible(self.CURRENT_SITE)
        return self

    def is_on_store(self) -> bool:
        return "demossostore.nyggs.com" in self.get_url()

    def is_dashboard(self) -> bool:
        return self.is_visible(self.DASHBOARD_MARK, timeout_ms=4000)

    def has_listing_or_form(self) -> bool:
        if self.is_visible(self.TABLE, timeout_ms=4000):
            return True
        if self.is_visible(self.ADD, timeout_ms=2000):
            return True
        if self.is_visible(self.SEARCH, timeout_ms=2000):
            return True
        return self.is_on_store() and "selectsite" not in self.get_url()

    def open_add_form(self) -> bool:
        if not self.is_visible(self.ADD, timeout_ms=5000):
            return False
        self.click(self.ADD)
        return True

    def leave_form_without_saving(self) -> None:
        if self.is_visible(self.BACK, timeout_ms=4000):
            self.click(self.BACK)
            return
        self.page.go_back()
        self.wait_until_ready()
