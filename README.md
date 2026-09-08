# NYGGS Playwright automation

Python + Playwright suite for the NYGGS SSO portal at https://demosso.nyggs.com/.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

Put `SSO_USERNAME` and `SSO_PASSWORD` in `.env`. Do not commit `.env`.

## Run tests

```bash
pytest tests/test_login.py -v
pytest tests/test_module_selection.py -v
pytest tests/test_site_selection.py -v
pytest tests/test_store_tiles.py -v
pytest tests/test_store_list_flows.py -v
pytest tests -v
```

Set `HEADLESS=false` to watch the browser. Set `SLOW_MO_MS=1000` to pause about one second between actions.

## HTML reports

Every pytest invocation automatically creates an immutable result folder:

```text
reports/runs/YYYYMMDD_HHMMSS_microseconds/
├── report.html
├── results.json
└── failures/
```

Open `report.html` in a browser to see discovered and executed totals, every test
status, durations, error tracebacks, and available failure screenshots. The
history section compares the latest three saved runs and highlights tests whose
status changed. Until three runs exist, it compares the available history.

`Not Run` means a test was discovered for the current pytest invocation but did
not execute. Tests excluded before collection, such as files outside a supplied
test path, are not part of that run's inventory.

## Layout

- `src/automation/core/` — shared library (browser, BasePage, waits, logger)
- `src/automation/pages/` — page objects
- `src/automation/flows/` — reusable multi-step flows
- `tests/` — pytest tests

Team standards: `.cursor/skills/nyggs-automation-standards/SKILL.md`
