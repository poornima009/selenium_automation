from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.site_grouping_flow import (
    MasterSiteGroupingFlow,
    SiteGroupingCreateBlockedError,
)
from automation.pages.store.master.site_grouping_page import SiteGroupingRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_site_grouping_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = stamp.translate(str.maketrans("0123456789", "ABCDEFGHIJ"))
    record = SiteGroupingRecord(name=f"AUTOSITEGROUP{suffix}")
    updated_name = f"UPDATEDSITEGROUP{suffix}"
    page, _workspace = store_session

    flow = MasterSiteGroupingFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Site Grouping create")
    except SiteGroupingCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    listing = flow.update(
        record.name,
        updated_name,
        remark="AUTO Site Grouping update",
    )
    assert listing.row_is_visible(updated_name)
    if not flow.approve(updated_name, remark="AUTO Site Grouping approve"):
        pytest.xfail("Site Grouping has no Approve action for the current role")

    listing = flow.find(updated_name)
    assert listing.row_is_visible(updated_name)

    history = flow.track(updated_name)
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
