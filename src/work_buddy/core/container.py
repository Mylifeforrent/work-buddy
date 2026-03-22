"""Dependency Injection Container for Work Buddy.

Selects mock or real adapters based on the global app configuration.
Agents depend on service interfaces (ABCs), never on concrete implementations.
"""

from work_buddy.core.config import AppConfig
from work_buddy.core.logging import get_logger

logger = get_logger(__name__)


class ServiceContainer:
    """Dependency injection container that holds all service adapters.

    Usage:
        config = load_app_config()
        container = create_container(config)
        jira = container.jira_service  # Returns JiraService ABC implementation
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._jira_service = None
        self._confluence_service = None
        self._opensearch_service = None
        self._grafana_service = None
        self._springboot_admin_service = None
        self._sso_auth_service = None
        self._credential_store = None
        self._browser_service = None

    @property
    def jira_service(self):
        """Get JiraService adapter (mock or real based on config)."""
        if self._jira_service is None:
            if self.config.mode == "mock":
                from work_buddy.adapters.mock.mock_jira import MockJiraAdapter
                self._jira_service = MockJiraAdapter(base_url=self.config.mock_jira_url)
                logger.info("Using MockJiraAdapter", extra={"agent": "container"})
            else:
                from work_buddy.adapters.real.real_jira import RealJiraAdapter
                self._jira_service = RealJiraAdapter()
                logger.info("Using RealJiraAdapter", extra={"agent": "container"})
        return self._jira_service

    @property
    def confluence_service(self):
        """Get ConfluenceService adapter (mock or real based on config)."""
        if self._confluence_service is None:
            if self.config.mode == "mock":
                from work_buddy.adapters.mock.mock_confluence import MockConfluenceAdapter
                self._confluence_service = MockConfluenceAdapter(base_url=self.config.mock_confluence_url)
                logger.info("Using MockConfluenceAdapter", extra={"agent": "container"})
            else:
                from work_buddy.adapters.real.real_confluence import RealConfluenceAdapter
                self._confluence_service = RealConfluenceAdapter()
                logger.info("Using RealConfluenceAdapter", extra={"agent": "container"})
        return self._confluence_service

    @property
    def opensearch_service(self):
        """Get OpenSearchService adapter (mock or real based on config)."""
        if self._opensearch_service is None:
            if self.config.mode == "mock":
                from work_buddy.adapters.mock.mock_opensearch import MockOpenSearchAdapter
                self._opensearch_service = MockOpenSearchAdapter()
                logger.info("Using MockOpenSearchAdapter", extra={"agent": "container"})
            else:
                from work_buddy.adapters.real.real_opensearch import RealOpenSearchAdapter
                self._opensearch_service = RealOpenSearchAdapter()
                logger.info("Using RealOpenSearchAdapter", extra={"agent": "container"})
        return self._opensearch_service

    @property
    def grafana_service(self):
        """Get GrafanaService adapter (mock or real based on config)."""
        if self._grafana_service is None:
            if self.config.mode == "mock":
                from work_buddy.adapters.mock.mock_grafana import MockGrafanaAdapter
                self._grafana_service = MockGrafanaAdapter()
                logger.info("Using MockGrafanaAdapter", extra={"agent": "container"})
            else:
                from work_buddy.adapters.real.real_grafana import RealGrafanaAdapter
                self._grafana_service = RealGrafanaAdapter()
                logger.info("Using RealGrafanaAdapter", extra={"agent": "container"})
        return self._grafana_service

    @property
    def springboot_admin_service(self):
        """Get SpringBootAdminService adapter (mock or real based on config)."""
        if self._springboot_admin_service is None:
            if self.config.mode == "mock":
                from work_buddy.adapters.mock.mock_springboot_admin import MockSpringBootAdminAdapter
                self._springboot_admin_service = MockSpringBootAdminAdapter()
                logger.info("Using MockSpringBootAdminAdapter", extra={"agent": "container"})
            else:
                from work_buddy.adapters.real.real_springboot_admin import RealSpringBootAdminAdapter
                self._springboot_admin_service = RealSpringBootAdminAdapter()
                logger.info("Using RealSpringBootAdminAdapter", extra={"agent": "container"})
        return self._springboot_admin_service

    @property
    def sso_auth_service(self):
        """Get SSOAuthService adapter (mock or real based on config)."""
        if self._sso_auth_service is None:
            if self.config.mode == "mock":
                from work_buddy.adapters.mock.mock_sso import MockSSOAuthAdapter
                self._sso_auth_service = MockSSOAuthAdapter(sso_url=self.config.mock_sso_url)
                logger.info("Using MockSSOAuthAdapter", extra={"agent": "container"})
            else:
                from work_buddy.adapters.real.real_sso import RealSSOAuthAdapter
                self._sso_auth_service = RealSSOAuthAdapter()
                logger.info("Using RealSSOAuthAdapter", extra={"agent": "container"})
        return self._sso_auth_service

    @property
    def credential_store(self):
        """Get CredentialStore adapter (mock or real based on config)."""
        if self._credential_store is None:
            if self.config.mode == "mock":
                from work_buddy.adapters.mock.mock_credentials import MockCredentialStore
                self._credential_store = MockCredentialStore()
                logger.info("Using MockCredentialStore", extra={"agent": "container"})
            else:
                from work_buddy.adapters.real.real_credentials import RealCredentialStore
                self._credential_store = RealCredentialStore()
                logger.info("Using RealCredentialStore", extra={"agent": "container"})
        return self._credential_store


def create_container(config: AppConfig) -> ServiceContainer:
    """Create a service container with the given configuration.

    Args:
        config: Global app configuration

    Returns:
        ServiceContainer with lazy-loaded adapters
    """
    logger.info(f"Creating service container in '{config.mode}' mode", extra={"agent": "container"})
    return ServiceContainer(config)
