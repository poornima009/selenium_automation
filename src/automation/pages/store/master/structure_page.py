from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class StructureRecord:
    name: str
    latitude: str
    longitude: str


class MasterStructurePage(BasePage):
    """Master > Location > Structure form fields."""

    def fill_create(self, record: StructureRecord) -> None:
        logger.info("Filling Structure create form for %s", record.name)
        self.fill_labeled("Name", record.name)
        self.fill_labeled("Latitude", record.latitude)
        self.fill_labeled("Longitude", record.longitude)

    def fill_update(self, name: str) -> None:
        logger.info("Updating Structure name to %s", name)
        field = self.labeled_control("Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Structure")
