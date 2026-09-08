from __future__ import annotations

from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.core.logger import get_logger
from automation.pages.store.master.client_page import ClientRecord, MasterClientPage
from automation.pages.store.master.entities import master_entity
from automation.pages.store.master.list_page import MasterListPage
from automation.pages.store.store_nav_page import StoreNavPage

logger = get_logger(__name__)


class ClientCreateBlockedError(RuntimeError):
    """The known account confirmation defect prevented Client creation."""


class MasterClientFlow:
    """Create, update, approve, and track a Client in one Store session."""

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._nav = StoreNavPage(page, self._settings)
        self._list = MasterListPage(page, self._settings)
        self._form = MasterClientPage(page, self._settings)

    def open(self) -> MasterListPage:
        self._list.dismiss_overlay()
        self._nav.open_path(*master_entity("client").path)
        self._list.close_menu()
        self._list.wait_for_visible(self._list.SEARCH)
        self._list.dismiss_overlay()
        return self._list

    def stay(self) -> MasterListPage:
        self._list.close_menu()
        self._list.dismiss_overlay()
        if self._list.search_is_visible():
            return self._list
        return self.open()

    def find(self, name: str) -> MasterListPage:
        listing = self.stay()
        listing.search(name)
        return listing

    def create(self, record: ClientRecord, remark: str) -> MasterListPage:
        logger.info("Creating Client %s", record.name)
        listing = self.open()
        listing.open_add()
        self._form.fill_create(record)
        self._form.fill_remark(remark)
        listing.save()
        listing.confirm(remark=remark)
        if listing.visible_dialog() is not None:
            raise ClientCreateBlockedError(
                "Known application bug: Client confirmation Save leaves the "
                "dialog open and sends no create request"
            )
        listing.wait_until_on_list()
        return self.find(record.name)

    def update(self, name: str, contact_person: str, remark: str) -> MasterListPage:
        logger.info("Updating Client %s", name)
        listing = self.find(name)
        listing.open_row(name)
        self._form.fill_update(contact_person)
        self._form.fill_remark(remark)
        listing.save()
        listing.confirm(remark=remark)
        listing.wait_after_save()
        return listing

    def approve(self, name: str, remark: str) -> bool:
        logger.info("Approving Client %s", name)
        listing = self._list
        if not listing.approve_is_visible():
            listing = self.find(name)
            listing.open_row(name)
        self._form.fill_remark(remark)
        if not listing.approve(remark=remark):
            return False
        listing.wait_until_on_list()
        self.find(name)
        return True

    def track(self, name: str) -> str:
        listing = self.find(name)
        return listing.open_track(name)
