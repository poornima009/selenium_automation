from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class ManufacturerModelRecord:
    name: str
    model: str


class MasterManufacturerModelPage(BasePage):
    """Master > Item > Manufacturer/Model form fields."""

    NAME = "input[name='taskName']"
    MODEL = "input[name='modal']"
    ADD_MODEL = "button:has-text('Add Model')"

    def fill_create(self, record: ManufacturerModelRecord) -> None:
        logger.info("Filling Manufacturer/Model form for %s", record.name)
        self.fill(self.NAME, record.name)
        self.fill(self.MODEL, record.model)
        self.click(self.ADD_MODEL)

    def fill_update(self, name: str) -> None:
        logger.info("Updating Manufacturer name to %s", name)
        field = self.page.locator(self.NAME).first
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Manufacturer/Model")
