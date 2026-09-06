---
name: nyggs-automation-standards
description: Enforces NYGGS Playwright POM standards, common-library reuse, low cognitive complexity, and safe test practices. Use when adding or changing pages, flows, core helpers, pytest tests, locators, or framework code in this repo.
---

# NYGGS automation standards

Follow this skill for every Python change in this repo. Keep the suite readable for multiple people.

## Layout (do not invent a new one)

```
src/automation/config/     # settings from env
src/automation/core/       # shared library only
src/automation/pages/      # one class per screen
src/automation/flows/      # multi-step reuse
tests/                     # pytest only
```

- Python 3 + Playwright **sync** API + pytest.
- Do not add Selenium, a second runner, or JS/TS Playwright tests.

## Architecture

- **Page Object Model.** Locators and page actions live on page classes. Tests never call `page.locator`, CSS, or XPath.
- **Common library.** Shared click/fill/wait/log/browser code goes in `src/automation/core/`. If you would copy five lines, put it in `core/` instead.
- **Flows.** Multi-step paths (`LoginFlow.login_as`) live in `flows/`. Tests call flows or page methods, not raw steps.
- **One screen = one page class.** One product app = one package under `pages/`.
- **Allowed patterns only:** Page Object, Factory (browser), Facade (flows), Settings. Do not add a new pattern for one page.

## Low cognitive complexity

- One job per function. Early returns over deep `if/else`.
- Nesting at most two levels. Split a method if it grows past ~30 lines.
- No `time.sleep` / `wait_for_timeout` for synchronization. Use `BasePage` waits.
- No dead code, unused imports, or commented-out scripts.
- Names say the action: `enter_employee_code`, not `do_stuff`, `temp`, or `x`.

## Coding practice

- Type hints on public methods.
- No hardcoded URLs, usernames, or passwords. Read `get_settings()` / env only.
- Never commit `.env` or secrets.
- Prefer locators: id, label, placeholder, role. No absolute XPath.
- Page methods return data or `self`. Assertions belong in tests.
- Tests are independent, named `test_<behavior>`, and assert one outcome.
- Failures must be readable: log actions through the shared logger.

## When adding a screen

1. Add or reuse a helper in `core/` if the action is generic.
2. Create `pages/<screen>_page.py` with locators as class attributes or a small locators block.
3. If two or more tests share the steps, add `flows/<name>_flow.py`.
4. Add `tests/test_<screen>.py`. Wire fixtures from `tests/conftest.py` only.

## Review gate

- [ ] New locator is on a page class, not a test
- [ ] Shared helper is in `core/`, not copied
- [ ] No secrets, no sleep, no extra dependencies
- [ ] Names and control flow are obvious on first read
- [ ] One concern per change

For good vs bad snippets, see [examples.md](examples.md).
