from __future__ import annotations

from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.pages.login_page import LoginPage
from automation.pages.module_selection_page import ModuleSelectionPage


class LoginFlow:
    """Reusable login sequence for any later module test."""

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._page = page
        self._login_page = LoginPage(page, self._settings)

    def login_as(self, username: str | None = None, password: str | None = None) -> LoginPage:
        user = username if username is not None else self._settings.username
        secret = password if password is not None else self._settings.password
        self._login_page.open()
        self._login_page.login(user, secret)
        return self._login_page

    def login_to_module_selection(
        self,
        username: str | None = None,
        password: str | None = None,
    ) -> ModuleSelectionPage:
        self.login_as(username, password)
        return ModuleSelectionPage(self._page, self._settings).wait_until_loaded()
