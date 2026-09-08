from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.core.browser import BrowserFactory
from automation.core.logger import get_logger
from automation.core.reporting import ReportManager
from automation.flows.enter_store_flow import EnterStoreFlow
from automation.flows.login_flow import LoginFlow
from automation.pages.module_selection_page import ModuleSelectionPage
from automation.pages.store.store_nav_page import StoreNavPage
from automation.pages.store.store_workspace_page import StoreWorkspacePage

logger = get_logger(__name__)
_report_manager: ReportManager | None = None
_report_path: Path | None = None


def pytest_sessionstart(session: pytest.Session) -> None:
    global _report_manager
    _report_manager = ReportManager(Path(str(session.config.rootpath)))


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    if _report_manager is not None:
        _report_manager.register_tests(items)


def pytest_deselected(items: list[pytest.Item]) -> None:
    if _report_manager is not None:
        _report_manager.mark_deselected(items)


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
    if _report_manager is not None:
        _report_manager.record_report(report)
    if not report.failed:
        return
    page = _page_for_failure(item)
    if page is None or page.is_closed() or _report_manager is None:
        return
    path = _report_manager.screenshot_path(item.nodeid)
    try:
        page.screenshot(path=str(path), full_page=True)
        _report_manager.attach_screenshot(item.nodeid, path)
    except Exception:
        logger.exception("Could not capture failure screenshot for %s", item.nodeid)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    global _report_path
    if _report_manager is not None:
        _report_path = _report_manager.finish(exitstatus)


def pytest_terminal_summary(terminalreporter) -> None:
    if _report_path is None:
        return
    terminalreporter.write_sep("=", f"HTML report: {_report_path}")


def _page_for_failure(item: pytest.Item) -> Page | None:
    page = item.funcargs.get("page")
    if page is not None:
        return page
    store_session = item.funcargs.get("store_session")
    if store_session is None:
        return None
    return store_session[0]
