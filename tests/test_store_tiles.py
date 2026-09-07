import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.pages.store.store_menu import store_leaf_paths
from automation.pages.store.store_nav_page import StoreNavPage
from automation.pages.store.store_workspace_page import StoreWorkspacePage

LEAF_PATHS = store_leaf_paths()


def test_store_dashboard_shows_site_and_widgets(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    page, workspace = store_session
    nav = StoreNavPage(page, settings)
    nav.open_path("Dashboard")

    assert workspace.is_on_store()
    assert settings.site_name in workspace.get_text(workspace.CURRENT_SITE)
    assert workspace.is_dashboard()


@pytest.mark.parametrize("path", LEAF_PATHS, ids=lambda p: " > ".join(p))
def test_store_tile_opens(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    path: tuple[str, ...],
) -> None:
    page, _workspace = store_session
    nav = StoreNavPage(page, settings)
    workspace = StoreWorkspacePage(page, settings)
    nav.open_path(*path)

    assert workspace.is_on_store()
    assert "selectsite" not in workspace.get_url()
    assert workspace.has_listing_or_form() or workspace.is_dashboard()
