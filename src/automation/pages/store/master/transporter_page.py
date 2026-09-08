from __future__ import annotations

from dataclasses import dataclass, replace

from automation.core.base_page import BasePage
from automation.core.logger import get_logger
from automation.pages.store.master.address_dialog import AddressDetails, MasterAddressDialog
from automation.pages.store.master.bank_dialog import BankDetails, MasterBankDialog

logger = get_logger(__name__)


@dataclass(frozen=True)
class TransporterRecord:
    name: str
    pan_number: str
    contact_person: str
    email: str
    contact_number: str
    bank: BankDetails = BankDetails()
    address: AddressDetails = AddressDetails()


class MasterTransporterPage(BasePage):
    """Master > Account > Transporter form fields."""

    TRANSPORTER_MAPPING = "label.MuiFormControlLabel-root:has-text('Transporter')"
    PAN_NOT_LINKED = "button:text-is('No')"

    def fill_create(self, record: TransporterRecord) -> None:
        logger.info("Filling Transporter create form for %s", record.name)
        self.fill_labeled("Transporter Name", record.name)
        self.fill_labeled("Email", record.email)
        self.fill_labeled("PAN No", record.pan_number)
        self.fill_labeled("Contact Person Name", record.contact_person)
        self._fill_contact_number(record.contact_number)
        self.click(self.PAN_NOT_LINKED)
        self._select_transporter_mapping()
        MasterBankDialog(self.page, self.settings).add(record.bank)
        address = record.address
        if not address.gst_number:
            address = replace(address, gst_number=f"07{record.pan_number}1Z5")
        MasterAddressDialog(self.page, self.settings).add(address)

    def fill_update(self, contact_person: str) -> None:
        logger.info("Updating Transporter contact person to %s", contact_person)
        field = self.labeled_control("Contact Person Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click()
        field.fill("")
        field.fill(contact_person)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Transporter")

    def _fill_contact_number(self, value: str) -> None:
        for label in ("Contact Person No", "Contact No"):
            field = self.labeled_control(label)
            try:
                field.wait_for(state="visible", timeout=1000)
                field.fill(value)
                return
            except Exception:
                continue

    def _select_transporter_mapping(self) -> None:
        mapping = self.locator(self.TRANSPORTER_MAPPING)
        checkbox = mapping.locator("input[type='checkbox']")
        if checkbox.is_checked():
            return
        logger.info("Selecting Transporter account mapping")
        mapping.click()
