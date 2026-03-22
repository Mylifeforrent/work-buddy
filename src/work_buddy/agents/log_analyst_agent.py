import os
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from work_buddy.agents.browser_test_agent import BrowserTestAgent
from work_buddy.services.opensearch_service import OpenSearchService
from work_buddy.services.grafana_service import GrafanaService
from work_buddy.core.config import load_app_config, ProjectConfig

class LogAnalystAgent:
    """Agent for automated alert triage and PVT (Post Verification Testing) health checks."""
    
    def __init__(self, browser_agent: BrowserTestAgent, opensearch: OpenSearchService, grafana: GrafanaService):
        self.browser_agent = browser_agent
        self.opensearch = opensearch
        self.grafana = grafana
        self.app_config = load_app_config()
        self.llm = ChatOpenAI(model=self.app_config.llm_model, temperature=0.1)

    async def run_pvt_healthcheck(self, project: ProjectConfig) -> str:
        """Execute PVT and generate an HTML report."""
        print(f"Running PVT for {project.name}")
        
        # 1. Capture OpenSearch evidence via UI
        os_pkg = await self.browser_agent.capture_opensearch(project)
        
        # 2. Capture SBA evidence via UI
        sba_pkg = await self.browser_agent.capture_springboot_admin(project)
        
        # 3. Extract pure text logs via API
        logs = await self.opensearch.get_log_entries(project.name, limit=20)
        
        return self._generate_pvt_report(project, os_pkg, sba_pkg, logs)

    def _generate_pvt_report(self, project: ProjectConfig, os_pkg, sba_pkg, logs: List[Dict]) -> str:
        out_dir = self.browser_agent.output_dir
        html = f"<html><head><title>PVT Report: {project.name}</title></head><body>"
        html += f"<h2>Post Verification Testing: {project.name}</h2>"
        
        html += "<h3>Spring Boot Admin</h3>"
        for shot in sba_pkg.screenshots:
            html += f"<p><img src='{os.path.basename(shot.path)}' width='800'></p>"
            
        html += "<h3>OpenSearch Keywords</h3>"
        for shot in os_pkg.screenshots:
            html += f"<p><img src='{os.path.basename(shot.path)}' width='800'></p>"
            
        html += "<h3>Recent Logs Sample</h3><ul>"
        for log in logs:
            html += f"<li>{log.get('timestamp', '')} [{log.get('level', 'INFO')}] {log.get('message', '')}</li>"
        html += "</ul></body></html>"
        
        report_path = os.path.join(out_dir, f"{project.name}_pvt_report.html")
        with open(report_path, "w") as f:
            f.write(html)
        return report_path

    async def triage_alert(self, project: ProjectConfig, alert_details: str) -> str:
        """Triage an alert using OpenSearch logs and Grafana metrics via LLM."""
        
        # Fetch relevant context
        logs = await self.opensearch.get_log_entries(project.name, limit=50)
        
        # If Grafana dashboard check defined, get metrics
        metrics = {}
        if project.grafana_checks:
            dash_id = project.grafana_checks[0].dashboard_id
            metrics = await self.grafana.get_dashboard(dash_id)
            
        log_text = "\\n".join([f"{l.get('level', 'INFO')}: {l.get('message', '')}" for l in logs])
        
        prompt = f"""
        You are an SRE alert triage assistant.
        Analyze the following alert along with recent logs and metrics data.
        
        Alert: {alert_details}
        
        Recent Logs:
        {log_text[:2000]} # truncate for context
        
        Metrics Dashboard Status:
        {metrics}
        
        Provide a triage recommendation. Start with exactly one of these labels:
        [IGNORE], [NEEDS ATTENTION], or [CRITICAL].
        Then provide a brief justification.
        """
        
        response = await self.llm.ainvoke([SystemMessage(content="You triage alerts."), HumanMessage(content=prompt)])
        rec = str(response.content)
        
        # Generate Triage Report
        return self._generate_triage_report(project, alert_details, rec)

    def _generate_triage_report(self, project: ProjectConfig, alert: str, recommendation: str) -> str:
        out_dir = self.browser_agent.output_dir
        html = f"<html><head><title>Triage: {project.name}</title></head><body>"
        html += f"<h2>Alert Triage Report: {project.name}</h2>"
        html += f"<h3>Alert Trigger</h3><pre>{alert}</pre>"
        
        color = "black"
        if "[CRITICAL]" in recommendation: color = "red"
        elif "[NEEDS ATTENTION]" in recommendation: color = "orange"
        elif "[IGNORE]" in recommendation: color = "green"
        
        html += f"<h3>LLM Recommendation</h3><div style='color: {color}; border: 1px solid #ccc; padding: 10px;'>{recommendation}</div>"
        html += "</body></html>"
        
        report_path = os.path.join(out_dir, f"{project.name}_triage_report.html")
        with open(report_path, "w") as f:
            f.write(html)
        return report_path
