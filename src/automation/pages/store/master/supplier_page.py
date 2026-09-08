from __future__ import annotations

from dataclasses import dataclass, replace

from automation.core.base_page import BasePage
from automation.core.logger import get_logger
from automation.pages.store.master.address_dialog import AddressDetails, MasterAddressDialog
from automation.pages.store.master.bank_dialog import BankDetails, MasterBankDialog

logger = get_logger(__name__)


@dataclass(frozen=True)
class SupplierRecord:
    name: str
    pan_number: str
    contact_person: str
    email: str
    contact_number: str
    bank: BankDetails = BankDetails()
    address: AddressDetails = AddressDetails()


class MasterSupplierPage(BasePage):
    """Master > Account > Supplier form fields."""

    VENDOR_MAPPING = "label.MuiFormControlLabel-root:has-text('Vendor')"
    PAN_NOT_LINKED = "button:text-is('No')"

    def fill_create(self, record: SupplierRecord) -> None:
        logger.info("Filling Supplier create form for %s", record.name)
        self.fill_labeled("Vendor Name", record.name)
        self.fill_labeled("Email", record.email)
        self.fill_labeled("PAN No", record.pan_number)
        self.fill_labeled("Contact Person Name", record.contact_person)
        self.fill_labeled("Contact Person No", record.contact_number)
        self.click(self.PAN_NOT_LINKED)
        self._select_vendor_mapping()
        MasterBankDialog(self.page, self.settings).add(record.bank)
        address = record.address
        if not address.gst_number:
            address = replace(address, gst_number=f"07{record.pan_number}1Z5")
        MasterAddressDialog(self.page, self.settings).add(address)

    def fill_update(self, contact_person: str) -> None:
        logger.info("Updating Supplier contact person to %s", contact_person)
        field = self.labeled_control("Contact Person Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click()
        field.fill("")
        field.fill(contact_person)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Supplier")

    def _select_vendor_mapping(self) -> None:
        mapping = self.locator(self.VENDOR_MAPPING)
        checkbox = mapping.locator("input[type='checkbox']")
        if checkbox.is_checked():
            return
        logger.info("Selecting Vendor account mapping")
        mapping.click()
