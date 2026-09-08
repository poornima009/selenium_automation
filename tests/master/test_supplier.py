from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.permission_flow import MasterPermissionFlow
from automation.flows.master.supplier_flow import (
    MasterSupplierFlow,
    SupplierCreateBlockedError,
)
from automation.pages.store.master.bank_dialog import BankDetails
from automation.pages.store.master.supplier_page import SupplierRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage

ACCOUNT_PERMISSION_MODULE = "Contractor"
CRUD_OPERATIONS = ("add", "update", "approve")


def test_master_supplier_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    record = SupplierRecord(
        name=f"AUTO-SUPPLIER-{stamp}",
        pan_number=f"SUPCL{stamp[-4:]}X",
        contact_person=f"Person {stamp[-6:]}",
        email=f"supplier{stamp[-6:]}@example.com",
        contact_number=f"9{stamp[-9:]}",
        bank=BankDetails(
            account_number=stamp[-12:],
            account_holder=f"Supplier {stamp[-6:]}",
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

    flow = MasterSupplierFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Supplier create")
    except SupplierCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    flow.update(record.name, updated_contact, remark="AUTO Supplier update")
    assert flow.approve(record.name, remark="AUTO Supplier approve")

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    history = flow.track(record.name)
    assert "UPDATE" in history.upper() or "UPDATED" in history.upper()
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
