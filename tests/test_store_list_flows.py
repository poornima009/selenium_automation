import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.pages.store.store_menu import STORE_LIST_PATHS
from automation.pages.store.store_nav_page import StoreNavPage
from automation.pages.store.store_workspace_page import StoreWorkspacePage


@pytest.mark.parametrize("path", STORE_LIST_PATHS, ids=lambda p: " > ".join(p))
def test_store_list_add_form_opens_and_cancels(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    path: tuple[str, ...],
) -> None:
    page, workspace = store_session
    nav = StoreNavPage(page, settings)
    nav.open_path(*path)

    assert workspace.has_listing_or_form()
    opened = workspace.open_add_form()
    if not opened:
        pytest.skip(f"No Add/Create action on {' > '.join(path)}")

    workspace.leave_form_without_saving()
    assert workspace.is_on_store()
