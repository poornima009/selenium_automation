from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class SiteGroupingRecord:
    name: str


class MasterSiteGroupingPage(BasePage):
    """Master > Site Grouping form fields."""

    SITE = "input[name='Select Site']"

    def fill_create(self, record: SiteGroupingRecord) -> None:
        logger.info("Filling Site Grouping create form for %s", record.name)
        self.fill_labeled("Site Grouping Name", record.name)
        self._select_first_site()

    def fill_update(self, name: str) -> None:
        logger.info("Updating Site Grouping name to %s", name)
        field = self.labeled_control("Site Grouping Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Site Grouping")

    def _select_first_site(self) -> None:
        field = self.page.locator(self.SITE).first
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click()
        option = self.page.get_by_role("option").first
        option.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        option.click()
        self.press_escape()
