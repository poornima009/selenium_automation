from __future__ import annotations

from pathlib import Path

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


class MasterChainagePage(BasePage):
    """Master > Location > Chainage import form."""

    UPLOAD = "input[type='file'][name='cancelCheque']"

    def fill_import(self, workbook: Path, position: str = "Start") -> None:
        logger.info("Uploading Chainage workbook %s", workbook.name)
        field = self.labeled_control("Select Position")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click()
        field.press("ArrowDown")
        option = self.page.get_by_role("option", name=position, exact=True)
        option.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        option.click()
        self.page.locator(self.UPLOAD).set_input_files(workbook)

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Chainage")
