from __future__ import annotations

from playwright.sync_api import Page


def wait_for_visible(page: Page, selector: str, timeout_ms: int) -> None:
    page.locator(selector).first.wait_for(state="visible", timeout=timeout_ms)


def wait_for_url_contains(page: Page, text: str, timeout_ms: int) -> None:
    if text in page.url:
        return
    page.wait_for_url(lambda url: text in url, timeout=timeout_ms)


def wait_for_url_not_contains(page: Page, text: str, timeout_ms: int) -> None:
    if text not in page.url:
        return
    page.wait_for_url(lambda url: text not in url, timeout=timeout_ms)
