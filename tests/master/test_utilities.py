import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.pages.store.master.entities import master_entities
from automation.pages.store.store_workspace_page import StoreWorkspacePage
from tests.master.cases import run_view

VIEW = master_entities(group="utilities", kind="view")


@pytest.mark.parametrize("entity", VIEW, ids=lambda e: e.key)
def test_master_utilities_opens(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    entity,
) -> None:
    page, workspace = store_session
    run_view(page, settings, workspace, entity)
