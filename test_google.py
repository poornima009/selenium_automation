from selenium import webdriver

print("Starting Chrome...")

driver = webdriver.Chrome()

print("Chrome started")

driver.get("https://www.google.com")

print("Title:", driver.title)

input("Press Enter to close Chrome...")

driver.quit()