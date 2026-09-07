from __future__ import annotations

from playwright.sync_api import Locator

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


class MasterPermissionPage(BasePage):
    """Master > Permission role matrix."""

    MODULE_SEARCH = "input[placeholder='Search modules...']"
    SAVE_MODULE = "button:has-text('Save Module')"
    EXPAND = "svg[data-testid='ExpandMoreIcon']"
    HEADING = "text=Permissions"

    def select_role(self, role: str) -> None:
        logger.info("Selecting Permission role %s", role)
        field = (
            self.page.locator("label")
            .filter(has_text="Role")
            .locator("xpath=ancestor::div[contains(@class,'MuiFormControl')][1]//input")
            .first
        )
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click(force=True)
        field.fill(role)
        choice = self.page.locator("[role='option']").filter(has_text=role).first
        try:
            choice.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
            choice.click(force=True)
        except Exception:
            self.press_escape()
        self.wait_for_visible(self.EXPAND)

    def filter_module(self, name: str) -> None:
        logger.info("Filtering Permission module %s", name)
        self.fill(self.MODULE_SEARCH, name)

    def _module_row(self, name: str) -> Locator:
        return self.page.get_by_text(name, exact=True).first.locator(
            "xpath=ancestor::div[contains(@class,'MuiBox-root')][2]"
        )

    def _operation(self, module: str, operation: str) -> Locator:
        return (
            self._module_row(module)
            .locator("label.MuiFormControlLabel-root")
            .filter(has_text=operation)
            .first
        )

    def expand_module(self, name: str) -> None:
        if self.is_visible(self.SAVE_MODULE, timeout_ms=1500):
            return
        logger.info("Expanding Permission module %s", name)
        self._module_row(name).locator(self.EXPAND).first.click(force=True)
        self.wait_for_visible(self.SAVE_MODULE)

    def is_granted(self, module: str, operation: str) -> bool:
        css = self._operation(module, operation).locator("span.MuiCheckbox-root").get_attribute("class")
        return "Mui-checked" in (css or "")

    def grant(self, module: str, operation: str) -> None:
        logger.info("Granting %s on %s", operation, module)
        box = self._operation(module, operation)
        if not self.is_granted(module, operation):
            box.click()
        box.locator("span.MuiCheckbox-root.Mui-checked").wait_for(
            timeout=self.settings.default_timeout_ms
        )

    def save_module(self) -> None:
        logger.info("Saving Permission module")
        self.click(self.SAVE_MODULE)
