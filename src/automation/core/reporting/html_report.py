from __future__ import annotations

from html import escape

from automation.core.reporting.models import RunResult, STATUSES, TestResult

STATUS_LABELS = {
    "passed": "Passed",
    "failed": "Failed",
    "error": "Error",
    "skipped": "Skipped",
    "xfailed": "Expected Failure",
    "xpassed": "Unexpected Pass",
    "deselected": "Deselected",
    "not_run": "Not Run",
}


def render_html_report(current: RunResult, history: list[RunResult]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Automation Report - {escape(current.run_id)}</title>
  <style>{_styles()}</style>
</head>
<body>
  <header>
    <div><span class="eyebrow">NYGGS AUTOMATION</span><h1>Test Run Report</h1></div>
    <div class="run-meta">{escape(current.run_id)}<br>{escape(current.started_at)}</div>
  </header>
  <main>
    {_summary(current)}
    {_comparison(history)}
    {_test_results(current.tests)}
  </main>
  <script>{_script()}</script>
</body>
</html>
"""


def _summary(run: RunResult) -> str:
    counts = run.counts
    chart_counts = {
        "passed": counts["passed"],
        "failed": counts["failed"] + counts["error"],
        "skipped": counts["skipped"] + counts["xfailed"] + counts["xpassed"],
        "not_run": counts["not_run"] + counts["deselected"],
    }
    cards = [
        ("Discovered", run.total, "neutral"),
        ("Executed", run.executed, "neutral"),
        ("Passed", counts["passed"], "passed"),
        ("Failed", counts["failed"], "failed"),
        ("Errors", counts["error"], "error"),
        ("Not Run", counts["not_run"] + counts["deselected"], "not_run"),
    ]
    card_html = "".join(
        f'<button class="metric {css}" data-filter="{css if css != "neutral" else "all"}">'
        f'<span>{escape(label)}</span><strong>{value}</strong></button>'
        for label, value, css in cards
    )
    chart = _result_chart(chart_counts, run.total, run.pass_rate)
    other = counts["skipped"] + counts["xfailed"] + counts["xpassed"]
    return f"""
<section>
  <div class="section-heading"><div><span class="eyebrow">OVERVIEW</span>
    <h2>{run.pass_rate:.1f}% passed</h2></div>
    <p>{run.executed} executed · {other} skipped/expected · {run.duration_seconds:.1f}s</p>
  </div>
  <div class="overview-grid">
    {chart}
    <div class="metrics">{card_html}</div>
  </div>
</section>
"""


def _result_chart(counts: dict[str, int], total: int, pass_rate: float) -> str:
    denominator = total or 1
    passed_end = counts["passed"] / denominator * 100
    failed_end = passed_end + counts["failed"] / denominator * 100
    skipped_end = failed_end + counts["skipped"] / denominator * 100
    gradient = (
        f"var(--passed) 0 {passed_end:.2f}%,"
        f"var(--failed) {passed_end:.2f}% {failed_end:.2f}%,"
        f"var(--skipped) {failed_end:.2f}% {skipped_end:.2f}%,"
        f"var(--not) {skipped_end:.2f}% 100%"
    )
    legend = "".join(
        f'<li><i class="{status}"></i><span>{escape(STATUS_LABELS[status])}</span>'
        f"<strong>{value}</strong></li>"
        for status, value in counts.items()
    )
    return f"""
<div class="chart-panel">
  <div class="donut" style="--segments:{gradient}" role="img" aria-label="{pass_rate:.1f}% passed">
    <div><strong>{pass_rate:.0f}%</strong><span>passed</span></div>
  </div>
  <ul class="legend">{legend}</ul>
</div>
"""


def _comparison(history: list[RunResult]) -> str:
    headers = "".join(
        f"<th>{escape(run.run_id)}<small>{escape(run.started_at)}</small></th>"
        for run in history
    )
    rows = [
        ("Pass rate", [f"{run.pass_rate:.1f}%" for run in history]),
        ("Discovered", [str(run.total) for run in history]),
        ("Executed", [str(run.executed) for run in history]),
        ("Passed", [str(run.counts["passed"]) for run in history]),
        ("Failed", [str(run.counts["failed"]) for run in history]),
        ("Errors", [str(run.counts["error"]) for run in history]),
        ("Not run", [str(run.counts["not_run"] + run.counts["deselected"]) for run in history]),
    ]
    body = "".join(
        f"<tr><th>{escape(label)}</th>{''.join(f'<td>{escape(value)}</td>' for value in values)}</tr>"
        for label, values in rows
    )
    changes = _status_changes(history)
    bars = "".join(_history_bar(run) for run in history)
    return f"""
<section>
  <div class="section-heading"><div><span class="eyebrow">HISTORY</span>
    <h2>Last {len(history)} test runs</h2></div>
    <p>Newest run appears on the right</p>
  </div>
  <div class="history-bars">{bars}</div>
  <div class="table-wrap"><table class="history"><thead><tr><th>Metric</th>{headers}</tr></thead>
    <tbody>{body}</tbody></table></div>
  {changes}
</section>
"""


def _history_bar(run: RunResult) -> str:
    total = run.total or 1
    counts = run.counts
    groups = (
        ("passed", counts["passed"]),
        ("failed", counts["failed"] + counts["error"]),
        ("skipped", counts["skipped"] + counts["xfailed"] + counts["xpassed"]),
        ("not_run", counts["not_run"] + counts["deselected"]),
    )
    segments = "".join(
        f'<span class="{status}" style="width:{count / total * 100:.2f}%" title="{STATUS_LABELS[status]}: {count}"></span>'
        for status, count in groups
        if count
    )
    return f"""
<div class="run-visual">
  <div><strong>{escape(run.run_id)}</strong><span>{run.pass_rate:.1f}% passed</span></div>
  <div class="stacked-bar" aria-label="{run.pass_rate:.1f}% passed">{segments}</div>
</div>
"""


def _status_changes(history: list[RunResult]) -> str:
    if len(history) < 2:
        return '<p class="empty">Run the suite again to see per-test changes.</p>'
    previous = {test.nodeid: test.status for test in history[-2].tests}
    changed = [
        test
        for test in history[-1].tests
        if previous.get(test.nodeid, "not_run") != test.status
    ]
    if not changed:
        return '<p class="empty">No test status changed from the previous run.</p>'
    items = "".join(
        "<li>"
        f"<code>{escape(test.nodeid)}</code>"
        f"<span>{escape(STATUS_LABELS.get(previous.get(test.nodeid, 'not_run'), 'Not Run'))}"
        f" → <b>{escape(STATUS_LABELS.get(test.status, test.status))}</b></span>"
        "</li>"
        for test in changed
    )
    return f'<details class="changes" open><summary>{len(changed)} status changes</summary><ul>{items}</ul></details>'


def _test_results(tests: list[TestResult]) -> str:
    controls = ['<button class="filter active" data-filter="all">All</button>']
    controls.extend(
        f'<button class="filter" data-filter="{status}">'
        f"{escape(STATUS_LABELS[status])} ({sum(test.status == status for test in tests)})</button>"
        for status in STATUSES
    )
    rows = "".join(_test_row(test) for test in tests)
    return f"""
<section>
  <div class="section-heading"><div><span class="eyebrow">DETAILS</span>
    <h2>All test cases</h2></div>
    <label class="search">Search <input id="search" type="search" placeholder="Test name or path"></label>
  </div>
  <div class="filters">{''.join(controls)}</div>
  <div id="test-list" class="test-list">{rows}</div>
  <p id="no-results" class="empty" hidden>No tests match the selected filters.</p>
</section>
"""


def _test_row(test: TestResult) -> str:
    detail = ""
    if test.error:
        detail += (
            '<details class="error-detail"><summary>Error details</summary>'
            f"<pre>{escape(test.error)}</pre></details>"
        )
    if test.screenshot:
        screenshot = escape(test.screenshot, quote=True)
        detail += (
            '<details class="screenshot"><summary>Failure screenshot</summary>'
            f'<a href="{screenshot}"><img src="{screenshot}" alt="Failure screenshot"></a></details>'
        )
    label = STATUS_LABELS.get(test.status, test.status)
    return f"""
<article class="test-row" data-status="{escape(test.status)}" data-search="{escape(test.nodeid.lower(), quote=True)}">
  <div class="test-main">
    <span class="status {escape(test.status)}">{escape(label)}</span>
    <div><strong>{escape(test.name)}</strong><code>{escape(test.nodeid)}</code></div>
    <span class="duration">{test.duration_seconds:.3f}s</span>
  </div>
  {detail}
</article>
"""


def _styles() -> str:
    return """
:root{--bg:#f4f7fb;--panel:#fff;--ink:#172033;--muted:#64748b;--line:#dce3ed;
--passed:#22a95b;--failed:#dc2747;--error:#b42318;--skipped:#e3a008;--not:#64748b;--accent:#255ca8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,sans-serif}
header{background:#12344d;color:#fff;display:flex;justify-content:space-between;align-items:center;padding:24px max(24px,calc((100% - 1200px)/2))}
h1,h2{margin:3px 0}.eyebrow{font-size:11px;font-weight:800;letter-spacing:.16em;color:#76b8e8}.run-meta{text-align:right;color:#cce0ef}
main{max-width:1200px;margin:auto;padding:24px}section{background:var(--panel);border:1px solid var(--line);border-radius:10px;margin-bottom:20px;padding:22px;box-shadow:0 2px 8px #23395d0c}
.section-heading{display:flex;justify-content:space-between;align-items:end;margin-bottom:18px}.section-heading p{color:var(--muted);margin:0}
.overview-grid{display:grid;grid-template-columns:330px 1fr;gap:24px;align-items:center}.chart-panel{display:flex;align-items:center;gap:24px;padding:8px}
.donut{width:170px;height:170px;flex:0 0 170px;border-radius:50%;background:conic-gradient(var(--segments));display:grid;place-items:center;position:relative}
.donut:after{content:"";position:absolute;width:106px;height:106px;border-radius:50%;background:var(--panel)}.donut div{z-index:1;text-align:center}.donut strong{display:block;font-size:29px}.donut span{color:var(--muted)}
.legend{list-style:none;padding:0;margin:0;min-width:110px}.legend li{display:grid;grid-template-columns:10px 1fr auto;align-items:center;gap:7px;padding:4px 0}.legend i{width:10px;height:10px;border-radius:50%}.legend i.passed{background:var(--passed)}.legend i.failed{background:var(--failed)}.legend i.skipped{background:var(--skipped)}.legend i.not_run{background:var(--not)}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.metric{border:1px solid var(--line);border-top:4px solid var(--accent);background:#fff;border-radius:7px;padding:13px;text-align:left;cursor:pointer}
.metric span{display:block;color:var(--muted)}.metric strong{font-size:28px}.metric.passed{border-top-color:var(--passed)}.metric.failed{border-top-color:var(--failed)}.metric.error{border-top-color:var(--error)}.metric.not_run{border-top-color:var(--not)}
.history-bars{display:grid;gap:12px;margin-bottom:20px}.run-visual>div:first-child{display:flex;justify-content:space-between;color:var(--muted);font-size:12px;margin-bottom:4px}.run-visual strong{color:var(--ink)}.stacked-bar{display:flex;height:16px;border-radius:4px;overflow:hidden;background:#e8edf3}.stacked-bar span.passed{background:var(--passed)}.stacked-bar span.failed{background:var(--failed)}.stacked-bar span.skipped{background:var(--skipped)}.stacked-bar span.not_run{background:var(--not)}
.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%}th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:right}th:first-child{text-align:left}thead th{background:#f7f9fc}th small{display:block;color:var(--muted);font-weight:400;white-space:nowrap}
.changes,.error-detail,.screenshot{margin-top:12px}.changes ul{padding:0;list-style:none}.changes li{display:flex;justify-content:space-between;gap:20px;border-top:1px solid var(--line);padding:8px}.changes code{overflow-wrap:anywhere}
.filters{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:14px}.filter{border:1px solid var(--line);background:#fff;border-radius:18px;padding:6px 11px;cursor:pointer}.filter.active{background:var(--accent);border-color:var(--accent);color:#fff}
.search{color:var(--muted)}input{border:1px solid var(--line);border-radius:5px;padding:8px;margin-left:6px;width:240px}
.test-list{border-top:1px solid var(--line)}.test-row{padding:13px 5px;border-bottom:1px solid var(--line)}.test-main{display:grid;grid-template-columns:120px 1fr 75px;align-items:center;gap:12px}
.test-main strong,.test-main code{display:block}.test-main code{color:var(--muted);margin-top:3px;overflow-wrap:anywhere}.duration{text-align:right;color:var(--muted)}
.status{border-radius:13px;padding:4px 9px;text-align:center;font-size:12px;font-weight:700;background:#eef2f7}.status.passed{background:#dcfce7;color:#137a3d}.status.failed,.status.error{background:#fee2e2;color:#a71930}.status.skipped,.status.xfailed{background:#fef3c7;color:#8a5a00}.status.xpassed{background:#e0e7ff;color:#4338ca}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#181f2a;color:#edf2f7;border-radius:6px;padding:14px;max-height:500px;overflow:auto}.screenshot img{display:block;max-width:100%;max-height:600px;margin-top:10px;border:1px solid var(--line)}
.empty{color:var(--muted);text-align:center;padding:16px}
@media(max-width:850px){.overview-grid{grid-template-columns:1fr}.chart-panel{justify-content:center}.metrics{grid-template-columns:repeat(3,1fr)}.section-heading{align-items:start;flex-direction:column;gap:10px}.search,input{width:100%;margin:4px 0}.test-main{grid-template-columns:95px 1fr}.duration{display:none}}
@media(max-width:520px){.metrics{grid-template-columns:repeat(2,1fr)}.chart-panel{align-items:flex-start}.donut{width:140px;height:140px;flex-basis:140px}.donut:after{width:86px;height:86px}}
"""


def _script() -> str:
    return """
const filters=document.querySelectorAll('[data-filter]');const search=document.getElementById('search');
let selected='all';
function applyFilters(){const query=(search.value||'').toLowerCase();let visible=0;
document.querySelectorAll('.test-row').forEach(row=>{const matchesStatus=selected==='all'||row.dataset.status===selected;
const matchesSearch=row.dataset.search.includes(query);row.hidden=!(matchesStatus&&matchesSearch);if(!row.hidden)visible++;});
document.getElementById('no-results').hidden=visible!==0;}
filters.forEach(button=>button.addEventListener('click',()=>{selected=button.dataset.filter;
document.querySelectorAll('.filter').forEach(item=>item.classList.toggle('active',item.dataset.filter===selected));applyFilters();}));
search.addEventListener('input',applyFilters);
"""
