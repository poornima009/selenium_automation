from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.permission_flow import (
    PERMISSION_MODULE,
    MasterPermissionFlow,
)
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_permission_01_add(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    page, _workspace = store_session
    form = MasterPermissionFlow(page, settings).grant("add")

    assert form.is_granted(PERMISSION_MODULE, "add")


def test_master_permission_02_update(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    page, _workspace = store_session
    form = MasterPermissionFlow(page, settings).grant("update")

    assert form.is_granted(PERMISSION_MODULE, "update")


def test_master_permission_03_approve(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    page, _workspace = store_session
    form = MasterPermissionFlow(page, settings).grant("approve")

    assert form.is_granted(PERMISSION_MODULE, "approve")
