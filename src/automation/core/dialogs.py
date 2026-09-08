from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from automation.core.logger import get_logger

logger = get_logger(__name__)

DIALOG = "[role='dialog']"
CONFIRM_LABELS = ("CREATE", "UPDATE", "APPROVE", "CONFIRM", "YES", "OK", "Save")


def visible_dialog(page: Page) -> Locator | None:
    dialogs = page.locator(DIALOG)
    for index in range(dialogs.count() - 1, -1, -1):
        node = dialogs.nth(index)
        if node.is_visible():
            return node
    return None


def dialog_text(page: Page) -> str:
    dialog = visible_dialog(page)
    if dialog is None:
        return ""
    return (dialog.inner_text() or "").strip()[:240]


def wait_loading_gone(page: Page, timeout_ms: int) -> None:
    loader = page.get_by_text("Loading...", exact=True)
    try:
        loader.first.wait_for(state="hidden", timeout=timeout_ms)
    except Exception:
        return


def confirm_action(
    page: Page,
    timeout_ms: int,
    labels: tuple[str, ...] = CONFIRM_LABELS,
    remark: str | None = None,
) -> bool:
    if not _wait_for_confirm_button(page, timeout_ms):
        logger.info("No confirm action dialog")
        return False
    dialog = visible_dialog(page)
    if dialog is None:
        return False
    if remark:
        _fill_remark(dialog, remark)
    for label in labels:
        button = dialog.locator("button").filter(has_text=re.compile(rf"^{label}$", re.I))
        if button.count() == 0 or not button.last.is_visible():
            continue
        logger.info("Confirming dialog with %s", label)
        button.last.scroll_into_view_if_needed()
        button.last.evaluate("el => el.scrollIntoView({block: 'center', inline: 'nearest'})")
        button.last.click()
        _wait_dialog_hidden(dialog, timeout_ms)
        if visible_dialog(page) is not None:
            button.last.evaluate("el => el.click()")
            _wait_dialog_hidden(dialog, timeout_ms)
        wait_loading_gone(page, timeout_ms)
        return True
    logger.info("Dialog without confirm button: %s", dialog_text(page))
    return False


def _fill_remark(dialog: Locator, remark: str) -> None:
    field = dialog.locator(
        "textarea, input[placeholder*='Remark' i], input[name*='remark' i], "
        "input[placeholder*='comment' i]"
    )
    if field.count() == 0:
        logger.info("No remark field on confirm dialog")
        return
    logger.info("Filling confirm remark")
    target = field.last
    target.click()
    target.fill(remark)
    target.press("Tab")


def _wait_for_confirm_button(page: Page, timeout_ms: int) -> bool:
    try:
        page.locator(
            f"{DIALOG} button:has-text('CREATE'), "
            f"{DIALOG} button:has-text('UPDATE'), "
            f"{DIALOG} button:has-text('APPROVE')"
        ).last.wait_for(state="visible", timeout=min(timeout_ms, 8000))
        return True
    except Exception:
        return visible_dialog(page) is not None


def _wait_dialog_hidden(dialog: Locator, timeout_ms: int) -> None:
    try:
        dialog.wait_for(state="hidden", timeout=min(timeout_ms, 8000))
    except Exception:
        logger.info("Dialog still open after confirm")
