"""Grafana Service Interface (Port).

Defines the abstract interface for Grafana dashboard and metrics operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MetricDataPoint:
    """A single metric data point."""
    timestamp: str
    value: float
    labels: dict = field(default_factory=dict)


@dataclass
class DashboardPanel:
    """Represents a panel in a Grafana dashboard."""
    id: str
    title: str
    panel_type: str  # graph, gauge, table, stat
    data: list[MetricDataPoint] = field(default_factory=list)


@dataclass
class Dashboard:
    """Represents a Grafana dashboard."""
    id: str
    title: str
    url: str = ""
    panels: list[DashboardPanel] = field(default_factory=list)


class GrafanaService(ABC):
    """Abstract interface for Grafana operations.

    Implementations:
    - MockGrafanaAdapter: Calls mock Grafana server
    - RealGrafanaAdapter: Calls real Grafana API (stub)
    """

    @abstractmethod
    async def get_dashboard(self, dashboard_id: str, base_url: Optional[str] = None) -> Dashboard:
        """Get a dashboard by ID."""
        ...

    @abstractmethod
    async def get_metrics(
        self,
        query: str,
        base_url: Optional[str] = None,
        time_range: Optional[str] = None,
    ) -> list[MetricDataPoint]:
        """Query metrics from Prometheus via Grafana."""
        ...

    @abstractmethod
    async def list_dashboards(self, base_url: Optional[str] = None) -> list[Dashboard]:
        """List all available dashboards."""
        ...
