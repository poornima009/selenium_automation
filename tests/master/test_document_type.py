from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.document_type_flow import (
    DocumentTypeCreateBlockedError,
    MasterDocumentTypeFlow,
)
from automation.pages.store.master.document_type_page import DocumentTypeRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_document_type_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    record = DocumentTypeRecord(name=f"AUTO-DOC-{stamp}")
    updated_name = f"UPDATED-DOC-{stamp}"
    page, _workspace = store_session

    flow = MasterDocumentTypeFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Document Type create")
    except DocumentTypeCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    listing = flow.update(
        record.name,
        updated_name,
        remark="AUTO Document Type update",
    )
    assert listing.row_is_visible(updated_name)
    if not flow.approve(updated_name, remark="AUTO Document Type approve"):
        pytest.xfail(
            "Document Type has no Approve action for the current role and is "
            "not available in the Permission matrix"
        )

    listing = flow.find(updated_name)
    assert listing.row_is_visible(updated_name)

    history = flow.track(updated_name)
    assert "UPDATE" in history.upper() or "UPDATED" in history.upper()
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
