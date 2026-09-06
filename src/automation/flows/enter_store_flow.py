from __future__ import annotations

from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.flows.open_module_flow import OpenModuleFlow
from automation.pages.store.store_nav_page import StoreNavPage
from automation.pages.store.store_workspace_page import StoreWorkspacePage


class EnterStoreFlow:
    """Login, open Store, pick site. Reuse before any Store tile test."""

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._page = page
        self._open_module = OpenModuleFlow(page, self._settings)

    def enter(self, site_name: str | None = None) -> StoreWorkspacePage:
        self._open_module.open_with_site("Store", site_name)
        StoreNavPage(self._page, self._settings).wait_until_ready()
        return StoreWorkspacePage(self._page, self._settings).wait_until_ready()
