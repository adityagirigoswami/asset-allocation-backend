from enum import Enum

class AssetStatus(str, Enum):
    available = "available"
    assigned = "assigned"
    under_repair = "under_repair"
    damaged = "damaged"
