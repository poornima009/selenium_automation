from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class EmployeeDepartmentRecord:
    name: str


class MasterEmployeeDepartmentPage(BasePage):
    """Master > Employees > Department form fields."""

    NAME = "input[required][maxlength='64']"

    def fill_create(self, record: EmployeeDepartmentRecord) -> None:
        logger.info("Filling Employee Department create form for %s", record.name)
        self.fill(self.NAME, record.name)

    def fill_update(self, name: str) -> None:
        logger.info("Updating Employee Department name to %s", name)
        field = self.page.locator(self.NAME).first
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Employee Department")
