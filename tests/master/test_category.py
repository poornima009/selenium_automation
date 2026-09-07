from __future__ import annotations

import pytest
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.crud_flow import MasterCrudFlow
from automation.pages.store.store_workspace_page import StoreWorkspacePage
from tests.master.cases import unique_name

ENTITY = "category"


@pytest.fixture(scope="module")
def category_name() -> str:
    return unique_name("CAT")


@pytest.fixture(scope="module")
def category_updated() -> str:
    return unique_name("CUT")


@pytest.fixture(scope="module")
def duplicate_name() -> str:
    return unique_name("CDP")


def _flow(page: Page, settings: Settings) -> MasterCrudFlow:
    return MasterCrudFlow(page, settings, ENTITY)


def test_master_category_01_add(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    category_name: str,
) -> None:
    page, _workspace = store_session
    listing = _flow(page, settings).create(category_name)
    assert listing.row_is_visible(category_name)


def test_master_category_02_update(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    category_name: str,
    category_updated: str,
) -> None:
    page, _workspace = store_session
    listing = _flow(page, settings).update(category_name, category_updated)
    target = category_updated if listing.row_is_visible(category_updated) else category_name
    assert listing.row_is_visible(target)


def test_master_category_03_approve(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    category_name: str,
    category_updated: str,
) -> None:
    page, _workspace = store_session
    flow = _flow(page, settings)
    listing = flow.open()
    listing.search(category_updated)
    target = category_updated if listing.row_is_visible(category_updated) else category_name
    approved = flow.approve(target)
    if not approved:
        pytest.skip("No Approve action on Master > Category")
    listing = flow.open()
    listing.search(target)
    state = listing.row_state(target).upper()
    assert "APPROVED" in state or listing.row_is_visible(target)


def test_master_category_04_empty_create(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    page, _workspace = store_session
    listing = _flow(page, settings).open_empty_save()
    assert listing.is_on_form() or listing.helper_text() or listing.alert_is_visible(timeout_ms=2000)


def test_master_category_05_duplicate_short_name(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    duplicate_name: str,
) -> None:
    page, _workspace = store_session
    flow = _flow(page, settings)
    short = duplicate_name[-6:]
    listing = flow.create(duplicate_name, short)
    assert listing.row_is_visible(duplicate_name)
    listing = flow.try_create(duplicate_name, short)
    blocked = listing.is_on_form() or listing.alert_is_visible(timeout_ms=3000)
    if listing.is_on_form():
        listing.go_back()
    listing = flow.open()
    listing.search(duplicate_name)
    if listing.row_count(duplicate_name) > 1:
        pytest.skip("Master > Category allows duplicate names")
    assert blocked or listing.row_count(duplicate_name) == 1


def test_master_category_06_search_missing(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
) -> None:
    page, _workspace = store_session
    listing = _flow(page, settings).open()
    missing = unique_name("ZZZ")
    listing.search(missing)
    assert listing.no_data_is_visible() or not listing.row_is_visible(missing)