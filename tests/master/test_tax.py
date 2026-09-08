from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.tax_flow import MasterTaxFlow, TaxCreateBlockedError
from automation.pages.store.master.tax_page import TaxRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_tax_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = stamp.translate(str.maketrans("0123456789", "ABCDEFGHIJ"))
    record = TaxRecord(name=f"AUTOTAX{suffix}", rate="7.5")
    updated_name = f"UPDATEDTAX{suffix}"
    page, _workspace = store_session

    flow = MasterTaxFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Tax create")
    except TaxCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    listing = flow.update(
        record.name,
        updated_name,
        remark="AUTO Tax update",
    )
    assert listing.row_is_visible(updated_name)
    if not flow.approve(updated_name, remark="AUTO Tax approve"):
        pytest.xfail("Tax has no Approve action for the current role")

    listing = flow.find(updated_name)
    assert listing.row_is_visible(updated_name)

    history = flow.track(updated_name)
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
