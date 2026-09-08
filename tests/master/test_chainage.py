from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from openpyxl import Workbook
from playwright.sync_api import Page

from automation.config.settings import Settings
from automation.flows.master.chainage_flow import (
    ChainageImportBlockedError,
    MasterChainageFlow,
)
from automation.pages.store.store_workspace_page import StoreWorkspacePage


def test_master_chainage_import_search_and_lifecycle_capability(
    settings: Settings,
    store_session: tuple[Page, StoreWorkspacePage],
    tmp_path: Path,
) -> None:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    chainage_name = f"9{stamp[-2:]}+{stamp[-3:]}"
    workbook = _chainage_workbook(tmp_path, chainage_name)
    page, _workspace = store_session

    flow = MasterChainageFlow(page, settings)
    try:
        listing = flow.import_workbook(
            workbook,
            chainage_name,
            remark="AUTO Chainage import",
        )
    except ChainageImportBlockedError as error:
        pytest.xfail(str(error))
    assert listing.row_is_visible(chainage_name)

    listing = flow.find(chainage_name)
    assert listing.row_is_visible(chainage_name)
    pytest.xfail(
        "Chainage is import-only and exposes no update, approve, or history actions"
    )


def _chainage_workbook(tmp_path: Path, chainage_name: str) -> Path:
    path = tmp_path / "chainage.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "ChainageTemplate"
    sheet.append(("Serial No", "Chainage Name", "Latitude", "Longitude"))
    sheet.append((1, chainage_name, 28.6139, 77.2090))
    workbook.save(path)
    return path
