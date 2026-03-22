from typing import Dict, Any
from work_buddy.services.grafana_service import GrafanaService

class RealGrafanaAdapter(GrafanaService):
    """Real implementation of GrafanaService."""
    
    async def get_dashboard(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("TODO")

    async def get_metrics(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("TODO")
