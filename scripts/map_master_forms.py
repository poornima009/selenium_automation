"""Dump live Master add-form fields. Not part of the pytest suite."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from automation.config.settings import get_settings
from automation.core.browser import BrowserFactory
from automation.flows.enter_store_flow import EnterStoreFlow
from automation.pages.store.master.entities import master_entities
from automation.pages.store.master.list_page import MasterListPage
from automation.pages.store.store_nav_page import StoreNavPage


def _dump_form(page) -> dict:
    labels = []
    for node in page.locator("label").all()[:40]:
        text = (node.inner_text() or "").strip().replace("\n", " ")
        if text:
            labels.append(text[:80])
    buttons = [
        (node.inner_text() or "").strip()
        for node in page.locator("button").all()[:40]
        if (node.inner_text() or "").strip()
    ]
    dialog = page.locator("[role='dialog']")
    dialog_text = ""
    if dialog.count() and dialog.first.is_visible():
        dialog_text = (dialog.first.inner_text() or "").strip()[:240]
    return {
        "url": page.url,
        "labels": labels,
        "buttons": buttons[:20],
        "primary": [t.strip() for t in page.locator("button.MuiButton-containedPrimary").all_inner_texts() if t.strip()][:10],
        "textareas": page.locator("textarea").count(),
        "dialog": dialog.count(),
        "dialog_text": dialog_text,
    }


def main() -> None:
    settings = get_settings()
    factory = BrowserFactory(settings)
    page = factory.start()
    EnterStoreFlow(page, settings).enter()
    nav = StoreNavPage(page, settings)
    listing = MasterListPage(page, settings)
    report = []
    try:
        for entity in master_entities(kind="list"):
            nav.open_path(*entity.path)
            listing.dismiss_overlay()
            item = {
                "key": entity.key,
                "add_enabled": listing.add_is_enabled(),
                "list_url": page.url,
            }
            if not item["add_enabled"]:
                report.append(item)
                continue
            listing.open_add()
            page.locator("label").first.wait_for(timeout=settings.default_timeout_ms)
            item["form"] = _dump_form(page)
            listing.dismiss_overlay()
            listing.go_back()
            listing.dismiss_overlay()
            if listing.is_visible(listing.SEARCH, timeout_ms=3000):
                listing.wait_for_visible(listing.SEARCH)
            report.append(item)
        print(json.dumps(report, indent=2))
    finally:
        factory.stop()


if __name__ == "__main__":
    main()
