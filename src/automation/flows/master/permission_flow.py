from __future__ import annotations

from playwright.sync_api import Page

from automation.config.settings import Settings, get_settings
from automation.core.logger import get_logger
from automation.pages.store.master.entities import master_entity
from automation.pages.store.master.list_page import MasterListPage
from automation.pages.store.master.permission_page import MasterPermissionPage
from automation.pages.store.store_nav_page import StoreNavPage

logger = get_logger(__name__)

PERMISSION_ROLE = "Manager"
PERMISSION_MODULE = "Chainage"


class MasterPermissionFlow:
    """Grant add, update, and approve on one Master > Permission module."""

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._nav = StoreNavPage(page, self._settings)
        self._list = MasterListPage(page, self._settings)
        self._form = MasterPermissionPage(page, self._settings)

    def open(self, module: str = PERMISSION_MODULE) -> MasterPermissionPage:
        self._list.dismiss_overlay()
        self._nav.open_path(*master_entity("permission").path)
        self._list.dismiss_overlay()
        self._form.select_role(PERMISSION_ROLE)
        self._form.filter_module(module)
        self._form.expand_module(module)
        return self._form

    def grant(
        self,
        operation: str,
        module: str = PERMISSION_MODULE,
    ) -> MasterPermissionPage:
        logger.info("Granting Permission %s on %s", operation, module)
        form = self.open(module)
        form.grant(module, operation)
        form.save_module()
        form.filter_module(module)
        form.expand_module(module)
        return form

    def grant_operations(
        self,
        module: str,
        operations: tuple[str, ...],
    ) -> MasterPermissionPage:
        logger.info("Granting %s permissions on %s", ", ".join(operations), module)
        form = self.open(module)
        for operation in operations:
            form.grant(module, operation)
        form.save_module()
        form.filter_module(module)
        form.expand_module(module)
        return form
