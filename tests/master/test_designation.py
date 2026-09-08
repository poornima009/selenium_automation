from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.designation_flow import (
    DesignationCreateBlockedError,
    MasterDesignationFlow,
)
from automation.pages.store.master.designation_page import DesignationRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_designation_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = stamp.translate(str.maketrans("0123456789", "ABCDEFGHIJ"))
    record = DesignationRecord(name=f"AUTODESIGNATION{suffix}")
    updated_name = f"UPDATEDDESIGNATION{suffix}"
    page, _workspace = store_session

    flow = MasterDesignationFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Designation create")
    except DesignationCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    listing = flow.update(
        record.name,
        updated_name,
        remark="AUTO Designation update",
    )
    assert listing.row_is_visible(updated_name)
    if not flow.approve(updated_name, remark="AUTO Designation approve"):
        pytest.xfail("Designation has no Approve action for the current role")

    listing = flow.find(updated_name)
    assert listing.row_is_visible(updated_name)

    history = flow.track(updated_name)
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
