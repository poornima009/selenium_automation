from __future__ import annotations

from dataclasses import dataclass

from automation.core.base_page import BasePage
from automation.core.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class CrudSpec:
    name_label: str
    extras: tuple[tuple[str, str], ...] = ()


CRUD_SPEC: dict[str, CrudSpec] = {
    "document_type": CrudSpec("Document Type Name"),
    "category": CrudSpec("Category Name", (("Short Name", "short"),)),
    "tax": CrudSpec("Name", (("Rate (%)", "1"),)),
    "tandc": CrudSpec("Name"),
    "site_grouping": CrudSpec("Site Grouping Name", (("Select Site", "first_option"),)),
    "templates": CrudSpec(
        "Template Name",
        (("Entity Type", "first_option"), ("Category", "first_option")),
    ),
    "unit": CrudSpec(
        "Name",
        (
            ("Type", "first_option"),
            ("Abbreviation", "short"),
            ("Conversion into KG", "1"),
        ),
    ),
    "items": CrudSpec(
        "Item Name",
        (
            ("Alias", "short"),
            ("HSN Code", "998314"),
            ("Primary Unit / Unit Type", "first_option"),
            ("Item Type", "first_option"),
            ("GST %", "first_option"),
        ),
    ),
    "manufacturer_model": CrudSpec("Name"),
    "supplier": CrudSpec(
        "Vendor Name",
        (("PAN No", "pan"), ("Contact Person Name", "person")),
    ),
    "transporter": CrudSpec(
        "Transporter Name",
        (("PAN No", "pan"), ("Contact Person Name", "person")),
    ),
    "departments": CrudSpec(
        "Department Name",
        (
            ("PAN No", "pan"),
            ("Contact Person Name", "person"),
            ("Contact No", "phone"),
        ),
    ),
    "client": CrudSpec(
        "Client Name",
        (("PAN No", "pan"), ("Contact Person Name", "person")),
    ),
    "fabricator": CrudSpec(
        "Fabricator Name",
        (("PAN No", "pan"), ("Contact Person Name", "person")),
    ),
    "chainage": CrudSpec("Select Position", (("Select Position", "first_option"),)),
    "other_location": CrudSpec(
        "Name",
        (("Latitude", "28.61"), ("Longitude", "77.20"), ("Radius", "100")),
    ),
    "structure": CrudSpec(
        "Name",
        (("Latitude", "28.61"), ("Longitude", "77.20")),
    ),
    "designation": CrudSpec("Designation Name"),
    "employee_type": CrudSpec("Employee Type Name"),
    "department": CrudSpec("Name"),
    "material_movement": CrudSpec(
        "Remark",
        (("GST State", "first_option"), ("Bill Type", "first_option")),
    ),
}


class MasterFormPage(BasePage):
    """Generic Master add/update form. Entity-specific pages stay for Store and Permission."""

    def fill_create(self, name: str, entity_key: str, short_name: str | None = None) -> None:
        spec = CRUD_SPEC.get(entity_key)
        if spec is None:
            self._auto_fill(name)
            return
        logger.info("Filling %s create form", entity_key)
        if spec.name_label != "Select Position":
            self.fill_labeled(spec.name_label, name)
        self._fill_extras(spec, name, short_name)

    def fill_update(self, name: str, entity_key: str) -> None:
        spec = CRUD_SPEC.get(entity_key)
        logger.info("Updating %s name to %s", entity_key, name)
        if spec is None:
            self._auto_fill(name)
            return
        if spec.name_label == "Select Position":
            return
        self._replace_labeled(spec.name_label, name)

    def _fill_extras(self, spec: CrudSpec, name: str, short_name: str | None = None) -> None:
        for label, kind in spec.extras:
            if kind == "first_option":
                self.select_first_labeled(label)
                continue
            if kind == "short":
                value = short_name or (name[-6:] if len(name) >= 6 else name)
                self.fill_labeled(label, value)
                continue
            if kind == "pan":
                self.fill_labeled(label, self._pan(name))
                continue
            if kind == "phone":
                self.fill_labeled(label, self._phone(name))
                continue
            if kind == "person":
                self.fill_labeled(label, f"Person{name[-4:]}")
                continue
            self.fill_labeled(label, kind)

    def _pan(self, name: str) -> str:
        letters = "".join(ch for ch in name.upper() if ch.isalpha())[:5].ljust(5, "A")
        digits = "".join(ch for ch in name if ch.isdigit())[-4:].ljust(4, "0")
        return f"{letters}{digits}X"

    def _phone(self, name: str) -> str:
        digits = "".join(ch for ch in name if ch.isdigit()).ljust(10, "8")[:10]
        return "9" + digits[1:]

    def _replace_labeled(self, label: str, value: str) -> None:
        field = self.labeled_control(label)
        field.wait_for(state="visible", timeout=self.settings.default_timeout_ms)
        field.click(force=True)
        field.fill("")
        field.fill(value)
        field.press("Tab")

    def _auto_fill(self, name: str) -> None:
        logger.info("Auto-filling required Master fields")
        labels = self.page.locator("label").filter(has_text="*")
        used_name = False
        for index in range(labels.count()):
            text = (labels.nth(index).inner_text() or "").strip()
            if "UPLOAD" in text.upper():
                continue
            field = (
                labels.nth(index)
                .locator("xpath=ancestor::div[contains(@class,'MuiFormControl')][1]")
                .locator("input, textarea")
                .first
            )
            if field.count() == 0:
                continue
            if field.get_attribute("role") == "combobox":
                field.click()
                option = self.page.locator("[role='option']").first
                if option.count():
                    option.click()
                continue
            value = name if not used_name else f"{name}{index}"[:20]
            field.fill(value)
            used_name = True
