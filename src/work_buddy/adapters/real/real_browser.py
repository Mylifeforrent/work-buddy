import asyncio
import os
import shutil
import subprocess
from datetime import datetime
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from work_buddy.services.browser_service import BrowserService, Screenshot


class RealBrowserAdapter(BrowserService):
    """Playwright implementation of BrowserService with video recording support."""

    # CSS for custom mouse cursor overlay
    CURSOR_CSS = """
    <style id="__work_buddy_cursor_style__">
    .__work_buddy_cursor__ {
        position: fixed;
        width: 20px;
        height: 20px;
        background: radial-gradient(circle, #ff4d4f 0%, #ff7875 40%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 999999;
        transform: translate(-50%, -50%);
        transition: left 0.05s ease-out, top 0.05s ease-out;
        box-shadow: 0 0 10px rgba(255, 77, 79, 0.5);
    }
    .__work_buddy_cursor__.__clicked__ {
        background: radial-gradient(circle, #52c41a 0%, #73d13d 40%, transparent 70%);
        box-shadow: 0 0 15px rgba(82, 196, 26, 0.7);
        transform: translate(-50%, -50%) scale(1.3);
    }
    </style>
    """

    CURSOR_HTML = """
    <div class="__work_buddy_cursor__" id="__work_buddy_cursor__"></div>
    """

    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._recording_dir: Optional[str] = None
        self._recording_context: Optional[BrowserContext] = None
        self._recording_page: Optional[Page] = None
        self._recording_start_time: Optional[datetime] = None
        self._cursor_visible: bool = False

    async def launch(self, headless: bool = True) -> None:
        """Launch the playwright browser and create a new page."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.page = await self.context.new_page()

    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        # Close recording context if active
        if self._recording_context:
            try:
                await self._recording_page.close()
                await self._recording_context.close()
            except Exception:
                pass
            self._recording_context = None
            self._recording_page = None

        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        page = self._active_page()
        await page.goto(url, wait_until="networkidle")

        # Re-setup cursor tracking after navigation (for recording page)
        if self._recording_page:
            await asyncio.sleep(0.5)  # Wait for page to settle
            await self._setup_cursor_tracking()

    async def screenshot(self, path: str, full_page: bool = False) -> Screenshot:
        """Capture a screenshot of the current page."""
        page = self._active_page()

        await page.screenshot(path=path, full_page=full_page)

        timestamp = datetime.utcnow().isoformat() + "Z"
        url = page.url
        label = path.split('/')[-1].split('.')[0]  # Basic label extraction

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
        page = self._active_page()

        # Show cursor at element location before clicking (for recording visibility)
        if self._recording_page:
            try:
                element = await page.query_selector(selector)
                if element:
                    box = await element.bounding_box()
                    if box:
                        # Move cursor to element center
                        x = box['x'] + box['width'] / 2
                        y = box['y'] + box['height'] / 2
                        await self._move_cursor_to(x, y)
                        await asyncio.sleep(0.1)  # Brief pause to show cursor
            except Exception:
                pass

        await page.click(selector)

        # Show click animation
        if self._recording_page:
            await self._show_click_animation()

    async def type_text(self, selector: str, text: str) -> None:
        """Type text into an input element."""
        page = self._active_page()

        # Show cursor at element location (for recording visibility)
        if self._recording_page:
            try:
                element = await page.query_selector(selector)
                if element:
                    box = await element.bounding_box()
                    if box:
                        x = box['x'] + box['width'] / 2
                        y = box['y'] + box['height'] / 2
                        await self._move_cursor_to(x, y)
                        await asyncio.sleep(0.1)
            except Exception:
                pass

        await page.fill(selector, text)

    async def wait_for(self, selector: str, timeout: int = 30000) -> None:
        """Wait for an element to appear on the page."""
        page = self._active_page()
        await page.wait_for_selector(selector, timeout=timeout)

    async def assert_text(self, selector: str, expected_text: str) -> bool:
        """Assert that an element contains the expected text."""
        page = self._active_page()
        element = await page.query_selector(selector)
        if not element:
            return False
        text = await element.inner_text()
        return text.strip() == expected_text.strip()

    async def get_text(self, selector: str) -> str:
        """Get the text content of an element."""
        page = self._active_page()
        element = await page.wait_for_selector(selector)
        if not element:
            return ""
        return await element.inner_text()

    async def get_current_url(self) -> str:
        """Get the current page URL."""
        page = self._active_page()
        return page.url

    # ── Video Recording (V2) ──────────────────────────────────────────────────

    async def start_recording(self, output_dir: str) -> None:
        """Start recording by creating a new browser context with video enabled.

        Playwright records video at the context level, so we create a dedicated
        recording context with record_video_dir set. The recording page becomes
        the active page for all subsequent browser operations until stop_recording.
        """
        if not self.browser:
            raise RuntimeError("Browser not launched")

        os.makedirs(output_dir, exist_ok=True)
        self._recording_dir = output_dir

        # Create a new context with video recording enabled
        self._recording_context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=output_dir,
            record_video_size={"width": 1280, "height": 720}
        )
        self._recording_page = await self._recording_context.new_page()
        self._recording_start_time = datetime.utcnow()
        self._cursor_visible = False

        # Set up cursor tracking for recording page
        await self._setup_cursor_tracking()

    async def stop_recording(self) -> str:
        """Stop recording, close the recording context, and return video path.

        Playwright finalizes the video file when the page/context is closed.
        """
        if not self._recording_page or not self._recording_context:
            return ""

        # Get the video object before closing
        video = self._recording_page.video
        if not video:
            await self._recording_context.close()
            self._recording_context = None
            self._recording_page = None
            return ""

        # Close the page — this triggers Playwright to finalize the video
        await self._recording_page.close()

        # Get the path where Playwright saved the video
        video_path = await video.path()

        # Close the recording context
        await self._recording_context.close()
        self._recording_context = None
        self._recording_page = None
        self._recording_start_time = None

        return str(video_path) if video_path else ""

    async def convert_to_gif(self, video_path: str, gif_path: str,
                              fps: int = 10, scale: int = 800) -> str:
        """Convert a WebM video to GIF using ffmpeg.

        Falls back gracefully if ffmpeg is not installed.
        """
        if not os.path.exists(video_path):
            return ""

        # Check if ffmpeg is available
        if not shutil.which("ffmpeg"):
            print("Warning: ffmpeg not found. Skipping GIF conversion.")
            return ""

        try:
            # ffmpeg command: video → palette-based GIF for quality
            palette_path = video_path + ".palette.png"

            # Step 1: Generate palette for high-quality GIF
            palette_cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos,palettegen",
                palette_path
            ]

            # Step 2: Use palette to create GIF
            gif_cmd = [
                "ffmpeg", "-y", "-i", video_path, "-i", palette_path,
                "-lavfi", f"fps={fps},scale={scale}:-1:flags=lanczos [x]; [x][1:v] paletteuse",
                gif_path
            ]

            # Run palette generation
            process = await asyncio.create_subprocess_exec(
                *palette_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()

            if process.returncode != 0:
                # Fallback: simple conversion without palette
                simple_cmd = [
                    "ffmpeg", "-y", "-i", video_path,
                    "-vf", f"fps={fps},scale={scale}:-1",
                    gif_path
                ]
                process = await asyncio.create_subprocess_exec(
                    *simple_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()

            # Clean up palette file
            if os.path.exists(palette_path):
                os.remove(palette_path)

            if os.path.exists(gif_path):
                return gif_path
            return ""

        except Exception as e:
            print(f"Warning: GIF conversion failed: {e}")
            return ""

    # ── Internal helpers ────────────────────────────────────────────────────

    def _active_page(self) -> Page:
        """Return the currently active page (recording page if recording, else default)."""
        if self._recording_page:
            return self._recording_page
        if not self.page:
            raise RuntimeError("Browser not launched")
        return self.page

    # ── Cursor Visibility for Recordings ─────────────────────────────────────

    async def _setup_cursor_tracking(self) -> None:
        """Set up the custom cursor overlay on the recording page."""
        if not self._recording_page:
            return

        try:
            # Inject cursor CSS and HTML
            await self._recording_page.evaluate(f"""
                document.head.insertAdjacentHTML('beforeend', `{self.CURSOR_CSS}`);
                document.body.insertAdjacentHTML('beforeend', `{self.CURSOR_HTML}`);
            """)
            self._cursor_visible = True
        except Exception:
            pass

    async def _move_cursor_to(self, x: float, y: float) -> None:
        """Move the custom cursor to a specific position."""
        if not self._recording_page or not self._cursor_visible:
            return

        try:
            await self._recording_page.evaluate(f"""
                const cursor = document.getElementById('__work_buddy_cursor__');
                if (cursor) {{
                    cursor.style.left = '{x}px';
                    cursor.style.top = '{y}px';
                    cursor.style.display = 'block';
                }}
            """)
        except Exception:
            pass

    async def _show_click_animation(self) -> None:
        """Show a brief click animation on the cursor."""
        if not self._recording_page or not self._cursor_visible:
            return

        try:
            await self._recording_page.evaluate("""
                const cursor = document.getElementById('__work_buddy_cursor__');
                if (cursor) {
                    cursor.classList.add('__clicked__');
                    setTimeout(() => cursor.classList.remove('__clicked__'), 200);
                }
            """)
        except Exception:
            pass

    async def _hide_cursor(self) -> None:
        """Hide the custom cursor."""
        if not self._recording_page or not self._cursor_visible:
            return

        try:
            await self._recording_page.evaluate("""
                const cursor = document.getElementById('__work_buddy_cursor__');
                if (cursor) {
                    cursor.style.display = 'none';
                }
            """)
        except Exception:
            pass
