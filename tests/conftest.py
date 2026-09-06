from __future__ import annotations

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.core.browser import BrowserFactory
from automation.flows.login_flow import LoginFlow
from automation.pages.module_selection_page import ModuleSelectionPage


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
