from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from db.auth import get_db
from core.security import require_admin, get_current_user
from api.models.allocations import Allocation
from api.models.assets import Asset
from api.models.assets_histories import AssetHistory
from api.utils.enums import AssetStatus
from api.schemas.allocation_schemas import AllocationCreate, AllocationOut
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

router = APIRouter(prefix="/allocations", tags=["Allocations"])

# -------- Create Allocation (Admin)
@router.post("", response_model=AllocationOut, dependencies=[Depends(require_admin)])
def allocate_asset(payload: AllocationCreate, db: Session = Depends(get_db), admin=Depends(get_current_user)):

    asset = db.query(Asset).filter(Asset.id == payload.asset_id, Asset.deleted_at.is_(None)).first()
    if not asset:
        raise HTTPException(404, "Asset not found")

    if asset.status != AssetStatus.available:
        raise HTTPException(409, "Asset is not available")

    alloc = Allocation(
        asset_id=payload.asset_id,
        employee_id=payload.employee_id,
        allocation_date=payload.allocation_date,
        allocated_by=admin.id,
        notes=payload.notes
    )
    db.add(alloc)

    # Update asset to allocated
    old = asset.status
    asset.status = AssetStatus.assigned

    event_metadata_payload = {
        "employee_id": str(payload.employee_id)  # Convert UUID to string
    }

    db.add(AssetHistory(
        asset_id=asset.id,
        user_id=admin.id,
        from_status=old,
        to_status=AssetStatus.assigned,
        event_metadata=event_metadata_payload
    ))

    db.commit()
    db.refresh(alloc)
    return alloc


# -------- Current employee allocations
@router.get("/current", response_model=list[AllocationOut])
def current_allocations(employee_id: str, db: Session = Depends(get_db)):
    return (
        db.query(Allocation)
        .filter(
            Allocation.employee_id == employee_id,
            Allocation.returned_at.is_(None),
            Allocation.deleted_at.is_(None)
        )
        .order_by(Allocation.allocation_date.desc())
        .all()
    )
