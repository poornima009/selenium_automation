import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.core.browser import BrowserFactory
from automation.flows.enter_store_flow import EnterStoreFlow
from automation.pages.store.store_menu import store_leaf_paths
from automation.pages.store.store_nav_page import StoreNavPage
from automation.pages.store.store_workspace_page import StoreWorkspacePage

LEAF_PATHS = store_leaf_paths()


@pytest.fixture(scope="module")
def store_session():
    settings = get_settings()
    factory = BrowserFactory(settings)
    page = factory.start()
    workspace = EnterStoreFlow(page, settings).enter()
    try:
        yield page, settings, workspace
    finally:
        factory.stop()


def test_store_dashboard_shows_site_and_widgets(store_session) -> None:
    page, settings, workspace = store_session
    nav = StoreNavPage(page, settings)
    nav.open_path("Dashboard")

    assert workspace.is_on_store()
    assert settings.site_name in workspace.get_text(workspace.CURRENT_SITE)
    assert workspace.is_dashboard()


@pytest.mark.parametrize("path", LEAF_PATHS, ids=lambda p: " > ".join(p))
def test_store_tile_opens(store_session, path: tuple[str, ...]) -> None:
    page, settings, _workspace = store_session
    nav = StoreNavPage(page, settings)
    workspace = StoreWorkspacePage(page, settings)
    nav.open_path(*path)

    assert workspace.is_on_store()
    assert "selectsite" not in workspace.get_url()
    assert workspace.has_listing_or_form() or workspace.is_dashboard()
