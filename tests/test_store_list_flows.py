import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.enter_store_flow import EnterStoreFlow
from automation.pages.store.store_menu import STORE_LIST_PATHS
from automation.pages.store.store_nav_page import StoreNavPage
from automation.pages.store.store_workspace_page import StoreWorkspacePage


@pytest.fixture
def store_workspace(page: Page, settings: Settings) -> StoreWorkspacePage:
    return EnterStoreFlow(page, settings).enter()


@pytest.mark.parametrize("path", STORE_LIST_PATHS, ids=lambda p: " > ".join(p))
def test_store_list_add_form_opens_and_cancels(
    page: Page,
    settings: Settings,
    store_workspace: StoreWorkspacePage,
    path: tuple[str, ...],
) -> None:
    nav = StoreNavPage(page, settings)
    nav.open_path(*path)

    assert store_workspace.has_listing_or_form()
    opened = store_workspace.open_add_form()
    if not opened:
        pytest.skip(f"No Add/Create action on {' > '.join(path)}")

    store_workspace.leave_form_without_saving()
    assert store_workspace.is_on_store()
