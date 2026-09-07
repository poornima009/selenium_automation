from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MasterEntity:
    key: str
    path: tuple[str, ...]
    group: str
    kind: str


MASTER_TREE: dict[str, list[str] | None] = {
    "Store": None,
    "Permission": None,
    "Document Type": None,
    "Category": None,
    "Tax": None,
    "T&C": None,
    "Equipment": None,
    "Site Grouping": None,
    "Templates": None,
    "Item": [
        "Unit",
        "Items",
        "Manufacturer/Model",
        "Low Stock Configuration",
        "Item Custom Filter",
    ],
    "Account": [
        "Contractor",
        "Supplier",
        "Transporter",
        "Departments",
        "Merge Accounts",
        "Client",
        "Fabricator",
    ],
    "Location": ["Chainage", "Other Location", "Structure"],
    "Employees": ["Employee", "Designation", "Employee Type", "Department"],
    "Module Utilities": ["File-Upload", "Item-SerialNo-Upload"],
    "Item Planning Details": None,
    "RFQ Role Mapping": None,
    "Material Movement": None,
}

_GROUP_BY_PARENT = {
    "Item": "item",
    "Account": "account",
    "Location": "location",
    "Employees": "employees",
    "Module Utilities": "utilities",
}

_OTHER_LEAVES = {"Item Planning Details", "RFQ Role Mapping", "Material Movement"}

VIEW_KEYS = frozenset(
    {
        "equipment",
        "merge_accounts",
        "file_upload",
        "item_serialno_upload",
        "item_planning_details",
        "rfq_role_mapping",
        "low_stock_configuration",
        "item_custom_filter",
    }
)


def _kind(key: str) -> str:
    if key == "store":
        return "special"
    if key == "permission":
        return "matrix"
    if key in VIEW_KEYS:
        return "view"
    return "list"


def _slug(name: str) -> str:
    return (
        name.lower()
        .replace("&", "and")
        .replace("/", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )


def _build_entities() -> tuple[MasterEntity, ...]:
    entities: list[MasterEntity] = []
    for child, grandchildren in MASTER_TREE.items():
        if not grandchildren:
            group = "other" if child in _OTHER_LEAVES else "top"
            key = _slug(child)
            entities.append(MasterEntity(key, ("Master", child), group, _kind(key)))
            continue
        group = _GROUP_BY_PARENT[child]
        for grandchild in grandchildren:
            key = _slug(grandchild)
            entities.append(
                MasterEntity(key, ("Master", child, grandchild), group, _kind(key))
            )
    return tuple(entities)


MASTER_ENTITIES: tuple[MasterEntity, ...] = _build_entities()


def master_entities(*, group: str | None = None, kind: str | None = None) -> tuple[MasterEntity, ...]:
    entities = MASTER_ENTITIES
    if group:
        entities = tuple(entity for entity in entities if entity.group == group)
    if kind:
        entities = tuple(entity for entity in entities if entity.kind == kind)
    return entities


def master_entity(key: str) -> MasterEntity:
    for entity in MASTER_ENTITIES:
        if entity.key == key:
            return entity
    raise KeyError(f"Unknown Master entity: {key}")
