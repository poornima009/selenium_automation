from __future__ import annotations

from dataclasses import dataclass, replace

from automation.core.base_page import BasePage
from automation.core.logger import get_logger
from automation.pages.store.master.address_dialog import AddressDetails, MasterAddressDialog
from automation.pages.store.master.bank_dialog import BankDetails, MasterBankDialog

logger = get_logger(__name__)


@dataclass(frozen=True)
class ContractorRecord:
    name: str
    pan_number: str
    contact_person: str
    email: str
    contact_number: str
    bank: BankDetails = BankDetails()
    address: AddressDetails = AddressDetails()


class MasterContractorPage(BasePage):
    """Master > Account > Contractor form fields."""

    CONTRACTOR_MAPPING = "label.MuiFormControlLabel-root:has-text('Contractor')"
    PAN_NOT_LINKED = "button:text-is('No')"

    def fill_create(self, record: ContractorRecord) -> None:
        logger.info("Filling Contractor create form for %s", record.name)
        self.fill_labeled("Contractor Name", record.name)
        self.fill_labeled("Email", record.email)
        self.fill_labeled("Pan No", record.pan_number)
        self.fill_labeled("Contact Person Name", record.contact_person)
        self.fill_labeled("Contact No", record.contact_number)
        self.click(self.PAN_NOT_LINKED)
        self._select_contractor_mapping()
        MasterBankDialog(self.page, self.settings).add(record.bank)
        address = record.address
        if not address.gst_number:
            address = replace(address, gst_number=f"07{record.pan_number}1Z5")
        MasterAddressDialog(self.page, self.settings).add(address)

    def fill_update(self, contact_person: str) -> None:
        logger.info("Updating Contractor contact person to %s", contact_person)
        field = self.labeled_control("Contact Person Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click()
        field.fill("")
        field.fill(contact_person)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Contractor")

    def _select_contractor_mapping(self) -> None:
        mapping = self.locator(self.CONTRACTOR_MAPPING)
        checkbox = mapping.locator("input[type='checkbox']")
        if checkbox.is_checked():
            return
        logger.info("Selecting Contractor account mapping")
        mapping.click()
