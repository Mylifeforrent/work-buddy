import asyncio
from datetime import datetime
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from work_buddy.services.browser_service import BrowserService, Screenshot

class RealBrowserAdapter(BrowserService):
    """Playwright implementation of BrowserService."""

    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def launch(self, headless: bool = True) -> None:
        """Launch the playwright browser and create a new page."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.page = await self.context.new_page()

    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        await self.page.goto(url, wait_until="networkidle")

    async def screenshot(self, path: str, full_page: bool = False) -> Screenshot:
        """Capture a screenshot of the current page."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        
        await self.page.screenshot(path=path, full_page=full_page)
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        url = self.page.url
        label = path.split('/')[-1].split('.')[0] # Basic label extraction
        
        return Screenshot(
            path=path,
            label=label,
            timestamp=timestamp,
            url=url,
            width=1920,
            height=1080
        )

    async def click(self, selector: str) -> None:
        """Click an element matching the CSS selector."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        await self.page.click(selector)

    async def type_text(self, selector: str, text: str) -> None:
        """Type text into an input element."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        await self.page.fill(selector, text)

    async def wait_for(self, selector: str, timeout: int = 30000) -> None:
        """Wait for an element to appear on the page."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        await self.page.wait_for_selector(selector, timeout=timeout)

    async def assert_text(self, selector: str, expected_text: str) -> bool:
        """Assert that an element contains the expected text."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        element = await self.page.query_selector(selector)
        if not element:
            return False
        text = await element.inner_text()
        return text.strip() == expected_text.strip()

    async def get_text(self, selector: str) -> str:
        """Get the text content of an element."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        element = await self.page.wait_for_selector(selector)
        if not element:
            return ""
        return await element.inner_text()

    async def get_current_url(self) -> str:
        """Get the current page URL."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        return self.page.url
