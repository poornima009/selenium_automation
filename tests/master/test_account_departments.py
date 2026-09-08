from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.account_departments_flow import (
    AccountDepartmentsCreateBlockedError,
    MasterAccountDepartmentsFlow,
)
from automation.pages.store.master.account_departments_page import (
    AccountDepartmentsRecord,
)
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_account_departments_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = stamp.translate(str.maketrans("0123456789", "ABCDEFGHIJ"))
    record = AccountDepartmentsRecord(
        name=f"AUTOACCOUNTDEPARTMENT{suffix}",
        pan_number=f"ABCDE{stamp[-4:]}F",
        contact_person_name=f"AUTOCONTACT{suffix}",
        contact_number=stamp[-10:],
    )
    updated_name = f"UPDATEDACCOUNTDEPARTMENT{suffix}"
    page, _workspace = store_session

    flow = MasterAccountDepartmentsFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Account Department create")
    except AccountDepartmentsCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    listing = flow.update(
        record.name,
        updated_name,
        remark="AUTO Account Department update",
    )
    assert listing.row_is_visible(updated_name)
    if not flow.approve(updated_name, remark="AUTO Account Department approve"):
        pytest.xfail("Account Departments has no Approve action for the current role")

    listing = flow.find(updated_name)
    assert listing.row_is_visible(updated_name)

    history = flow.track(updated_name)
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
