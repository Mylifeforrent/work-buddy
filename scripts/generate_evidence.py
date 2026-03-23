#!/usr/bin/env python3
"""Generate testing evidence for Work Buddy agents.

This script demonstrates the browser automation capabilities and generates
actual evidence files (screenshots, metadata JSON) for verification.

Usage:
    python3 scripts/generate_evidence.py

Requirements:
    - Playwright installed (pip install playwright && playwright install chromium)
    - No need for mock services - uses simple static pages
"""

import asyncio
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from work_buddy.agents.browser_test_agent import BrowserTestAgent
from work_buddy.core.config import (
    ProjectConfig, TestFlow, TestStep, AuthConfig,
    ToolUrls, EvidenceCheck, SpringBootAdminCheck, GrafanaCheck
)
from work_buddy.adapters.real.real_browser import RealBrowserAdapter


async def generate_evidence():
    """Generate testing evidence using real browser automation."""
    output_dir = "evidence"
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Work Buddy - Testing Evidence Generator")
    print("=" * 60)
    print(f"\nOutput directory: {output_dir}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Initialize browser
    print("1. Launching browser...")
    browser = RealBrowserAdapter()
    await browser.launch(headless=True)
    print("   ✓ Browser launched (Chromium headless)")

    try:
        agent = BrowserTestAgent(browser=browser, output_dir=output_dir, enable_recording=True)

        # Test 1: Navigate to example.com and take screenshots
        print("\n2. Running Test Flow 1: Simple Navigation Test")
        project1 = ProjectConfig(
            name="example-site",
            type="react-app",
            base_url="https://example.com",
            auth=AuthConfig(type="none"),
            test_flows=[
                TestFlow(
                    name="homepage_check",
                    steps=[
                        TestStep(action="navigate", target="https://example.com"),
                        TestStep(action="wait_for", target="h1", label="wait_heading"),
                        TestStep(action="screenshot", label="homepage"),
                        TestStep(action="assert_text", target="h1", value="Example Domain"),
                    ]
                )
            ]
        )

        pkg1 = await agent.execute_react_flow(project1, project1.test_flows[0])
        print(f"   Flow: {pkg1.flow_name}")
        print(f"   Passed: {pkg1.passed}")
        print(f"   Screenshots: {len(pkg1.screenshots)}")
        if pkg1.errors:
            print(f"   Errors: {pkg1.errors}")

        # Test 2: HTTPBin forms test
        print("\n3. Running Test Flow 2: Form Interaction Test")
        project2 = ProjectConfig(
            name="httpbin-test",
            type="react-app",
            base_url="https://httpbin.org",
            auth=AuthConfig(type="none"),
            test_flows=[
                TestFlow(
                    name="forms_test",
                    steps=[
                        TestStep(action="navigate", target="https://httpbin.org/forms/post"),
                        TestStep(action="screenshot", label="form_initial"),
                        TestStep(action="type", target="input[name='custname']", value="Test User"),
                        TestStep(action="type", target="input[name='custtel']", value="123-456-7890"),
                        TestStep(action="type", target="input[name='custemail']", value="test@example.com"),
                        TestStep(action="screenshot", label="form_filled"),
                        TestStep(action="click", target="button[type='submit']"),
                        TestStep(action="wait_for", target="body"),
                        TestStep(action="screenshot", label="form_submitted"),
                    ]
                )
            ]
        )

        pkg2 = await agent.execute_react_flow(project2, project2.test_flows[0])
        print(f"   Flow: {pkg2.flow_name}")
        print(f"   Passed: {pkg2.passed}")
        print(f"   Screenshots: {len(pkg2.screenshots)}")
        if pkg2.errors:
            print(f"   Errors: {pkg2.errors}")

        # Generate summary report
        print("\n4. Generating Evidence Summary Report")
        report_path = os.path.join(output_dir, "evidence_summary.html")
        generate_summary_report(report_path, [pkg1, pkg2])
        print(f"   ✓ Report saved: {report_path}")

    finally:
        await browser.close()
        print("\n5. Browser closed")

    # List generated evidence
    print("\n" + "=" * 60)
    print("Generated Evidence Files:")
    print("=" * 60)

    for root, dirs, files in os.walk(output_dir):
        for f in files:
            filepath = os.path.join(root, f)
            size = os.path.getsize(filepath)
            print(f"   {f:50s} {size:>10,} bytes")

    print("\n✓ Evidence generation complete!")
    return True


def generate_summary_report(report_path: str, packages):
    """Generate an HTML summary report of all evidence packages."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Work Buddy - Testing Evidence Summary</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .package {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 4px; }}
        .passed {{ background: #e8f5e9; border-left: 4px solid #4CAF50; }}
        .failed {{ background: #ffebee; border-left: 4px solid #f44336; }}
        .meta {{ color: #666; font-size: 14px; }}
        .screenshots {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px; }}
        .screenshot {{ border: 1px solid #eee; padding: 5px; }}
        .screenshot img {{ max-width: 400px; height: auto; }}
        .timestamp {{ color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Work Buddy - Testing Evidence Summary</h1>
        <p class="timestamp">Generated: {datetime.now().isoformat()}</p>
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
                <strong>Recordings:</strong> {len(pkg.recordings)}
            </p>
"""

        if pkg.errors:
            html += f"""
            <p><strong>Errors:</strong></p>
            <ul>
                {"".join(f"<li>{e}</li>" for e in pkg.errors)}
            </ul>
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
                    <img src="{filename}" alt="{shot.label}">
                </div>
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

    with open(report_path, 'w') as f:
        f.write(html)


if __name__ == "__main__":
    success = asyncio.run(generate_evidence())
    sys.exit(0 if success else 1)