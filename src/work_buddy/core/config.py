"""Configuration management for Work Buddy.

Handles loading and validation of:
- app.yaml: Global configuration (mode, log level, common settings)
- configs/projects/*.yaml: Per-project configurations
"""

from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, Field


# ── Project root detection ────────────────────────────────────────────────────

def _find_project_root() -> Path:
    """Find the project root by looking for configs/ directory."""
    # Try common locations
    candidates = [
        Path.cwd(),
        Path.cwd().parent,
        Path(__file__).parent.parent.parent.parent,  # src/work_buddy/core/ -> project root
    ]
    for candidate in candidates:
        if (candidate / "configs").is_dir():
            return candidate
    # Default to cwd
    return Path.cwd()


PROJECT_ROOT = _find_project_root()
CONFIGS_DIR = PROJECT_ROOT / "configs"
PROJECTS_DIR = CONFIGS_DIR / "projects"


# ── App Configuration ─────────────────────────────────────────────────────────

class AppConfig(BaseModel):
    """Global application configuration."""
    mode: Literal["mock", "live"] = "mock"
    log_level: str = "INFO"
    structured_logging: bool = False

    # Mock server URLs (used when mode=mock)
    mock_jira_url: str = "http://localhost:8081"
    mock_confluence_url: str = "http://localhost:8082"
    mock_sso_url: str = "http://localhost:8090"

    # LLM settings
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"

    # Evidence storage
    evidence_dir: str = "evidence"
    screenshots_dir: str = "screenshots"


# ── Project Configuration ─────────────────────────────────────────────────────

class EvidenceCheck(BaseModel):
    """A single evidence check configuration."""
    name: str
    query: Optional[str] = None
    screenshot_label: Optional[str] = None


class SpringBootAdminCheck(BaseModel):
    """SpringBoot Admin health check configuration."""
    service_name: str
    check: str = "r2db_status"
    expected: str = "UP"
    screenshot_label: Optional[str] = None


class GrafanaCheck(BaseModel):
    """Grafana dashboard check configuration."""
    dashboard_id: str
    screenshot_label: Optional[str] = None


class TestStep(BaseModel):
    """A single step in a browser test flow."""
    action: str  # navigate, click, type, wait_for, screenshot, assert_text
    target: Optional[str] = None  # URL, selector, or text
    value: Optional[str] = None  # Value for type action
    label: Optional[str] = None  # Label for screenshot


class TestFlow(BaseModel):
    """A named test flow with ordered steps."""
    name: str
    steps: list[TestStep]


class AuthConfig(BaseModel):
    """Authentication configuration."""
    type: Literal["corporate-sso", "form-login", "none"] = "corporate-sso"
    username_selector: str = "#username"
    password_selector: str = "#password"
    submit_selector: str = "#submit"
    sso_url: Optional[str] = None


class ToolUrls(BaseModel):
    """URLs for monitoring tool instances."""
    opensearch: Optional[str] = None
    springboot_admin: Optional[str] = None
    grafana: Optional[str] = None


class JiraConfig(BaseModel):
    """Jira configuration for a project."""
    project_key: str
    epic: Optional[str] = None
    sprint_board: Optional[str] = None
    labels: list[str] = Field(default_factory=list)
    components: list[str] = Field(default_factory=list)
    description_template: Optional[str] = None


class PostmanConfig(BaseModel):
    """Postman configuration for API testing."""
    collection: str
    environment: Optional[str] = None


class ProjectConfig(BaseModel):
    """Per-project configuration."""
    name: str
    type: Literal["react-app", "backend"] = "backend"
    base_url: Optional[str] = None  # For React apps

    # Jira settings
    jira: Optional[JiraConfig] = None

    # Authentication
    auth: AuthConfig = Field(default_factory=AuthConfig)

    # Monitoring tool URLs (per-project, since instances may differ)
    tool_urls: ToolUrls = Field(default_factory=ToolUrls)

    # Evidence checks
    evidence_checks: Optional[dict[str, list[EvidenceCheck]]] = None
    springboot_admin_checks: list[SpringBootAdminCheck] = Field(default_factory=list)
    grafana_checks: list[GrafanaCheck] = Field(default_factory=list)

    # Browser test flows (for React apps)
    test_flows: list[TestFlow] = Field(default_factory=list)

    # Postman (for backend services)
    postman: Optional[PostmanConfig] = None


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_app_config() -> AppConfig:
    """Load global app configuration from configs/app.yaml."""
    config_path = CONFIGS_DIR / "app.yaml"
    if not config_path.exists():
        return AppConfig()

    with open(config_path) as f:
        data = yaml.safe_load(f) or {}

    return AppConfig(**data)


def load_project_config(project_name: str) -> ProjectConfig:
    """Load a project configuration by name.

    Args:
        project_name: Name of the project (matches YAML filename without extension)

    Returns:
        ProjectConfig instance

    Raises:
        FileNotFoundError: If no config file found for the project
        ValueError: If config validation fails
    """
    config_path = PROJECTS_DIR / f"{project_name}.yaml"
    if not config_path.exists():
        available = list_projects()
        raise FileNotFoundError(
            f"No configuration found for project '{project_name}'. "
            f"Available projects: {', '.join(available) if available else 'none'}"
        )

    with open(config_path) as f:
        data = yaml.safe_load(f) or {}

    return ProjectConfig(**data)


def list_projects() -> list[str]:
    """List all configured project names.

    Returns:
        List of project names (YAML filenames without extension)
    """
    if not PROJECTS_DIR.exists():
        return []

    return sorted([
        p.stem for p in PROJECTS_DIR.glob("*.yaml")
        if not p.name.startswith("_")
    ])
