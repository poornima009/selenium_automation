from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class TemplateRecord:
    name: str


class MasterTemplatesPage(BasePage):
    """Master > Templates form fields."""

    def fill_create(
        self,
        record: TemplateRecord,
        mapped_categories: set[str],
    ) -> None:
        logger.info("Filling Template create form for %s", record.name)
        self.fill_labeled("Template Name", record.name)
        self.select_first_labeled("Entity Type")
        self._select_unmapped_category(mapped_categories)

    def fill_update(self, name: str) -> None:
        logger.info("Updating Template name to %s", name)
        field = self.labeled_control("Template Name")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.fill("")
        field.fill(name)
        field.press("Tab")

    def fill_remark(self, remark: str) -> None:
        self.fill_optional_remark(remark, "Templates")

    def _select_unmapped_category(self, mapped_categories: set[str]) -> None:
        field = self.labeled_control("Category")
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click()
        options = self.page.get_by_role("option")
        options.first.wait_for(
            state="visible",
            timeout=self.settings.default_timeout_ms,
        )
        existing = {name.casefold() for name in mapped_categories}
        for index in range(options.count()):
            option = options.nth(index)
            name = (option.inner_text() or "").strip()
            if name and name.casefold() not in existing:
                logger.info("Selecting unmapped Template category %s", name)
                option.click()
                return
        raise RuntimeError("No unmapped Template category is available")
