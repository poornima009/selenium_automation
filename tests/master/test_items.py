from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.items_flow import ItemCreateBlockedError, MasterItemsFlow
from automation.pages.store.master.items_page import ItemRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_items_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = stamp.translate(str.maketrans("0123456789", "ABCDEFGHIJ"))[-6:]
    record = ItemRecord(
        name=f"AUTOITEM{suffix}",
        alias=f"A{stamp[-6:]}",
        hsn_code=stamp[-8:],
    )
    updated_name = f"UPDATEDITEM{suffix}"
    page, _workspace = store_session

    flow = MasterItemsFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Item create")
    except ItemCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    listing = flow.update(
        record.name,
        updated_name,
        remark="AUTO Item update",
    )
    assert listing.row_is_visible(updated_name)
    if not flow.approve(updated_name, remark="AUTO Item approve"):
        pytest.xfail("Items has no Approve action for the current role")

    listing = flow.find(updated_name)
    assert listing.row_is_visible(updated_name)

    history = flow.track(updated_name)
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
