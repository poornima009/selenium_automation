from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class StoreRecord:
    name: str
    alias: str
    short_name: str
    incharge: str = "Demo admin"
    keeper: str = "Demo admin"
    address_line1: str = "Auto Lane 1"
    country: str = "INDIA"
    state: str = "DELHI"
    city: str = "Delhi"
    pin_code: str = "110001"
    phone: str = "9999999999"
    racks_sheet: str | None = None


class MasterStorePage(BasePage):
    """Master > Store add/update form fields."""

    INCHARGE = "input[name='StoreIncharge']"
    KEEPER = "input[name='StoreKeeper']"
    RACK_AVAILABLE = "label:has-text('Rack Available')"
    RACK_NAME = "input[placeholder='Press Enter To Add Rack']"
    RACK_FILE = "input[type='file'][accept*='csv']"
    ADD_ADDRESS = "svg[data-testid='AddCircleIcon']"
    ADDRESS_LINE1 = "[role='dialog'] input[name='addressLine1']"
    COUNTRY = "[role='dialog'] input[name='countryId']"
    STATE = "[role='dialog'] input[name='state']"
    CITY = "[role='dialog'] input[name='city']"
    PIN_CODE = "[role='dialog'] input[name='pinCode']"
    PHONE = "[role='dialog'] input[name='primaryPhoneNo']"
    SAVE_ADDRESS = "[role='dialog'] button:has-text('Save')"

    def fill_create(self, record: StoreRecord) -> None:
        logger.info("Filling Store create form for %s", record.name)
        self.fill_labeled("Store Name", record.name)
        self.fill_labeled("Alias Name", record.alias)
        self.fill_labeled("Short Name", record.short_name)
        self.select_autocomplete(self.INCHARGE, record.incharge)
        self.select_autocomplete(self.KEEPER, record.keeper)
        if record.racks_sheet:
            self.import_racks(record.racks_sheet)
        self._add_address(record)

    def import_racks(self, sheet_path: str) -> None:
        logger.info("Importing Store racks from %s", sheet_path)
        self.click(self.RACK_AVAILABLE)
        self.wait_for_visible(self.RACK_NAME)
        self.page.locator(self.RACK_FILE).first.set_input_files(sheet_path)
        self.wait_loading_gone()
        self.page.get_by_text("File Uploaded successfully", exact=False).first.wait_for(
            state="visible", timeout=self.settings.default_timeout_ms
        )
        first_rack = _first_rack_name(sheet_path)
        if first_rack:
            self.page.get_by_text(first_rack, exact=True).first.wait_for(
                state="visible", timeout=self.settings.default_timeout_ms
            )
        self.page.locator(self.RACK_NAME).first.press("Tab")
        self._dismiss_upload_alert()

    def _dismiss_upload_alert(self) -> None:
        alert = self.page.get_by_text("File Uploaded successfully", exact=False)
        try:
            alert.first.wait_for(state="hidden", timeout=8000)
        except Exception:
            return

    def fill_update(self, alias: str) -> None:
        logger.info("Updating Store alias to %s", alias)
        self._ensure_editable()
        field = self.labeled_control("Alias Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click()
        field.fill("")
        field.fill(alias)
        field.press("Tab")

    def _ensure_editable(self) -> None:
        if self._alias_is_visible(4000):
            return
        edit = self.page.get_by_role("button", name="Edit")
        if edit.count() and edit.first.is_visible():
            logger.info("Opening Store edit from view")
            edit.first.click()
            self.labeled_control("Alias Name").wait_for(
                state="visible", timeout=self.settings.default_timeout_ms
            )
            return
        icon = self.page.locator("svg[data-testid='EditIcon']")
        if icon.count() and icon.first.is_visible():
            icon.first.click()
            self.labeled_control("Alias Name").wait_for(
                state="visible", timeout=self.settings.default_timeout_ms
            )

    def clear_alias(self) -> None:
        logger.info("Clearing Store alias")
        self._ensure_editable()
        field = self.labeled_control("Alias Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click()
        field.fill("")
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Store")

    def wait_until_named(self, name: str) -> None:
        self.wait_loading_gone()
        back = self.page.locator("svg[data-testid='ArrowBackIcon']")
        try:
            back.first.wait_for(state="visible", timeout=8000)
        except Exception:
            pass
        self.page.get_by_text(name, exact=False).first.wait_for(
            state="visible", timeout=self.settings.default_timeout_ms
        )

    def shows_alias(self, alias: str) -> bool:
        return self._shows_labeled("Alias Name", alias)

    def _shows_labeled(self, label: str, value: str) -> bool:
        field = self.labeled_control(label)
        try:
            field.wait_for(state="visible", timeout=4000)
            current = field.input_value() or ""
            if value in current:
                return True
        except Exception:
            pass
        return self.page.get_by_text(value, exact=False).count() > 0

    def _alias_is_visible(self, timeout_ms: int) -> bool:
        try:
            field = self.labeled_control("Alias Name")
            field.wait_for(state="visible", timeout=timeout_ms)
            return field.is_editable()
        except Exception:
            return False

    def _add_address(self, record: StoreRecord) -> None:
        logger.info("Adding Store address")
        self.click(self.ADD_ADDRESS)
        self.wait_for_visible(self.ADDRESS_LINE1)
        self.fill(self.ADDRESS_LINE1, record.address_line1)
        self.select_autocomplete(self.COUNTRY, record.country)
        self.select_autocomplete(self.STATE, record.state)
        self.fill(self.CITY, record.city)
        self.fill(self.PIN_CODE, record.pin_code)
        self.fill(self.PHONE, record.phone)
        self.click(self.SAVE_ADDRESS)
        self.wait_for_hidden(self.ADDRESS_LINE1)


def _first_rack_name(sheet_path: str) -> str:
    lines = Path(sheet_path).read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:
        name = line.strip()
        if name:
            return name
    return ""
