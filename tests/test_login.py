from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.login_flow import LoginFlow
from automation.pages.login_page import LoginPage


def test_valid_login_opens_module_selection(page: Page, settings: Settings) -> None:
    login_page = LoginFlow(page, settings).login_as()

    login_page.wait_for_url_contains("modulesSelection")
    assert login_page.is_on_module_selection()


def test_invalid_password_stays_on_login(page: Page, settings: Settings) -> None:
    login_page = LoginFlow(page, settings).login_as(
        username=settings.username,
        password="wrong-password",
    )

    assert login_page.is_loaded()
    assert login_page.error_message_visible()
    assert "modulesSelection" not in login_page.get_url()


def test_empty_fields_do_not_leave_login(page: Page, settings: Settings) -> None:
    login_page = LoginPage(page, settings).open()
    login_page.login("", "")

    assert login_page.is_loaded()
    assert "modulesSelection" not in login_page.get_url()
