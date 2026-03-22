import pytest
import os
import json
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

from work_buddy.agents.browser_test_agent import BrowserTestAgent
from work_buddy.services.browser_service import Screenshot
from work_buddy.core.config import ProjectConfig, TestFlow, TestStep, AuthConfig, ToolUrls, EvidenceCheck


def _make_screenshot(path="mock_path.png", label="mock"):
    """Create a real Screenshot dataclass (not a MagicMock) for JSON serialization."""
    return Screenshot(
        path=path,
        label=label,
        timestamp="2023-01-01T00:00:00Z",
        url="http://mock",
        width=1920,
        height=1080
    )


@pytest.fixture
def mock_browser():
    browser = AsyncMock(unsafe=True)
    browser.get_current_url.return_value = "http://localhost:8080/somepage"
    browser.assert_text.return_value = True
    browser.screenshot.return_value = _make_screenshot()
    browser.start_recording.return_value = None
    browser.stop_recording.return_value = ""  # No video path by default
    browser.convert_to_gif.return_value = ""
    return browser


@pytest.fixture
def agent(mock_browser, tmp_path):
    return BrowserTestAgent(browser=mock_browser, output_dir=str(tmp_path), enable_recording=True)


@pytest.fixture
def agent_no_recording(mock_browser, tmp_path):
    return BrowserTestAgent(browser=mock_browser, output_dir=str(tmp_path), enable_recording=False)


@pytest.mark.asyncio
async def test_execute_react_flow_success(agent, mock_browser):
    project = ProjectConfig(
        name="test-project",
        type="react-app",
        base_url="http://localhost:3000",
        auth=AuthConfig(type="none")
    )
    flow = TestFlow(
        name="login_flow",
        steps=[
            TestStep(action="navigate", target="/login"),
            TestStep(action="type", target="#username", value="user"),
            TestStep(action="click", target="#submit"),
            TestStep(action="wait_for", target=".dashboard"),
            TestStep(action="screenshot", label="dashboard_view")
        ]
    )
    
    pkg = await agent.execute_react_flow(project, flow)
    
    assert pkg.passed is True
    assert pkg.project_name == "test-project"
    assert pkg.flow_name == "login_flow"
    assert len(pkg.errors) == 0
    assert len(pkg.screenshots) == 1
    
    # Verify browser interactions
    assert mock_browser.navigate.call_count >= 2  # once for base_url, once for step
    mock_browser.type_text.assert_called_with("#username", "user")
    mock_browser.click.assert_called_with("#submit")
    mock_browser.wait_for.assert_called_with(".dashboard")
    mock_browser.screenshot.assert_called()


@pytest.mark.asyncio
async def test_capture_opensearch(agent, mock_browser):
    project = ProjectConfig(
        name="backend-server",
        type="backend",
        tool_urls=ToolUrls(opensearch="http://localhost:9200/dashboards"),
        auth=AuthConfig(type="none"),
        evidence_checks={
            "opensearch": [
                EvidenceCheck(query="error OR Exception", screenshot_label="errors", name="chk1")
            ]
        }
    )
    
    pkg = await agent.capture_opensearch(project)
    
    assert pkg.passed is True
    assert pkg.source_tool == "opensearch"
    assert len(pkg.screenshots) == 1
    mock_browser.navigate.assert_called_with("http://localhost:9200/dashboards")


# ── Video Recording Tests (V2) ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_recording_lifecycle_during_react_flow(agent, mock_browser):
    """Verify that start_recording is called before flow and stop_recording after."""
    project = ProjectConfig(
        name="test-app",
        type="react-app",
        base_url="http://localhost:3000",
        auth=AuthConfig(type="none")
    )
    flow = TestFlow(
        name="checkout",
        steps=[
            TestStep(action="screenshot", label="checkout_page")
        ]
    )
    
    pkg = await agent.execute_react_flow(project, flow)
    
    # Recording should have been started and stopped
    mock_browser.start_recording.assert_called_once()
    mock_browser.stop_recording.assert_called_once()


@pytest.mark.asyncio
async def test_recording_disabled_skips_recording(agent_no_recording, mock_browser):
    """Verify recording is skipped when enable_recording=False."""
    project = ProjectConfig(
        name="test-app",
        type="react-app",
        base_url="http://localhost:3000",
        auth=AuthConfig(type="none")
    )
    flow = TestFlow(
        name="checkout",
        steps=[
            TestStep(action="screenshot", label="checkout_page")
        ]
    )
    
    pkg = await agent_no_recording.execute_react_flow(project, flow)
    
    # Recording should NOT have been called
    mock_browser.start_recording.assert_not_called()
    mock_browser.stop_recording.assert_not_called()
    assert len(pkg.recordings) == 0
    assert len(pkg.gifs) == 0


@pytest.mark.asyncio
async def test_recording_with_video_produces_evidence(agent, mock_browser, tmp_path):
    """Verify that when stop_recording returns a video, recordings and gifs are populated."""
    # Create a fake video file that stop_recording will return
    fake_video = str(tmp_path / "recordings" / "fake_video.webm")
    os.makedirs(os.path.dirname(fake_video), exist_ok=True)
    with open(fake_video, "wb") as f:
        f.write(b"fake video content")
    
    mock_browser.stop_recording.return_value = fake_video
    mock_browser.convert_to_gif.return_value = str(tmp_path / "gifs" / "preview.gif")
    
    # Create fake gif file
    os.makedirs(str(tmp_path / "gifs"), exist_ok=True)
    with open(str(tmp_path / "gifs" / "preview.gif"), "wb") as f:
        f.write(b"fake gif content")
    
    project = ProjectConfig(
        name="video-test",
        type="react-app",
        base_url="http://localhost:3000",
        auth=AuthConfig(type="none")
    )
    flow = TestFlow(
        name="demo_flow",
        steps=[TestStep(action="screenshot", label="step1")]
    )
    
    pkg = await agent.execute_react_flow(project, flow)
    
    # Should have recording and GIF
    assert len(pkg.recordings) == 1
    assert pkg.recordings[0].format == "webm"
    assert len(pkg.gifs) == 1
    assert pkg.gifs[0].format == "gif"
    
    # Verify convert_to_gif was called
    mock_browser.convert_to_gif.assert_called_once()


@pytest.mark.asyncio
async def test_recording_during_opensearch_capture(agent, mock_browser):
    """Verify recording is started/stopped during opensearch capture."""
    project = ProjectConfig(
        name="backend-svc",
        type="backend",
        tool_urls=ToolUrls(opensearch="http://localhost:9200"),
        auth=AuthConfig(type="none"),
        evidence_checks={
            "opensearch": [
                EvidenceCheck(query="error", screenshot_label="err", name="check1")
            ]
        }
    )
    
    pkg = await agent.capture_opensearch(project)
    
    mock_browser.start_recording.assert_called_once()
    mock_browser.stop_recording.assert_called_once()



@pytest.mark.asyncio
async def test_evidence_package_includes_recordings_in_metadata(agent, mock_browser, tmp_path):
    """Verify the metadata JSON includes recordings and gifs fields."""
    project = ProjectConfig(
        name="meta-test",
        type="react-app",
        base_url="http://localhost:3000",
        auth=AuthConfig(type="none")
    )
    flow = TestFlow(
        name="meta_flow",
        steps=[TestStep(action="screenshot", label="view")]
    )
    
    pkg = await agent.execute_react_flow(project, flow)
    
    # Check that the metadata JSON was written with recordings/gifs keys
    meta_path = os.path.join(str(tmp_path), "meta-test_meta_flow_react-app_package.json")
    assert os.path.exists(meta_path)
    with open(meta_path) as f:
        data = json.load(f)
    assert "recordings" in data
    assert "gifs" in data


@pytest.mark.asyncio
async def test_recording_failure_is_graceful(agent, mock_browser):
    """Verify that if start_recording fails, the flow still executes normally."""
    mock_browser.start_recording.side_effect = RuntimeError("Recording not supported")
    
    project = ProjectConfig(
        name="fallback-test",
        type="react-app",
        base_url="http://localhost:3000",
        auth=AuthConfig(type="none")
    )
    flow = TestFlow(
        name="simple",
        steps=[TestStep(action="screenshot", label="page")]
    )
    
    # Should not raise, just skip recording
    pkg = await agent.execute_react_flow(project, flow)
    assert pkg.passed is True
    assert len(pkg.screenshots) == 1
    assert len(pkg.recordings) == 0
