from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from automation.core.reporting import ReportManager
from automation.core.reporting.manager import load_run_history


def _item(nodeid: str) -> SimpleNamespace:
    return SimpleNamespace(nodeid=nodeid)


def _report(
    nodeid: str,
    *,
    outcome: str,
    when: str = "call",
    error: str = "",
    wasxfail: bool = False,
) -> SimpleNamespace:
    return SimpleNamespace(
        nodeid=nodeid,
        when=when,
        duration=0.25,
        passed=outcome == "passed",
        failed=outcome == "failed",
        skipped=outcome == "skipped",
        longreprtext=error,
        longrepr=error,
        wasxfail=wasxfail,
    )


def test_report_classifies_results_and_keeps_inventory(tmp_path: Path) -> None:
    manager = ReportManager(tmp_path)
    items = [_item("tests/test_one.py::test_pass"), _item("tests/test_one.py::test_not_run")]
    manager.register_tests(items)
    manager.record_report(_report(items[0].nodeid, outcome="passed"))

    path = manager.finish(0)
    data = json.loads(path.with_name("results.json").read_text(encoding="utf-8"))

    assert data["counts"]["passed"] == 1
    assert data["counts"]["not_run"] == 1
    assert data["total"] == 2


def test_report_renders_failure_error_and_screenshot(tmp_path: Path) -> None:
    manager = ReportManager(tmp_path)
    nodeid = "tests/test_failure.py::test_example"
    manager.register_tests([_item(nodeid)])
    manager.record_report(
        _report(nodeid, outcome="failed", error="AssertionError: <unsafe>")
    )
    screenshot = manager.screenshot_path(nodeid)
    screenshot.write_bytes(b"png")
    manager.attach_screenshot(nodeid, screenshot)

    html = manager.finish(1).read_text(encoding="utf-8")

    assert "AssertionError: &lt;unsafe&gt;" in html
    assert "failures/tests_test_failure.py_test_example.png" in html
    assert 'data-status="failed"' in html


def test_run_directories_never_overwrite(tmp_path: Path) -> None:
    started = datetime(2026, 9, 8, 20, 13, 14, tzinfo=timezone.utc)

    first = ReportManager(tmp_path, started)
    second = ReportManager(tmp_path, started)

    assert first.run_directory != second.run_directory
    assert first.run_directory.exists()
    assert second.run_directory.exists()


def test_history_returns_latest_three_runs_in_time_order(tmp_path: Path) -> None:
    started = datetime(2026, 9, 8, 20, 0, tzinfo=timezone.utc)
    for index in range(4):
        run_time = started + timedelta(minutes=index)
        manager = ReportManager(tmp_path, run_time)
        nodeid = "tests/test_history.py::test_status"
        manager.register_tests([_item(nodeid)])
        outcome = "failed" if index == 3 else "passed"
        manager.record_report(_report(nodeid, outcome=outcome))
        manager.finish(int(outcome == "failed"), run_time + timedelta(seconds=1))

    history = load_run_history(tmp_path / "reports" / "runs")

    assert len(history) == 3
    assert [run.started_at for run in history] == sorted(run.started_at for run in history)
    assert history[-1].counts["failed"] == 1
