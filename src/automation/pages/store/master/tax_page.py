from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class TaxRecord:
    name: str
    rate: str


class MasterTaxPage(BasePage):
    """Master > Tax form fields."""

    def fill_create(self, record: TaxRecord) -> None:
        logger.info("Filling Tax create form for %s", record.name)
        self.fill_labeled("Name", record.name)
        self.fill_labeled("Rate (%)", record.rate)

    def fill_update(self, name: str) -> None:
        logger.info("Updating Tax name to %s", name)
        field = self.labeled_control("Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Tax")
