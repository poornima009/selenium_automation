from __future__ import annotations

from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.flows.login_flow import LoginFlow
from automation.pages.module_selection_page import ModuleSelectionPage
from automation.pages.site_selection_page import SiteSelectionPage


class OpenModuleFlow:
    """Login, open a module card, optionally pick a site. Reused by every product."""

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._page = page
        self._login_flow = LoginFlow(page, self._settings)
        self._modules = ModuleSelectionPage(page, self._settings)

    def open(self, module_name: str) -> ModuleSelectionPage:
        self._login_flow.login_to_module_selection()
        self._modules.open_module(module_name)
        return self._modules

    def open_with_site(self, module_name: str, site_name: str | None = None) -> SiteSelectionPage:
        self.open(module_name)
        site = SiteSelectionPage(self._page, self._settings).wait_until_loaded()
        chosen = site_name or self._settings.site_name
        site.search(chosen)
        site.select(chosen)
        return site
