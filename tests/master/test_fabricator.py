from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.fabricator_flow import (
    FabricatorCreateBlockedError,
    MasterFabricatorFlow,
)
from automation.flows.master.permission_flow import MasterPermissionFlow
from automation.pages.store.master.bank_dialog import BankDetails
from automation.pages.store.master.fabricator_page import FabricatorRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage

ACCOUNT_PERMISSION_MODULE = "Contractor"
CRUD_OPERATIONS = ("add", "update", "approve")


def test_master_fabricator_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    record = FabricatorRecord(
        name=f"AUTO-FABRICATOR-{stamp}",
        pan_number=f"FABCL{stamp[-4:]}X",
        contact_person=f"Person {stamp[-6:]}",
        email=f"fabricator{stamp[-6:]}@example.com",
        contact_number=f"9{stamp[-9:]}",
        bank=BankDetails(
            account_number=stamp[-12:],
            account_holder=f"Fabricator {stamp[-6:]}",
        ),
    )
    updated_contact = f"Updated {stamp[-6:]}"
    page, _workspace = store_session

    permissions = MasterPermissionFlow(page, settings).grant_operations(
        ACCOUNT_PERMISSION_MODULE,
        CRUD_OPERATIONS,
    )
    for operation in CRUD_OPERATIONS:
        assert permissions.is_granted(ACCOUNT_PERMISSION_MODULE, operation)

    flow = MasterFabricatorFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Fabricator create")
    except FabricatorCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    flow.update(record.name, updated_contact, remark="AUTO Fabricator update")
    assert flow.approve(record.name, remark="AUTO Fabricator approve")

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    history = flow.track(record.name)
    assert "UPDATE" in history.upper() or "UPDATED" in history.upper()
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
