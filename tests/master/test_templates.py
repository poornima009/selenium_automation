from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.templates_flow import (
    MasterTemplatesFlow,
    TemplateCreateBlockedError,
)
from automation.pages.store.master.templates_page import TemplateRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_templates_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = stamp.translate(str.maketrans("0123456789", "ABCDEFGHIJ"))
    record = TemplateRecord(name=f"AUTOTEMPLATE{suffix[-6:]}")
    updated_name = f"UPDATEDTEMPLATE{suffix[-6:]}"
    page, _workspace = store_session

    flow = MasterTemplatesFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Template create")
    except TemplateCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    listing = flow.update(
        record.name,
        updated_name,
        remark="AUTO Template update",
    )
    assert listing.row_is_visible(updated_name)
    if not flow.approve(updated_name, remark="AUTO Template approve"):
        pytest.xfail("Templates has no Approve action for the current role")

    listing = flow.find(updated_name)
    assert listing.row_is_visible(updated_name)

    history = flow.track(updated_name)
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
