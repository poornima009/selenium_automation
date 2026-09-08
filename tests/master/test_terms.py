from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.terms_flow import MasterTermsFlow, TermsCreateBlockedError
from automation.pages.store.master.terms_page import TermsRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_terms_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = stamp.translate(str.maketrans("0123456789", "ABCDEFGHIJ"))
    record = TermsRecord(
        name=f"AUTOTERMS{suffix}",
        content="Automated terms and conditions.",
    )
    updated_name = f"UPDATEDTERMS{suffix}"
    page, _workspace = store_session

    flow = MasterTermsFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO T&C create")
    except TermsCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    listing = flow.update(
        record.name,
        updated_name,
        content="Updated automated terms and conditions.",
        remark="AUTO T&C update",
    )
    assert listing.row_is_visible(updated_name)
    if not flow.approve(updated_name, remark="AUTO T&C approve"):
        pytest.xfail("T&C has no Approve action for the current role")

    listing = flow.find(updated_name)
    assert listing.row_is_visible(updated_name)

    history = flow.track(updated_name)
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
