from __future__ import annotations

from datetime import datetime
from secrets import token_hex

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.crud_flow import MasterCrudFlow
from automation.pages.store.master.entities import MasterEntity
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def unique_name(prefix: str = "AT") -> str:
    return f"{prefix}{datetime.now().strftime('%H%M%S')}{token_hex(2)}"


def run_list_crud(
    page: Page,
    settings: Settings,
    entity: MasterEntity,
) -> None:
    name = unique_name()
    updated = unique_name("UT")
    flow = MasterCrudFlow(page, settings, entity.key)
    listing = flow.open()
    if not listing.add_is_enabled():
        pytest.skip(f"No Add on {' > '.join(entity.path)}")

    listing = flow.create(name)
    assert listing.row_is_visible(name), f"{entity.key} add did not list {name}"

    listing = flow.update(name, updated)
    target = updated if listing.row_is_visible(updated) else name
    assert listing.row_is_visible(target), f"{entity.key} update did not keep the row"

    if not flow.approve(target):
        return
    listing = flow.open()
    listing.search(target)
    state = listing.row_state(target).upper()
    assert "APPROVED" in state or listing.row_is_visible(target)


def run_view(
    page: Page,
    settings: Settings,
    workspace: StoreWorkspacePage,
    entity: MasterEntity,
) -> None:
    MasterCrudFlow(page, settings, entity.key).open()
    assert workspace.is_on_store()
    assert workspace.has_listing_or_form()
