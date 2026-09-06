# Examples

## Page object — good

```python
class LoginPage(BasePage):
    EMPLOYEE_CODE = "#employeeCode"
    PASSWORD = "input[placeholder='Password']"
    SIGN_IN = "button.submit-button"

    def enter_employee_code(self, value: str) -> "LoginPage":
        self.fill(self.EMPLOYEE_CODE, value)
        return self

    def submit(self) -> None:
        self.click(self.SIGN_IN)
```

## Page object — bad

```python
def test_login(page):
    page.locator("#employeeCode").fill("demo-admin")
    page.wait_for_timeout(3000)
    page.locator("xpath=/html/body/div[1]/button").click()
```

## Flow — good

```python
class LoginFlow:
    def __init__(self, page: Page) -> None:
        self._login = LoginPage(page)

    def login_as(self, username: str, password: str) -> None:
        self._login.open().login(username, password)
```

## Shared helper — good

```python
# core/base_page.py
def fill(self, selector: str, value: str) -> None:
    self.wait_for_visible(selector)
    self.page.locator(selector).fill(value)
```

Copying `fill` + `wait` into a second page is not allowed. Put it in `core/`.
