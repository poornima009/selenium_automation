from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class EmployeeTypeRecord:
    name: str


class MasterEmployeeTypePage(BasePage):
    """Master > Employees > Employee Type form fields."""

    def fill_create(self, record: EmployeeTypeRecord) -> None:
        logger.info("Filling Employee Type create form for %s", record.name)
        self.fill_labeled("Employee Type Name", record.name)

    def fill_update(self, name: str) -> None:
        logger.info("Updating Employee Type name to %s", name)
        field = self.labeled_control("Employee Type Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Employee Type")
