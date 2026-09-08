from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class DesignationRecord:
    name: str


class MasterDesignationPage(BasePage):
    """Master > Employees > Designation form fields."""

    def fill_create(self, record: DesignationRecord) -> None:
        logger.info("Filling Designation create form for %s", record.name)
        self.fill_labeled("Designation Name", record.name)

    def fill_update(self, name: str) -> None:
        logger.info("Updating Designation name to %s", name)
        field = self.labeled_control("Designation Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Designation")
