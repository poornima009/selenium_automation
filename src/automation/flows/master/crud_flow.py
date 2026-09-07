from __future__ import annotations

from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.core.logger import get_logger
from automation.pages.store.master.entities import master_entity
from automation.pages.store.master.form_page import MasterFormPage
from automation.pages.store.master.list_page import MasterListPage
from automation.pages.store.store_nav_page import StoreNavPage

logger = get_logger(__name__)


class MasterCrudFlow:
    """Create, update, and approve a catalog Master list entity."""

    def __init__(self, page: Page, settings: Settings | None, entity_key: str) -> None:
        self._settings = settings or get_settings()
        self._entity = master_entity(entity_key)
        self._nav = StoreNavPage(page, self._settings)
        self._list = MasterListPage(page, self._settings)
        self._form = MasterFormPage(page, self._settings)

    def open(self) -> MasterListPage:
        self._list.dismiss_overlay()
        self._nav.open_path(*self._entity.path)
        self._list.dismiss_overlay()
        return self._list

    def create(self, name: str, short_name: str | None = None) -> MasterListPage:
        logger.info("Creating %s %s", self._entity.key, name)
        listing = self.open()
        listing.open_add()
        self._form.fill_create(name, self._entity.key, short_name)
        listing.save()
        listing.confirm()
        listing.wait_until_on_list()
        listing = self.open()
        listing.search(name)
        return listing

    def try_create(self, name: str, short_name: str | None = None) -> MasterListPage:
        logger.info("Trying create %s %s", self._entity.key, name)
        listing = self.open()
        listing.open_add()
        self._form.fill_create(name, self._entity.key, short_name)
        listing.save()
        listing.confirm()
        return listing

    def open_empty_save(self) -> MasterListPage:
        listing = self.open()
        listing.open_add()
        listing.save()
        listing.confirm()
        return listing

    def update(self, name: str, new_name: str) -> MasterListPage:
        logger.info("Updating %s %s", self._entity.key, name)
        listing = self.open()
        listing.search(name)
        listing.open_row(name)
        listing.dismiss_menu()
        self._form.fill_update(new_name, self._entity.key)
        listing.save()
        listing.confirm()
        listing.wait_until_on_list()
        listing = self.open()
        listing.search(new_name)
        if not listing.row_is_visible(new_name):
            listing.search(name)
        return listing

    def approve(self, name: str) -> bool:
        logger.info("Approving %s %s", self._entity.key, name)
        listing = self.open()
        listing.search(name)
        if listing.approve():
            listing.search(name)
            return True
        listing.open_row(name)
        approved = listing.approve()
        if approved:
            listing.wait_until_on_list()
            listing.search(name)
        return approved
