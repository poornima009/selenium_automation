from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

STATUSES = (
    "passed",
    "failed",
    "error",
    "skipped",
    "xfailed",
    "xpassed",
    "deselected",
    "not_run",
)


@dataclass
class TestResult:
    nodeid: str
    name: str
    status: str = "not_run"
    duration_seconds: float = 0.0
    phase: str = ""
    error: str = ""
    screenshot: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TestResult":
        return cls(**data)


@dataclass
class RunResult:
    run_id: str
    started_at: str
    finished_at: str = ""
    duration_seconds: float = 0.0
    exit_status: int = 0
    tests: list[TestResult] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        totals = {status: 0 for status in STATUSES}
        for test in self.tests:
            totals[test.status] = totals.get(test.status, 0) + 1
        return totals

    @property
    def total(self) -> int:
        return len(self.tests)

    @property
    def executed(self) -> int:
        return self.total - self.counts["deselected"] - self.counts["not_run"]

    @property
    def pass_rate(self) -> float:
        return (self.counts["passed"] / self.executed * 100) if self.executed else 0.0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["counts"] = self.counts
        data["total"] = self.total
        data["executed"] = self.executed
        data["pass_rate"] = round(self.pass_rate, 2)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunResult":
        fields = {
            key: value
            for key, value in data.items()
            if key not in {"counts", "total", "executed", "pass_rate"}
        }
        fields["tests"] = [TestResult.from_dict(test) for test in fields.get("tests", [])]
        return cls(**fields)
