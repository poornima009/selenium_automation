from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.open_module_flow import OpenModuleFlow
from automation.pages.site_selection_page import SiteSelectionPage


def test_search_filters_demo_site(page: Page, settings: Settings) -> None:
    OpenModuleFlow(page, settings).open("Store")
    site_page = SiteSelectionPage(page, settings).wait_until_loaded()
    site_page.search(settings.site_name)

    names = site_page.visible_site_names()
    assert settings.site_name in names
    assert names == [settings.site_name]


def test_select_demo_site_opens_module_home(page: Page, settings: Settings) -> None:
    site_page = OpenModuleFlow(page, settings).open_with_site("Store")

    assert "selectsite" not in site_page.get_url()
    assert settings.site_name in site_page.current_site_label()
