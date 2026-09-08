import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.pages.store.master.entities import master_entities
from automation.pages.store.store_workspace_page import StoreWorkspacePage
from tests.master.cases import run_list_crud, run_view

LIST = tuple(
    entity
    for entity in master_entities(group="item", kind="list")
    if entity.key != "unit"
)
VIEW = master_entities(group="item", kind="view")


@pytest.mark.parametrize("entity", LIST, ids=lambda e: e.key)
def test_master_item_add_update_approve(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    entity,
) -> None:
    page, _workspace = store_session
    run_list_crud(page, settings, entity)


@pytest.mark.parametrize("entity", VIEW, ids=lambda e: e.key)
def test_master_item_opens(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    entity,
) -> None:
    page, workspace = store_session
    run_view(page, settings, workspace, entity)
