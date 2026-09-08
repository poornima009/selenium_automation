from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class AccountDepartmentsRecord:
    name: str
    pan_number: str
    contact_person_name: str
    contact_number: str


class MasterAccountDepartmentsPage(BasePage):
    """Master > Account > Departments form fields."""

    def fill_create(self, record: AccountDepartmentsRecord) -> None:
        logger.info("Filling Account Departments form for %s", record.name)
        self.fill_labeled("Department Name", record.name)
        self.fill_labeled("PAN No", record.pan_number)
        self.fill_labeled("Contact Person Name", record.contact_person_name)
        self.fill_labeled("Contact No", record.contact_number)

    def fill_update(self, name: str) -> None:
        logger.info("Updating Account Department name to %s", name)
        field = self.labeled_control("Department Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Account Departments")
