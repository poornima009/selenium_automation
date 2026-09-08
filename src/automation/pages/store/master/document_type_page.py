from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class DocumentTypeRecord:
    name: str


class MasterDocumentTypePage(BasePage):
    """Master > Document Type form fields."""

    def fill_create(self, record: DocumentTypeRecord) -> None:
        logger.info("Filling Document Type create form for %s", record.name)
        self.fill_labeled("Document Type Name", record.name)

    def fill_update(self, name: str) -> None:
        logger.info("Updating Document Type name to %s", name)
        field = self.labeled_control("Document Type Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click()
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Document Type")
