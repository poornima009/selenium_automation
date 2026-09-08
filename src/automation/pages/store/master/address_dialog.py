from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class AddressDetails:
    line1: str = "Auto Lane 1"
    country: str = "INDIA"
    state: str = "DELHI"
    city: str = "Delhi"
    pin_code: str = "110001"
    phone: str = "9999999999"
    secondary_phone: str = "9888888888"
    gst_number: str = ""


class MasterAddressDialog(BasePage):
    """Reusable address dialog embedded in Master account forms."""

    OPEN = "text=Add Address"
    LINE1 = (
        "input[name='addressLine1'], input[placeholder*='Address Line 1']"
    )
    COUNTRY = (
        "input[name='countryId'], input[placeholder*='Country']"
    )
    STATE = (
        "input[name='state'], input[placeholder*='State']"
    )
    CITY = (
        "input[name='city'], input[placeholder*='City']"
    )
    PIN_CODE = (
        "input[name='pinCode'], input[placeholder*='Pin Code']"
    )
    PHONE = (
        "input[name='primaryPhoneNo'], input[name='primaryNumber'], "
        "input[placeholder*='Primary Number']"
    )
    SECONDARY_PHONE = (
        "input[name='secondaryNumber'], input[placeholder*='Secondary Number']"
    )
    GST_NUMBER = "input[name='GstNo'], input[placeholder*='GST Number']"
    SAVE = (
        "button:has-text('Save Address'), "
        "[role='dialog'] button:has-text('Save')"
    )

    def add(self, details: AddressDetails) -> None:
        logger.info("Adding Master account address")
        self.click(self.OPEN)
        self.wait_for_visible(self.LINE1)
        self.fill(self.LINE1, details.line1)
        self.select_autocomplete(self.COUNTRY, details.country)
        self.select_autocomplete(self.STATE, details.state)
        self.fill(self.CITY, details.city)
        self.fill(self.PIN_CODE, details.pin_code)
        self.fill(self.PHONE, details.phone)
        self._fill_if_visible(self.SECONDARY_PHONE, details.secondary_phone)
        self._fill_if_visible(self.GST_NUMBER, details.gst_number)
        self.click(self.SAVE)
        self.wait_for_hidden(self.LINE1)

    def _fill_if_visible(self, selector: str, value: str) -> None:
        if not value or not self.is_visible(selector, timeout_ms=1000):
            return
        self.fill(selector, value)
