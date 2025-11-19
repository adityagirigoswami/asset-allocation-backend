from pydantic import BaseModel

class AssetDashboardSummary(BaseModel):
    total_assets: int
    available: int
    assigned: int
    under_repair: int
    damaged: int
    pending_requests: int
