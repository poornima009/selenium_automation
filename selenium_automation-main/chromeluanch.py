import asyncio
from playwright.async_api import async_playwright, Playwright


async def run(playwright: Playwright):
    browser = await playwright.chromium.launch(
        headless=False
    )

    page = await browser.new_page()

    print("Opening website...")

    await page.goto(
        "https://nkcssoqa.nyggs.com/",
        wait_until="domcontentloaded"
    )

    print("Page title:", await page.title())
    print("Current URL:", page.url)

    # Wait for login fields
    await page.locator("#employeeCode").wait_for()
    await page.locator("#password").wait_for()

    print("Entering User ID...")
    await page.locator("#employeeCode").fill("ss031")

    print("Entering Password...")
    await page.locator("#password").fill("1234567")

    print("Clicking Login...")
    await page.locator('button[type="sign in"]').click()

    await page.wait_for_load_state("networkidle")

    print("Login completed")
    print("Current URL:", page.url)

    # Keep browser open for 10 seconds
    await page.wait_for_timeout(10000)

    await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())