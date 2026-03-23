import asyncio
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from work_buddy.services.browser_service import BrowserService, Screenshot, Recording, EvidencePackage
from work_buddy.core.config import ProjectConfig, TestFlow, TestStep, AuthConfig


class BrowserTestAgent:
    """Agent responsible for executing browser UI tests and capturing screenshots.

    V2: Added video recording and GIF conversion for evidence verification.
    Each flow execution is wrapped with start_recording/stop_recording,
    producing both WebM video and GIF preview alongside static screenshots.
    """

    def __init__(self, browser: BrowserService, output_dir: str = "evidence",
                 enable_recording: bool = True):
        self.browser = browser
        self.output_dir = output_dir
        self.baseline_dir = os.path.join(output_dir, "baseline")
        self.recordings_dir = os.path.join(output_dir, "recordings")
        self.gifs_dir = os.path.join(output_dir, "gifs")
        self.enable_recording = enable_recording
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.baseline_dir, exist_ok=True)
        os.makedirs(self.recordings_dir, exist_ok=True)
        os.makedirs(self.gifs_dir, exist_ok=True)

    async def _start_recording_if_enabled(self, label: str) -> None:
        """Start video recording if recording is enabled."""
        if self.enable_recording:
            try:
                await self.browser.start_recording(self.recordings_dir)
            except Exception as e:
                print(f"Warning: Could not start recording for {label}: {e}")

    async def _stop_recording_if_enabled(self, project_name: str, flow_name: str) -> tuple[list[Recording], list[Recording]]:
        """Stop recording and convert to GIF. Returns (recordings, gifs)."""
        recordings = []
        gifs = []

        if not self.enable_recording:
            return recordings, gifs

        try:
            video_path = await self.browser.stop_recording()
            if video_path and os.path.exists(video_path):
                timestamp = datetime.utcnow().isoformat() + "Z"
                size_bytes = os.path.getsize(video_path)

                # Rename to a descriptive name
                final_video_name = f"{project_name}_{flow_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.webm"
                final_video_path = os.path.join(self.recordings_dir, final_video_name)
                if video_path != final_video_path:
                    os.rename(video_path, final_video_path)

                recording = Recording(
                    path=final_video_path,
                    format="webm",
                    label=f"{project_name}_{flow_name}",
                    timestamp=timestamp,
                    size_bytes=size_bytes
                )
                recordings.append(recording)

                # Convert to GIF
                gif_name = f"{project_name}_{flow_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.gif"
                gif_path = os.path.join(self.gifs_dir, gif_name)
                print(f"Converting video to GIF: {final_video_path} -> {gif_path}")
                result_gif = await self.browser.convert_to_gif(final_video_path, gif_path)
                print(f"GIF conversion result: {result_gif}")
                if result_gif:
                    gif_size = os.path.getsize(result_gif) if os.path.exists(result_gif) else 0
                    gif_recording = Recording(
                        path=result_gif,
                        format="gif",
                        label=f"{project_name}_{flow_name}_preview",
                        timestamp=timestamp,
                        size_bytes=gif_size
                    )
                    gifs.append(gif_recording)

        except Exception as e:
            print(f"Warning: Recording stop/conversion failed: {e}")

        return recordings, gifs

    async def handle_sso(self, auth_config: AuthConfig, username: str = "testuser", password: str = "dummy") -> None:
        """Handle corporate SSO login if redirected to the SSO page."""
        if auth_config.type == "none" or not auth_config.sso_url:
            return
            
        current_url = await self.browser.get_current_url()
        # If the URL looks like the SSO login page (in mock mode, it's 8090/login)
        if "login" in current_url.lower() or auth_config.sso_url in current_url:
            print(f"Detected SSO login page at {current_url}. Executing login...")
            try:
                await self.browser.wait_for(auth_config.username_selector, timeout=5000)
                await self.browser.type_text(auth_config.username_selector, username)
                await self.browser.type_text(auth_config.password_selector, password)
                await self.browser.click(auth_config.submit_selector)
                # Wait for navigation back to the app
                await asyncio.sleep(3)
            except Exception as e:
                print(f"Warning: SSO handling failed: {e}")

    async def execute_react_flow(self, project: ProjectConfig, flow: TestFlow) -> EvidencePackage:
        """Execute a UI test flow for a React Web App with video recording."""
        print(f"Executing React flow '{flow.name}' for {project.name}")
        screenshots = []
        errors = []
        
        # Start recording
        await self._start_recording_if_enabled(f"{project.name}_{flow.name}")

        try:
            if project.base_url:
                await self.browser.navigate(project.base_url)
                await asyncio.sleep(2)
                await self.handle_sso(project.auth)
                
            for step in flow.steps:
                try:
                    if step.action == "navigate" and step.target:
                        await self.browser.navigate(step.target)
                        await self.handle_sso(project.auth)
                    elif step.action == "click" and step.target:
                        await self.browser.click(step.target)
                    elif step.action == "type" and step.target and step.value:
                        await self.browser.type_text(step.target, step.value)
                    elif step.action == "wait_for" and step.target:
                        await self.browser.wait_for(step.target)
                    elif step.action == "assert_text" and step.target and step.value:
                        success = await self.browser.assert_text(step.target, step.value)
                        if not success:
                            errors.append(f"Assertion failed: Expected '{step.value}' at '{step.target}'")
                    elif step.action == "screenshot":
                        label = step.label or f"step_{len(screenshots)}"
                        path = os.path.join(self.output_dir, f"{project.name}_{flow.name}_{label}.png")
                        shot = await self.browser.screenshot(path, full_page=True)
                        screenshots.append(shot)
                        
                    await asyncio.sleep(1) # Small delay between steps
                except Exception as e:
                    errors.append(f"Step {step.action} failed: {str(e)}")
                    # Try to capture failure screenshot
                    fail_path = os.path.join(self.output_dir, f"{project.name}_{flow.name}_FAILURE.png")
                    try:
                        shot = await self.browser.screenshot(fail_path)
                        screenshots.append(shot)
                    except:
                        pass
                    break
                    
        except Exception as e:
            errors.append(f"Flow execution failed: {str(e)}")

        # Stop recording and get video/GIF
        recordings, gifs = await self._stop_recording_if_enabled(project.name, flow.name)

        return self._create_package(project.name, flow.name, "react-app", screenshots, errors,
                                     recordings=recordings, gifs=gifs)

    async def capture_opensearch(self, project: ProjectConfig) -> EvidencePackage:
        """Capture OpenSearch logs dashboard screenshots with video recording."""
        url = project.tool_urls.opensearch
        if not url:
            return self._empty_package(project.name, "opensearch", "No OpenSearch URL configured")
            
        screenshots = []
        errors = []

        # Start recording
        await self._start_recording_if_enabled(f"{project.name}_opensearch")

        try:
            await self.browser.navigate(url)
            await asyncio.sleep(2)
            await self.handle_sso(project.auth)
            
            checks = project.evidence_checks.get("opensearch", []) if project.evidence_checks else []
            for check in checks:
                if check.query:
                    search_selector = "input[type='text'], input[placeholder*='Search']"
                    await self.browser.wait_for(search_selector, timeout=5000)
                    await self.browser.type_text(search_selector, check.query)
                    await asyncio.sleep(2)
                
                label = check.screenshot_label or check.name
                path = os.path.join(self.output_dir, f"{project.name}_opensearch_{label}.png")
                shot = await self.browser.screenshot(path, full_page=True)
                screenshots.append(shot)
                
        except Exception as e:
            errors.append(str(e))

        # Stop recording and get video/GIF
        recordings, gifs = await self._stop_recording_if_enabled(project.name, "opensearch_capture")

        return self._create_package(project.name, "opensearch_capture", "opensearch", screenshots, errors,
                                     recordings=recordings, gifs=gifs)

    async def capture_springboot_admin(self, project: ProjectConfig) -> EvidencePackage:
        """Capture SpringBoot Admin health status screenshots with video recording."""
        url = project.tool_urls.springboot_admin
        if not url:
            return self._empty_package(project.name, "springboot_admin", "No SBA URL configured")
            
        screenshots = []
        errors = []

        # Start recording
        await self._start_recording_if_enabled(f"{project.name}_sba")

        try:
            await self.browser.navigate(url)
            await asyncio.sleep(2)
            await self.handle_sso(project.auth)
            
            for check in project.springboot_admin_checks:
                # Find the service card
                selector = f"#service-{check.service_name}"
                try:
                    await self.browser.wait_for(selector, timeout=5000)
                    label = check.screenshot_label or f"sba_{check.service_name}"
                    path = os.path.join(self.output_dir, f"{project.name}_{label}.png")
                    shot = await self.browser.screenshot(path)
                    screenshots.append(shot)
                except Exception as e:
                    errors.append(f"Failed to capture SBA for {check.service_name}: {e}")
                    
        except Exception as e:
            errors.append(str(e))

        # Stop recording and get video/GIF
        recordings, gifs = await self._stop_recording_if_enabled(project.name, "sba_capture")

        return self._create_package(project.name, "sba_capture", "springboot-admin", screenshots, errors,
                                     recordings=recordings, gifs=gifs)

    async def capture_grafana(self, project: ProjectConfig) -> EvidencePackage:
        """Capture Grafana dashboard screenshots with video recording."""
        url = project.tool_urls.grafana
        if not url:
            return self._empty_package(project.name, "grafana", "No Grafana URL configured")
            
        screenshots = []
        errors = []

        # Start recording
        await self._start_recording_if_enabled(f"{project.name}_grafana")

        try:
            for check in project.grafana_checks:
                dashboard_url = f"{url}/d/{check.dashboard_id}"
                await self.browser.navigate(dashboard_url)
                await asyncio.sleep(2)
                await self.handle_sso(project.auth)
                
                # Wait for panels to load
                await asyncio.sleep(3)
                label = check.screenshot_label or f"grafana_{check.dashboard_id}"
                path = os.path.join(self.output_dir, f"{project.name}_{label}.png")
                shot = await self.browser.screenshot(path, full_page=True)
                screenshots.append(shot)
                
        except Exception as e:
            errors.append(str(e))

        # Stop recording and get video/GIF
        recordings, gifs = await self._stop_recording_if_enabled(project.name, "grafana_capture")

        return self._create_package(project.name, "grafana_capture", "grafana", screenshots, errors,
                                     recordings=recordings, gifs=gifs)

    def _create_package(self, project_name: str, flow_name: str, source_tool: str,
                        screenshots: List[Screenshot], errors: List[str],
                        recordings: List[Recording] = None,
                        gifs: List[Recording] = None) -> EvidencePackage:
        pkg = EvidencePackage(
            project_name=project_name,
            flow_name=flow_name,
            source_tool=source_tool,
            screenshots=screenshots,
            recordings=recordings or [],
            gifs=gifs or [],
            passed=len(errors) == 0,
            errors=errors,
            metadata={"timestamp": datetime.utcnow().isoformat() + "Z"}
        )
        
        # Write metadata JSON
        meta_path = os.path.join(self.output_dir, f"{project_name}_{flow_name}_{source_tool}_package.json")
        with open(meta_path, "w") as f:
            data = {
                "project": pkg.project_name,
                "flow": pkg.flow_name,
                "tool": pkg.source_tool,
                "passed": pkg.passed,
                "errors": pkg.errors,
                "screenshots": [s.__dict__ for s in pkg.screenshots],
                "recordings": [r.__dict__ for r in pkg.recordings],
                "gifs": [g.__dict__ for g in pkg.gifs]
            }
            json.dump(data, f, indent=2)
            
        return pkg

    def _empty_package(self, project_name: str, flow_name: str, msg: str) -> EvidencePackage:
        return self._create_package(project_name, flow_name, "unknown", [], [msg])

    async def generate_comparison_report(self, project_name: str, flow_name: str) -> str:
        """Generate side-by-side HTML report comparing baseline to current screenshots."""
        current_files = [f for f in os.listdir(self.output_dir) if f.startswith(f"{project_name}_{flow_name}") and f.endswith(".png")]
        
        html_content = f"""
        <html><head><title>Upgrade Comparison: {project_name} {flow_name}</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; }}
            .comparison-row {{ display: flex; margin-bottom: 30px; border-bottom: 1px solid #ccc; padding-bottom: 20px; }}
            .comparison-block {{ flex: 1; padding: 10px; }}
            img {{ max-width: 100%; border: 1px solid #eee; }}
        </style>
        </head><body>
        <h2>Upgrade Comparison Report: {project_name} - {flow_name}</h2>
        """
        
        for file in current_files:
            baseline_path = os.path.join(self.baseline_dir, file)
            current_path = os.path.join(self.output_dir, file)
            
            baseline_img = f"<img src='baseline/{file}'>" if os.path.exists(baseline_path) else "<i>No baseline found</i>"
            current_img = f"<img src='{file}'>"
            
            html_content += f"""
            <h3>{file}</h3>
            <div class="comparison-row">
                <div class="comparison-block"><h4>Baseline</h4>{baseline_img}</div>
                <div class="comparison-block"><h4>Post-Upgrade</h4>{current_img}</div>
            </div>
            """
            
        html_content += "</body></html>"
        report_path = os.path.join(self.output_dir, f"{project_name}_{flow_name}_comparison.html")
        with open(report_path, "w") as f:
            f.write(html_content)
        return report_path

    async def run_newman_collection(self, project: ProjectConfig) -> EvidencePackage:
        """Run Postman collection using newman CLI and capture report."""
        if not project.postman or not project.postman.collection:
            return self._empty_package(project.name, "api_tests", "No Postman configuration")

        print(f"Running Postman collection for {project.name}")
        report_file = os.path.join(self.output_dir, f"{project.name}_api_report.html")

        cmd = ["newman", "run", project.postman.collection, "-r", "cli,htmlextra", "--reporter-htmlextra-export", report_file]
        if project.postman.environment:
            cmd.extend(["-e", project.postman.environment])

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        errors = []
        if process.returncode != 0:
            errors.append(f"Newman execution failed. Output: {stdout.decode()} Error: {stderr.decode()}")

        pkg = self._create_package(project.name, "api_tests", "postman", [], errors)
        pkg.metadata["report_path"] = report_file
        return pkg

    def generate_summary_report(self, packages: List[EvidencePackage], output_path: Optional[str] = None) -> str:
        """Generate an HTML summary report aggregating all evidence packages.

        Args:
            packages: List of EvidencePackage objects to summarize
            output_path: Optional path for the output file. Defaults to evidence/evidence_summary.html

        Returns:
            Path to the generated HTML report
        """
        if output_path is None:
            output_path = os.path.join(self.output_dir, "evidence_summary.html")

        timestamp = datetime.utcnow().isoformat() + "Z"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Work Buddy - Testing Evidence Summary</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .stat {{ padding: 15px 25px; background: #f5f5f5; border-radius: 4px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .stat-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .package {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 4px; }}
        .passed {{ background: #e8f5e9; border-left: 4px solid #4CAF50; }}
        .failed {{ background: #ffebee; border-left: 4px solid #f44336; }}
        .meta {{ color: #666; font-size: 14px; }}
        .screenshots {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px; }}
        .screenshot {{ border: 1px solid #eee; padding: 5px; }}
        .screenshot img {{ max-width: 400px; height: auto; cursor: pointer; }}
        .screenshot img:hover {{ opacity: 0.8; }}
        .timestamp {{ color: #888; font-size: 12px; }}
        .error-list {{ background: #fff3e0; padding: 10px; border-radius: 4px; margin-top: 10px; }}
        .error-list li {{ color: #e65100; }}
        .gif-preview {{ margin-top: 10px; }}
        .gif-preview img {{ max-width: 300px; border: 1px solid #eee; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Work Buddy - Testing Evidence Summary</h1>
        <p class="timestamp">Generated: {timestamp}</p>

        <div class="summary">
            <div class="stat">
                <div class="stat-value">{len(packages)}</div>
                <div class="stat-label">Total Flows</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #4CAF50;">{sum(1 for p in packages if p.passed)}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #f44336;">{sum(1 for p in packages if not p.passed)}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat">
                <div class="stat-value">{sum(len(p.screenshots) for p in packages)}</div>
                <div class="stat-label">Screenshots</div>
            </div>
        </div>
"""

        for pkg in packages:
            status_class = "passed" if pkg.passed else "failed"
            status_emoji = "✅" if pkg.passed else "❌"

            html += f"""
        <div class="package {status_class}">
            <h3>{status_emoji} {pkg.project_name} - {pkg.flow_name}</h3>
            <p class="meta">
                <strong>Source Tool:</strong> {pkg.source_tool} |
                <strong>Screenshots:</strong> {len(pkg.screenshots)} |
                <strong>Recordings:</strong> {len(pkg.recordings)} |
                <strong>GIFs:</strong> {len(pkg.gifs)}
            </p>
"""

            if pkg.errors:
                html += f"""
            <div class="error-list">
                <strong>Errors:</strong>
                <ul>
                    {"".join(f"<li>{e}</li>" for e in pkg.errors)}
                </ul>
            </div>
"""

            if pkg.screenshots:
                html += """
            <div class="screenshots">
"""
                for shot in pkg.screenshots:
                    filename = os.path.basename(shot.path)
                    html += f"""
                <div class="screenshot">
                    <p><strong>{shot.label}</strong></p>
                    <a href="{filename}" target="_blank">
                        <img src="{filename}" alt="{shot.label}" title="Click to view full size">
                    </a>
                </div>
"""
                html += """
            </div>
"""

            if pkg.gifs:
                html += """
            <div class="gif-preview">
                <p><strong>Animated Preview:</strong></p>
"""
                for gif in pkg.gifs:
                    gif_filename = os.path.basename(gif.path)
                    html += f"""
                <img src="../gifs/{gif_filename}" alt="Test Flow Animation">
"""
                html += """
            </div>
"""

            html += """
        </div>
"""

        html += """
    </div>
</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html)

        return output_path
