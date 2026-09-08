from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class BankDetails:
    account_number: str = "100000000001"
    account_holder: str = "Automation Contractor"
    bank_name: str = "Automation Bank"
    ifsc_code: str = "AUTB0000001"


class MasterBankDialog(BasePage):
    """Reusable bank-detail dialog embedded in Master account forms."""

    OPEN = "text=Add Bank"
    SAVE = "button:has-text('Save Details')"

    def add(self, details: BankDetails) -> None:
        logger.info("Adding Master account bank details")
        self.click(self.OPEN)
        self.fill_labeled("Account Number", details.account_number)
        self.fill_labeled("Account Holder Name", details.account_holder)
        self.fill_labeled("Bank Name", details.bank_name)
        self.fill_labeled("IFSC Code", details.ifsc_code)
        self.click(self.SAVE)
        self.page.get_by_text("Add Bank Details", exact=True).wait_for(
            state="hidden", timeout=self.settings.default_timeout_ms
        )
