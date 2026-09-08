from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.other_location_flow import (
    MasterOtherLocationFlow,
    OtherLocationCreateBlockedError,
    OtherLocationWorkflowUnavailableError,
)
from automation.pages.store.master.other_location_page import OtherLocationRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_other_location_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = stamp.translate(str.maketrans("0123456789", "ABCDEFGHIJ"))
    record = OtherLocationRecord(
        name=f"AUTOLOCATION{suffix}",
        latitude="28.6139",
        longitude="77.2090",
        radius="100",
    )
    updated_name = f"UPDATEDLOCATION{suffix}"
    page, _workspace = store_session

    flow = MasterOtherLocationFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Other Location create")
    except (
        OtherLocationCreateBlockedError,
        OtherLocationWorkflowUnavailableError,
    ) as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    listing = flow.update(
        record.name,
        updated_name,
        remark="AUTO Other Location update",
    )
    assert listing.row_is_visible(updated_name)
    if not flow.approve(updated_name, remark="AUTO Other Location approve"):
        pytest.xfail("Other Location has no Approve action for the current role")

    listing = flow.find(updated_name)
    assert listing.row_is_visible(updated_name)

    history = flow.track(updated_name)
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
