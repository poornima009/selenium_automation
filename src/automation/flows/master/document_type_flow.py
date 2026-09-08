from __future__ import annotations

from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.core.logger import get_logger
from automation.pages.store.master.document_type_page import (
    DocumentTypeRecord,
    MasterDocumentTypePage,
)
from automation.pages.store.master.entities import master_entity
from automation.pages.store.master.list_page import MasterListPage
from automation.pages.store.store_nav_page import StoreNavPage

logger = get_logger(__name__)


class DocumentTypeCreateBlockedError(RuntimeError):
    """The confirmation dialog prevented Document Type creation."""


class MasterDocumentTypeFlow:
    """Create, update, approve, and track a Document Type in one session."""

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._nav = StoreNavPage(page, self._settings)
        self._list = MasterListPage(page, self._settings)
        self._form = MasterDocumentTypePage(page, self._settings)

    def open(self) -> MasterListPage:
        self._list.dismiss_overlay()
        self._nav.open_path(*master_entity("document_type").path)
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

    def create(self, record: DocumentTypeRecord, remark: str) -> MasterListPage:
        logger.info("Creating Document Type %s", record.name)
        listing = self.open()
        listing.open_add()
        self._form.fill_create(record)
        self._form.fill_remark(remark)
        listing.save()
        listing.confirm(remark=remark)
        if listing.visible_dialog() is not None:
            raise DocumentTypeCreateBlockedError(
                "Application bug: Document Type confirmation Save leaves the "
                "dialog open and sends no create request"
            )
        listing.wait_until_on_list()
        return self.find(record.name)

    def update(self, name: str, updated_name: str, remark: str) -> MasterListPage:
        logger.info("Updating Document Type %s", name)
        listing = self.find(name)
        listing.open_row(name)
        self._form.fill_update(updated_name)
        self._form.fill_remark(remark)
        listing.save()
        listing.confirm(remark=remark)
        listing.wait_after_save()
        return self.find(updated_name)

    def approve(self, name: str, remark: str) -> bool:
        logger.info("Approving Document Type %s", name)
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
