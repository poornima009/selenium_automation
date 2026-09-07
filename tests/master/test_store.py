from __future__ import annotations

from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.store_flow import MasterStoreFlow
from automation.pages.store.master.store_page import StoreRecord
from automation.pages.store.store_workspace_page import StoreWorkspacePage

_RACK_HEADER = (Path(__file__).resolve().parents[2] / "testdata" / "store_racks.csv").read_text(
    encoding="utf-8"
).splitlines()[0]


def _racks_sheet(folder: Path, stamp: str) -> Path:
    path = folder / "store_racks.csv"
    path.write_text(
        f"{_RACK_HEADER}\nRACK-{stamp[-6:]}-1\nRACK-{stamp[-6:]}-2\n",
        encoding="utf-8",
    )
    return path


def test_master_store_add_search_update_approve_track(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    tmp_path: Path,
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    record = StoreRecord(
        name=f"AUTO-STORE-{stamp}",
        alias=f"ALIAS-{stamp[-6:]}",
        short_name=f"A{stamp[-5:]}",
        racks_sheet=str(_racks_sheet(tmp_path, stamp)),
    )
    updated_alias = f"U{record.alias[-6:]}"
    page, _workspace = store_session
    flow = MasterStoreFlow(page, settings)

    listing = flow.create(record, remark="AUTO create")
    assert listing.row_is_visible(record.name)

    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    flow.update(record.name, updated_alias, remark="AUTO update")
    assert flow.approve(record.name, remark="AUTO approve")
    listing = flow.find(record.name)
    assert listing.row_is_visible(record.name)

    history = flow.track(record.name)
    assert history
    assert "APPROVE" in history.upper() or "APPROVED" in history.upper()
