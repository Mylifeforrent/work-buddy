import asyncio
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from work_buddy.services.browser_service import BrowserService, Screenshot, EvidencePackage
from work_buddy.core.config import ProjectConfig, TestFlow, AuthConfig

class BrowserTestAgent:
    """Agent responsible for executing browser UI tests and capturing screenshots."""

    def __init__(self, browser: BrowserService, output_dir: str = "evidence"):
        self.browser = browser
        self.output_dir = output_dir
        self.baseline_dir = os.path.join(output_dir, "baseline")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.baseline_dir, exist_ok=True)

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
        """Execute a UI test flow for a React Web App."""
        print(f"Executing React flow '{flow.name}' for {project.name}")
        screenshots = []
        errors = []
        
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

        return self._create_package(project.name, flow.name, "react-app", screenshots, errors)

    async def capture_opensearch(self, project: ProjectConfig) -> EvidencePackage:
        """Capture OpenSearch logs dashboard screenshots based on configured keywords."""
        url = project.tool_urls.opensearch
        if not url:
            return self._empty_package(project.name, "opensearch", "No OpenSearch URL configured")
            
        screenshots = []
        errors = []
        try:
            await self.browser.navigate(url)
            await asyncio.sleep(2)
            await self.handle_sso(project.auth)
            
            checks = project.evidence_checks.get("opensearch", []) if project.evidence_checks else []
            for check in checks:
                if check.query:
                    # Very simple mock sequence: type in search bar, press enter
                    search_selector = "input[type='text'], input[placeholder*='Search']"
                    await self.browser.wait_for(search_selector, timeout=5000)
                    await self.browser.type_text(search_selector, check.query)
                    # Assuming press enter or there's a submit button
                    # For Playwright, we can just click body or something to unfocus, or simulated Enter
                    # As a stub:
                    await asyncio.sleep(2)
                
                label = check.screenshot_label or check.name
                path = os.path.join(self.output_dir, f"{project.name}_opensearch_{label}.png")
                shot = await self.browser.screenshot(path, full_page=True)
                screenshots.append(shot)
                
        except Exception as e:
            errors.append(str(e))
            
        return self._create_package(project.name, "opensearch_capture", "opensearch", screenshots, errors)

    async def capture_springboot_admin(self, project: ProjectConfig) -> EvidencePackage:
        """Capture SpringBoot Admin health status screenshots."""
        url = project.tool_urls.springboot_admin
        if not url:
            return self._empty_package(project.name, "springboot_admin", "No SBA URL configured")
            
        screenshots = []
        errors = []
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
            
        return self._create_package(project.name, "sba_capture", "springboot-admin", screenshots, errors)

    async def capture_grafana(self, project: ProjectConfig) -> EvidencePackage:
        """Capture Grafana dashboard screenshots."""
        url = project.tool_urls.grafana
        if not url:
            return self._empty_package(project.name, "grafana", "No Grafana URL configured")
            
        screenshots = []
        errors = []
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
            
        return self._create_package(project.name, "grafana_capture", "grafana", screenshots, errors)

    def _create_package(self, project_name: str, flow_name: str, source_tool: str, screenshots: List[Screenshot], errors: List[str]) -> EvidencePackage:
        pkg = EvidencePackage(
            project_name=project_name,
            flow_name=flow_name,
            source_tool=source_tool,
            screenshots=screenshots,
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
                "screenshots": [s.__dict__ for s in pkg.screenshots]
            }
            json.dump(data, f, indent=2)
            
        return pkg

    def _empty_package(self, project_name: str, flow_name: str, msg: str) -> EvidencePackage:
        return self._create_package(project_name, flow_name, "unknown", [], [msg])

    async def generate_comparison_report(self, project_name: str, flow_name: str) -> str:
        """Generate side-by-side HTML report comparing baseline to current screenshots."""
        # Ensure we have screenshots with the prefix project_name_flow_name
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
