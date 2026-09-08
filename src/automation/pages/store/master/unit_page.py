from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class UnitRecord:
    name: str
    unit_type: str
    abbreviation: str
    conversion_into_kg: str


class MasterUnitPage(BasePage):
    """Master > Item > Unit form fields."""

    def fill_create(self, record: UnitRecord) -> None:
        logger.info("Filling Unit create form for %s", record.name)
        self.fill_labeled("Name", record.name)
        self._select_type(record.unit_type)
        self.fill_labeled("Abbreviation", record.abbreviation)
        self.fill_labeled("Conversion into KG", record.conversion_into_kg)

    def fill_update(self, name: str, abbreviation: str) -> None:
        logger.info("Updating Unit name to %s", name)
        self._replace_labeled("Name", name)
        self._replace_labeled("Abbreviation", abbreviation)

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Unit")

    def _select_type(self, unit_type: str) -> None:
        field = self.labeled_control("Type")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click()
        option = self.page.get_by_role("option", name=unit_type, exact=True)
        option.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        option.click()

    def _replace_labeled(self, label: str, value: str) -> None:
        field = self.labeled_control(label)
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(value)
        field.press("Tab")
