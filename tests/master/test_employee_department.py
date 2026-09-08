from __future__ import annotations

from datetime import datetime

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.employee_department_flow import (
    EmployeeDepartmentCreateBlockedError,
    MasterEmployeeDepartmentFlow,
)
from automation.pages.store.master.employee_department_page import (
    EmployeeDepartmentRecord,
)
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_employee_department_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = stamp.translate(str.maketrans("0123456789", "ABCDEFGHIJ"))
    record = EmployeeDepartmentRecord(name=f"AUTODEPARTMENT{suffix}")
    updated_name = f"UPDATEDDEPARTMENT{suffix}"
    page, _workspace = store_session

    flow = MasterEmployeeDepartmentFlow(page, settings)
    try:
        listing = flow.create(record, remark="AUTO Employee Department create")
    except EmployeeDepartmentCreateBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    listing = flow.update(
        record.name,
        updated_name,
        remark="AUTO Employee Department update",
    )
    assert listing.row_is_visible(updated_name)
    if not flow.approve(updated_name, remark="AUTO Employee Department approve"):
        pytest.xfail("Employee Department has no Approve action for the current role")

    listing = flow.find(updated_name)
    assert listing.row_is_visible(updated_name)

    history = flow.track(updated_name)
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
