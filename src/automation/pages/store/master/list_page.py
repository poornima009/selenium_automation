from __future__ import annotations

from playwright.sync_api import Locator

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


class MasterListPage(BasePage):
    """Shared Master list chrome: add, search, save, row actions, approve."""

    ADD = "button:has-text('+ Add'), button:has-text('Add')"
    SEARCH = "#serachInputBox"
    SAVE = (
        "button.MuiButton-containedPrimary:has-text('Create'), "
        "button.MuiButton-containedPrimary:has-text('Update'), "
        "button.MuiButton-containedPrimary:has-text('Save')"
    )
    APPROVE = (
        "button:has-text('Approve'), button:has-text('APPROVE'), "
        "svg[data-testid='ThumbUpIcon'], svg[data-testid='CheckCircleIcon'], "
        "svg[data-testid='TaskAltIcon']"
    )
    DELETE = (
        "button:has-text('Delete'), button:has-text('DELETE'), "
        "svg[data-testid='DeleteIcon'], svg[data-testid='DeleteOutlineIcon']"
    )
    TRACK = "svg[data-testid='HistoryIcon']"
    TRACK_BUTTON = "button:has(svg[data-testid='HistoryIcon'])"
    TRACK_PANEL = "[role='dialog'], .MuiDrawer-paper, .MuiPopover-paper"
    BACK = "svg[data-testid='ArrowBackIcon']"
    ROW = "table tbody tr"
    LIST_ADD = "button:has-text('+ Add')"
    FORM_FIELD = (
        "div.MuiFormControl-root input:not(#serachInputBox), "
        "div.MuiFormControl-root textarea"
    )
    NO_DATA = (
        "text=No Data Found, text=No data found, text=No Records, "
        "text=No Record Found, text=No rows"
    )
    HELPER = ".MuiFormHelperText-root, .Mui-error"

    def dismiss_menu(self) -> None:
        self.close_menu()

    def dismiss_overlay(self) -> None:
        if self.visible_dialog() is None:
            return
        logger.info("Dismissing leftover dialog")
        self.press_escape()
        dialog = self.visible_dialog()
        if dialog is None:
            return
        cancel = dialog.get_by_role("button", name="CANCEL", exact=False)
        if cancel.count() and cancel.first.is_visible():
            cancel.first.click(force=True)
            return
        self.press_escape()

    def search_is_visible(self) -> bool:
        return self.is_visible(self.SEARCH, timeout_ms=5000)

    def delete_is_visible(self) -> bool:
        return self.is_visible(self.DELETE, timeout_ms=2000)

    def add_is_enabled(self) -> bool:
        button = self.page.locator(self.LIST_ADD)
        return button.count() > 0 and button.first.is_visible() and button.first.is_enabled()

    def is_on_form(self) -> bool:
        return self._is_form_url(self.page.url)

    def open_add(self) -> None:
        logger.info("Opening Master add form")
        self.click(self.ADD)
        self.page.locator(self.FORM_FIELD).first.wait_for(
            state="visible", timeout=self.settings.default_timeout_ms
        )

    def search(self, name: str) -> None:
        logger.info("Searching Master list for %s", name)
        self.wait_for_visible(self.SEARCH)
        self.fill(self.SEARCH, name)
        self.press_enter(self.SEARCH)
        self.wait_loading_gone()
        try:
            self.row_locator(name).first.wait_for(state="visible", timeout=8000)
        except Exception:
            return

    def no_data_is_visible(self) -> bool:
        return self.is_visible(self.NO_DATA, timeout_ms=3000)

    def helper_text(self) -> str:
        helper = self.page.locator(self.HELPER)
        if helper.count() == 0:
            return ""
        return (helper.first.inner_text() or "").strip()

    def row_locator(self, name: str) -> Locator:
        return self.page.locator(self.ROW).filter(has_text=name)

    def row_is_visible(self, name: str) -> bool:
        return self.row_locator(name).count() > 0 and self.row_locator(name).first.is_visible()

    def row_count(self, name: str) -> int:
        return self.row_locator(name).count()

    def row_state(self, name: str) -> str:
        status = self.row_locator(name).locator(".status-component")
        if status.count() == 0:
            return ""
        return (status.first.inner_text() or "").strip()

    def row_text(self, name: str) -> str:
        if not self.row_is_visible(name):
            return ""
        return (self.row_locator(name).first.inner_text() or "").strip()

    def open_row(self, name: str) -> None:
        logger.info("Opening Master row %s", name)
        self.close_menu()
        row = self.row_locator(name)
        row.first.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        self._click_row_open(row, name)
        self.wait_loading_gone()
        self._open_edit_if_view()
        self._wait_for_form()

    def _click_row_open(self, row: Locator, name: str) -> None:
        for testid in ("EditIcon", "ModeEditIcon", "ModeEditOutlineIcon", "VisibilityIcon"):
            icon = row.locator(f"svg[data-testid='{testid}']")
            if icon.count() and icon.first.is_visible():
                icon.first.evaluate("el => el.click()")
                return
        row.get_by_text(name, exact=False).first.evaluate("el => el.click()")

    def _open_edit_if_view(self) -> None:
        if self.save_is_visible():
            return
        if self._wait_form_if_open(2000) and self.save_is_visible():
            return
        edit = self.page.get_by_role("button", name="Edit")
        if edit.count() and edit.first.is_visible():
            logger.info("Opening edit from view")
            edit.first.click()
            self.wait_loading_gone()
            return
        icon = self.page.locator("svg[data-testid='EditIcon']")
        if icon.count() and icon.first.is_visible():
            icon.first.click()
            self.wait_loading_gone()

    def save_is_visible(self) -> bool:
        for label in ("Create", "Update", "Save", "UPDATE", "CREATE"):
            button = self.page.get_by_role("button", name=label, exact=False)
            if button.count() and button.first.is_visible():
                return True
        icon = self.page.locator("button:has(svg[data-testid='SaveIcon'])")
        return icon.count() > 0 and icon.first.is_visible()

    def _wait_form_if_open(self, timeout_ms: int) -> bool:
        try:
            self.page.locator(self.FORM_FIELD).first.wait_for(
                state="visible", timeout=timeout_ms
            )
            return True
        except Exception:
            return self.is_on_form()

    def _wait_for_form(self) -> None:
        if self._wait_form_if_open(self.settings.default_timeout_ms):
            return
        self.page.locator(self.FORM_FIELD).first.wait_for(
            state="visible", timeout=self.settings.default_timeout_ms
        )

    def save(self) -> None:
        logger.info("Saving Master form")
        for label in ("Create", "Update", "Save", "UPDATE", "CREATE"):
            button = self.page.get_by_role("button", name=label, exact=False)
            if button.count() == 0 or not button.first.is_visible():
                continue
            logger.info("Clicking save button %s", label)
            self.click_action(button.first)
            return
        icon = self.page.locator("button:has(svg[data-testid='SaveIcon'])")
        if icon.count() and icon.first.is_visible():
            self.click_action(icon.first)
            return
        if not self.save_is_visible():
            logger.info("No save button on this screen")
            return
        self.click(self.SAVE)

    def confirm(self, remark: str | None = None) -> None:
        self.confirm_action(remark=remark)

    def wait_after_save(self) -> None:
        self.wait_loading_gone()
        dialog = self.visible_dialog()
        if dialog is None:
            return
        ok = dialog.get_by_role("button", name="OK")
        if ok.count() and ok.first.is_visible():
            ok.first.click(force=True)
            self.wait_loading_gone()

    def open_track(self, name: str) -> str:
        logger.info("Opening Store track history for %s", name)
        self.close_menu()
        row = self.row_locator(name)
        row.first.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        row.first.hover()
        self._click_track(row)
        self.wait_loading_gone()
        text = self._track_text()
        if not text:
            logger.info("Track panel did not open")
        self.press_escape()
        return text

    def _click_track(self, row: Locator) -> None:
        button = row.locator(self.TRACK_BUTTON)
        if button.count() and button.last.is_visible():
            logger.info("Clicking track action button")
            button.last.click(force=True)
            return
        icon = row.locator(self.TRACK)
        if icon.count() == 0:
            logger.info("No track icon on row")
            return
        icon.last.evaluate(
            "el => { const host = el.closest('button') || el.parentElement; host.click(); }"
        )

    def _track_text(self) -> str:
        marker = self.page.locator("text=/Updated|Approved|Created|UPDATE|APPROVE/i")
        try:
            marker.last.wait_for(state="visible", timeout=8000)
        except Exception:
            return self.dialog_text()
        panel = self.page.locator(self.TRACK_PANEL)
        if panel.count() and panel.last.is_visible():
            return (panel.last.inner_text() or "").strip()
        return (marker.last.inner_text() or "").strip()

    def wait_until_on_list(self) -> None:
        self.wait_loading_gone()
        if self.visible_dialog() is not None:
            self.dismiss_overlay()
        if self.is_on_form():
            self.go_back()
            self.wait_loading_gone()
        if self.search_is_visible():
            return

    def _is_form_url(self, url: str) -> bool:
        lowered = url.lower()
        return "add" in lowered or "update" in lowered

    def approve_is_visible(self) -> bool:
        button = self.page.get_by_role("button", name="Approve", exact=False)
        try:
            button.first.wait_for(state="visible", timeout=2000)
            return True
        except Exception:
            return False

    def approve(self, remark: str | None = None) -> bool:
        button = self.page.get_by_role("button", name="Approve", exact=False)
        try:
            button.first.wait_for(state="visible", timeout=5000)
        except Exception:
            logger.info("Approve button not on this screen")
            return False
        logger.info("Approving Master record")
        self.click_action(button.first)
        self.confirm(remark=remark)
        return True

    def go_back(self) -> None:
        if not self.is_visible(self.BACK, timeout_ms=2000):
            return
        self.click(self.BACK, force=True)
