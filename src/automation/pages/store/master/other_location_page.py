from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Locator

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class OtherLocationRecord:
    name: str
    latitude: str
    longitude: str
    radius: str


class MasterOtherLocationPage(BasePage):
    """Master > Location > Other Location form fields."""

    def fill_create(self, record: OtherLocationRecord) -> None:
        logger.info("Filling Other Location create form for %s", record.name)
        self._fill("Name", record.name)
        self._fill("Latitude", record.latitude)
        self._fill("Longitude", record.longitude)
        self._fill("Radius", record.radius)

    def fill_update(self, name: str) -> None:
        logger.info("Updating Other Location name to %s", name)
        field = self._field("Name")
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Other Location")

    def _fill(self, label: str, value: str) -> None:
        field = self._field(label)
        field.fill(value)

    def _field(self, label: str) -> Locator:
        field = self.page.get_by_label(label, exact=False).first
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        return field
