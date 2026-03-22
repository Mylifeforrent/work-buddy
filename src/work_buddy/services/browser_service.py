"""Browser Service Interface (Port).

Defines the abstract interface for browser automation operations.
Used by the Browser Test Agent for screenshot capture from React apps
and monitoring dashboards (OpenSearch, SpringBoot Admin, Grafana).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Screenshot:
    """Represents a captured screenshot."""
    path: str
    label: str
    timestamp: str
    url: str = ""
    width: int = 1920
    height: int = 1080


@dataclass
class EvidencePackage:
    """A collection of screenshots and metadata from a test flow."""
    project_name: str
    flow_name: str
    source_tool: str  # react-app, opensearch, springboot-admin, grafana
    screenshots: list[Screenshot] = field(default_factory=list)
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class BrowserService(ABC):
    """Abstract interface for browser automation.

    Implementations:
    - PlaywrightBrowserService: Real browser via Playwright
    """

    @abstractmethod
    async def launch(self, headless: bool = True) -> None:
        """Launch the browser."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        ...

    @abstractmethod
    async def navigate(self, url: str) -> None:
        """Navigate to a URL."""
        ...

    @abstractmethod
    async def screenshot(self, path: str, full_page: bool = False) -> Screenshot:
        """Capture a screenshot of the current page.

        Args:
            path: File path to save the screenshot
            full_page: If True, capture the full scrollable page

        Returns:
            Screenshot metadata
        """
        ...

    @abstractmethod
    async def click(self, selector: str) -> None:
        """Click an element matching the CSS selector."""
        ...

    @abstractmethod
    async def type_text(self, selector: str, text: str) -> None:
        """Type text into an input element."""
        ...

    @abstractmethod
    async def wait_for(self, selector: str, timeout: int = 30000) -> None:
        """Wait for an element to appear on the page.

        Args:
            selector: CSS selector to wait for
            timeout: Maximum wait time in milliseconds
        """
        ...

    @abstractmethod
    async def assert_text(self, selector: str, expected_text: str) -> bool:
        """Assert that an element contains the expected text.

        Returns:
            True if text matches, False otherwise
        """
        ...

    @abstractmethod
    async def get_text(self, selector: str) -> str:
        """Get the text content of an element."""
        ...

    @abstractmethod
    async def get_current_url(self) -> str:
        """Get the current page URL."""
        ...
