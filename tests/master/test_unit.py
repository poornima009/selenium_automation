from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.unit_flow import (
    MasterUnitFlow,
    UnitCreateBlockedError,
)
from automation.pages.store.master.unit_page import UnitRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_unit_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name_suffix = stamp.translate(str.maketrans("0123456789", "ABCDEFGHIJ"))
    record = UnitRecord(
        name=f"AUTOUNIT{name_suffix}",
        unit_type="weight",
        abbreviation=f"A{stamp[-3:]}",
        conversion_into_kg="1",
    )
    updated_name = f"UPDATEDUNIT{name_suffix}"
    updated_abbreviation = f"U{stamp[-3:]}"
    page, _workspace = store_session

    flow = MasterUnitFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Unit create")
    except UnitCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    listing = flow.update(
        record.name,
        updated_name,
        updated_abbreviation,
        remark="AUTO Unit update",
    )
    assert listing.row_is_visible(updated_name)
    if not flow.approve(updated_name, remark="AUTO Unit approve"):
        pytest.xfail("Unit has no Approve action for the current role")

    listing = flow.find(updated_name)
    assert listing.row_is_visible(updated_name)

    history = flow.track(updated_name)
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
