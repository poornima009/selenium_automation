from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class TermsRecord:
    name: str
    content: str


class MasterTermsPage(BasePage):
    """Master > T&C form fields."""

    NAME = "label:has-text('Name') + div input"
    EDITOR = ".jodit-wysiwyg[contenteditable='true']"

    def fill_create(self, record: TermsRecord) -> None:
        logger.info("Filling T&C create form for %s", record.name)
        self._fill_name(record.name)
        self._fill_editor(record.content)

    def fill_update(self, name: str, content: str) -> None:
        logger.info("Updating T&C name to %s", name)
        self._fill_name(name)
        self._fill_editor(content)

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "T&C")

    def _fill_name(self, name: str) -> None:
        field = self.page.locator(self.NAME).first
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def _fill_editor(self, content: str) -> None:
        editor = self.page.locator(self.EDITOR).first
        editor.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        editor.click()
        editor.fill("")
        editor.press_sequentially(content)
        editor.press("Tab")
