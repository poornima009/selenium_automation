"""Live Store menu on Demo. Parents with children are not clickable leaves."""

from automation.pages.store.master.entities import MASTER_TREE

STORE_MENU: dict[str, dict[str, list[str] | None] | list[str]] = {
    "Dashboard": [],
    "Master": MASTER_TREE,
    "Purchase": ["Purchase Order", "Purchase Return", "Dispatches", "Advance Payment"],
    "Stock Receipt": ["MRN Slip", "Stock Transfer", "Short & Excess"],
    "Issue": ["Issue Slip", "Issue Return", "Issue Gate Pass"],
    "Sales Orders": ["Sales Order", "Sales Order Issue", "Sales Order Invoice"],
    "Requisition": [],
    "Indent": [],
    "RFQ": [],
    "Gate Entry": [],
    "Debit/Credit": ["Issue Debit Note", "Vendor CR/DB Note"],
    "Report": [
        "Inventory Report",
        "Download Reports",
        "Item Serial",
        "Item Movement Analysis",
        "Plant Report",
        "Stock Transfer",
        "Employee Ledger",
        "Credit/Debit Notes",
        "Supplier Ledger",
        "Site Ledger",
        "Contractor Ledger",
        "Crusher Report",
        "Tanker Distribution",
        "weighBridge Report",
        "Most Frequent Purchase",
        "Supplier Item Pricing",
        "Equipment Ledger",
        "Department Ledger",
        "Day Book",
        "Item Cumulative Transaction",
        "V1 Category Stock Summary",
        "Supplier Issue Ledger",
        "V2 Category Stock Summary",
        "Fabricator's Report",
    ],
    "Setting": [
        "Company Setting",
        "Entities Configuration",
        "Entity Document Mapping Configuration",
        "Change Theme",
        "Navbar Setting",
        "Manage Licences",
        "Indent Sitewise Threshold",
        "Genric Code Genratore Config",
        "Dashboard Permission",
    ],
    "Mix Design Requisition": [],
    "Crusher": ["Crusher Config", "Crusher Output"],
    "Trip-Management": ["Weigh Bridge", "Trip-Mrn", "Trip-IssueSlip"],
    "Job-Card": [],
}

# List screens used for deeper add-form E2E (open form, do not save).
STORE_LIST_PATHS: tuple[tuple[str, ...], ...] = (
    ("Master", "Category"),
    ("Master", "Item", "Items"),
    ("Purchase", "Purchase Order"),
    ("Requisition",),
    ("Indent",),
    ("RFQ",),
    ("Gate Entry",),
    ("Issue", "Issue Slip"),
    ("Stock Receipt", "MRN Slip"),
)


def store_leaf_paths() -> list[tuple[str, ...]]:
    paths: list[tuple[str, ...]] = []
    for parent, children in STORE_MENU.items():
        if children == []:
            paths.append((parent,))
            continue
        if isinstance(children, list):
            for child in children:
                paths.append((parent, child))
            continue
        for child, grandchildren in children.items():
            if not grandchildren:
                paths.append((parent, child))
                continue
            for grandchild in grandchildren:
                paths.append((parent, child, grandchild))
    return paths
