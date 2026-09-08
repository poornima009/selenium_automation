from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.core.logger import get_logger
from automation.pages.store.master.chainage_page import MasterChainagePage
from automation.pages.store.master.entities import master_entity
from automation.pages.store.master.list_page import MasterListPage
from automation.pages.store.store_nav_page import StoreNavPage

logger = get_logger(__name__)


class ChainageImportBlockedError(RuntimeError):
    """The confirmation dialog prevented Chainage import."""


class MasterChainageFlow:
    """Import and search Chainage records."""

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._nav = StoreNavPage(page, self._settings)
        self._list = MasterListPage(page, self._settings)
        self._form = MasterChainagePage(page, self._settings)

    def open(self) -> MasterListPage:
        self._list.dismiss_overlay()
        self._nav.open_path(*master_entity("chainage").path)
        self._list.close_menu()
        self._list.wait_for_visible(self._list.LIST_ADD)
        self._list.dismiss_overlay()
        return self._list

    def stay(self) -> MasterListPage:
        self._list.close_menu()
        self._list.dismiss_overlay()
        if self._list.add_is_enabled():
            return self._list
        return self.open()

    def find(self, name: str) -> MasterListPage:
        logger.info("Checking Chainage table for %s", name)
        return self.stay()

    def import_workbook(
        self,
        workbook: Path,
        chainage_name: str,
        remark: str,
    ) -> MasterListPage:
        logger.info("Importing Chainage %s", chainage_name)
        listing = self.open()
        listing.open_add()
        self._form.fill_import(workbook)
        self._form.fill_remark(remark)
        listing.save()
        listing.confirm(remark=remark)
        if listing.visible_dialog() is not None:
            raise ChainageImportBlockedError(
                "Application bug: Chainage confirmation Save leaves the dialog "
                "open after import"
            )
        listing.wait_until_on_list()
        return self.find(chainage_name)
