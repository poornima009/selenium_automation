from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class ItemRecord:
    name: str
    alias: str
    hsn_code: str


class MasterItemsPage(BasePage):
    """Master > Item > Items form fields."""

    def fill_create(self, record: ItemRecord) -> None:
        logger.info("Filling Item create form for %s", record.name)
        self.fill_labeled("Item Name", record.name)
        self.fill_labeled("Alias", record.alias)
        self.fill_labeled("HSN Code", record.hsn_code)
        self.select_first_labeled("Primary Unit / Unit Type")
        self.select_first_labeled("Item Type")
        self.fill_labeled("GST %", "18")

    def fill_update(self, name: str) -> None:
        logger.info("Updating Item name to %s", name)
        field = self.labeled_control("Item Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Items")
