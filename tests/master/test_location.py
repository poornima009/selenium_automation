import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.pages.store.master.entities import master_entities
from automation.pages.store.store_workspace_page import StoreWorkspacePage
from tests.master.cases import run_list_crud

LIST = master_entities(group="location", kind="list")


@pytest.mark.parametrize("entity", LIST, ids=lambda e: e.key)
def test_master_location_add_update_approve(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    entity,
) -> None:
    page, _workspace = store_session
    run_list_crud(page, settings, entity)
