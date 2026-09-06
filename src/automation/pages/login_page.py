from __future__ import annotations

from automation.core.base_page import BasePage


class LoginPage(BasePage):
    EMPLOYEE_CODE = "#employeeCode"
    PASSWORD = "input[placeholder='Password']"
    SIGN_IN = "button.submit-button"
    LANDING_HEADING = "text=Welcome to NYGGS"

    def wait_until_loaded(self) -> "LoginPage":
        self.wait_for_visible(self.EMPLOYEE_CODE)
        return self

    def open(self) -> "LoginPage":
        self.goto(self.settings.base_url)
        return self.wait_until_loaded()

    def enter_employee_code(self, value: str) -> "LoginPage":
        self.fill(self.EMPLOYEE_CODE, value)
        return self

    def enter_password(self, value: str) -> "LoginPage":
        self.fill(self.PASSWORD, value)
        return self

    def submit(self) -> None:
        self.click(self.SIGN_IN)

    def login(self, username: str, password: str) -> None:
        self.enter_employee_code(username)
        self.enter_password(password)
        self.submit()

    def is_loaded(self) -> bool:
        return self.is_visible(self.EMPLOYEE_CODE)

    def error_message_visible(self) -> bool:
        return self.alert_is_visible()

    def error_message(self) -> str:
        return self.alert_text()

    def is_on_module_selection(self) -> bool:
        if "modulesSelection" in self.get_url():
            return True
        return self.is_visible(self.LANDING_HEADING)
