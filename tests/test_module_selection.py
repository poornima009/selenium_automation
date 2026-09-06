from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.open_module_flow import OpenModuleFlow
from automation.pages.login_page import LoginPage
from automation.pages.module_selection_page import ModuleSelectionPage

EXPECTED_MODULES = [
    "NYGGS HRMS",
    "Planning & Billing",
    "Store",
    "Accounting",
    "P&M",
    "Tender Management",
]


def test_module_cards_are_visible(module_selection_page: ModuleSelectionPage) -> None:
    names = module_selection_page.module_names()

    assert module_selection_page.is_loaded()
    for name in EXPECTED_MODULES:
        assert name in names


def test_logout_returns_to_login(module_selection_page: ModuleSelectionPage) -> None:
    module_selection_page.logout()

    login_page = LoginPage(module_selection_page.page, module_selection_page.settings)
    login_page.wait_until_loaded()
    assert login_page.is_loaded()
    assert "modulesSelection" not in login_page.get_url()


def test_opening_store_opens_store_app(page: Page, settings: Settings) -> None:
    modules = OpenModuleFlow(page, settings).open("Store")

    modules.wait_for_url_contains("demossostore.nyggs.com")
    assert "modulesSelection" not in modules.get_url()
