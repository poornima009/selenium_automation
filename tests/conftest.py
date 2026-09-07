from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.core.browser import BrowserFactory
from automation.core.logger import get_logger
from automation.flows.enter_store_flow import EnterStoreFlow
from automation.flows.login_flow import LoginFlow
from automation.pages.module_selection_page import ModuleSelectionPage
from automation.pages.store.store_nav_page import StoreNavPage
from automation.pages.store.store_workspace_page import StoreWorkspacePage

logger = get_logger(__name__)


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture
def page(settings: Settings) -> Page:
    factory = BrowserFactory(settings)
    browser_page = factory.start()
    try:
        yield browser_page
    finally:
        factory.stop()


@pytest.fixture
def module_selection_page(page: Page, settings: Settings) -> ModuleSelectionPage:
    return LoginFlow(page, settings).login_to_module_selection()


class _StoreBrowser:
    """One SSO login for Store tests. Recreates the browser if the page dies."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._factory: BrowserFactory | None = None
        self.page: Page | None = None
        self.workspace: StoreWorkspacePage | None = None

    def start(self) -> None:
        self.stop()
        self._factory = BrowserFactory(self._settings)
        self.page = self._factory.start()
        self.workspace = EnterStoreFlow(self.page, self._settings).enter()

    def stop(self) -> None:
        if self._factory is None:
            return
        self._factory.stop()
        self._factory = None
        self.page = None
        self.workspace = None

    def session(self) -> tuple[Page, StoreWorkspacePage]:
        if self.page is None or self.page.is_closed():
            logger.info("Store session lost; logging in again")
            self.start()
        assert self.page is not None
        assert self.workspace is not None
        StoreNavPage(self.page, self._settings).prepare()
        return self.page, self.workspace


@pytest.fixture(scope="session")
def _store_browser(settings: Settings) -> _StoreBrowser:
    browser = _StoreBrowser(settings)
    browser.start()
    yield browser
    browser.stop()


@pytest.fixture(scope="module")
def store_session(_store_browser: _StoreBrowser):
    yield _store_browser.session()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    session = item.funcargs.get("store_session")
    if session is None:
        return
    page, _workspace = session
    if page.is_closed():
        return
    folder = Path("reports/failures")
    folder.mkdir(parents=True, exist_ok=True)
    name = item.nodeid.replace("/", "_").replace("::", "_").replace(" ", "_")
    page.screenshot(path=str(folder / f"{name}.png"))
