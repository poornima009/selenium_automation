from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from automation.core.reporting.html_report import render_html_report
from automation.core.reporting.models import RunResult, TestResult


class ReportManager:
    """Collect pytest outcomes and persist one immutable report directory."""

    def __init__(self, project_root: Path, started_at: datetime | None = None) -> None:
        self.project_root = project_root
        self.started = started_at or datetime.now().astimezone()
        self.run_directory = self._create_run_directory(project_root / "reports" / "runs")
        self.failure_directory = self.run_directory / "failures"
        self.failure_directory.mkdir()
        self.result = RunResult(
            run_id=self.run_directory.name,
            started_at=self.started.isoformat(timespec="seconds"),
        )
        self._tests: dict[str, TestResult] = {}

    def register_tests(self, items: Iterable[Any]) -> None:
        for item in items:
            self._ensure_test(item.nodeid)

    def mark_deselected(self, items: Iterable[Any]) -> None:
        for item in items:
            self._ensure_test(item.nodeid).status = "deselected"

    def record_report(self, report: Any) -> None:
        test = self._ensure_test(report.nodeid)
        test.duration_seconds += float(getattr(report, "duration", 0.0))
        status = self._status_for(report)
        if status:
            test.status = status
            test.phase = report.when
        if report.failed:
            test.error = getattr(report, "longreprtext", "") or str(
                getattr(report, "longrepr", "")
            )

    def screenshot_path(self, nodeid: str) -> Path:
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid).strip("_")
        return self.failure_directory / f"{safe_name}.png"

    def attach_screenshot(self, nodeid: str, path: Path) -> None:
        test = self._ensure_test(nodeid)
        test.screenshot = path.relative_to(self.run_directory).as_posix()

    def finish(self, exit_status: int, finished_at: datetime | None = None) -> Path:
        finished = finished_at or datetime.now().astimezone()
        self.result.finished_at = finished.isoformat(timespec="seconds")
        self.result.duration_seconds = max(0.0, (finished - self.started).total_seconds())
        self.result.exit_status = int(exit_status)
        self.result.tests = sorted(self._tests.values(), key=lambda test: test.nodeid)

        json_path = self.run_directory / "results.json"
        json_path.write_text(
            json.dumps(self.result.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        history = load_run_history(self.run_directory.parent, limit=3)
        html_path = self.run_directory / "report.html"
        html_path.write_text(render_html_report(self.result, history), encoding="utf-8")
        return html_path

    def _ensure_test(self, nodeid: str) -> TestResult:
        if nodeid not in self._tests:
            self._tests[nodeid] = TestResult(nodeid=nodeid, name=_test_name(nodeid))
        return self._tests[nodeid]

    @staticmethod
    def _status_for(report: Any) -> str:
        was_xfail = bool(getattr(report, "wasxfail", False))
        if was_xfail:
            return "xfailed" if report.skipped else "xpassed"
        if report.skipped:
            return "skipped"
        if report.failed:
            return "failed" if report.when == "call" else "error"
        if report.when == "call" and report.passed:
            return "passed"
        return ""

    def _create_run_directory(self, runs_directory: Path) -> Path:
        runs_directory.mkdir(parents=True, exist_ok=True)
        base_name = self.started.strftime("%Y%m%d_%H%M%S_%f")
        candidate = runs_directory / base_name
        suffix = 1
        while candidate.exists():
            candidate = runs_directory / f"{base_name}_{suffix}"
            suffix += 1
        candidate.mkdir()
        return candidate


def load_run_history(runs_directory: Path, limit: int = 3) -> list[RunResult]:
    history: list[RunResult] = []
    paths = sorted(runs_directory.glob("*/results.json"), reverse=True)
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            history.append(RunResult.from_dict(data))
        except (OSError, ValueError, TypeError):
            continue
        if len(history) == limit:
            break
    return list(reversed(history))


def _test_name(nodeid: str) -> str:
    return nodeid.rsplit("::", maxsplit=1)[-1]
