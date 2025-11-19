from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session , joinedload
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
from api.models.users import User


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

    # Update asset status
    old = asset.status
    asset.status = AssetStatus.assigned

    db.add(AssetHistory(
        asset_id=asset.id,
        user_id=admin.id,
        from_status=old,
        to_status=AssetStatus.assigned,
        event_metadata={"employee_id": str(payload.employee_id)}
    ))

    db.commit()
    db.refresh(alloc)

    # Set output fields
    employee = db.query(User).filter(User.id == payload.employee_id).first()

    alloc.asset_name = asset.name
    alloc.employee_name = employee.full_name if employee else None
    alloc.allocated_by_name = admin.full_name

    return alloc


@router.get("", response_model=list[AllocationOut], dependencies=[Depends(require_admin)])
def list_all_allocations(db: Session = Depends(get_db)):
    allocations = (
        db.query(Allocation)
        .options(
            joinedload(Allocation.asset),
            joinedload(Allocation.employee),
            joinedload(Allocation.allocator)
        )
        .filter(Allocation.deleted_at.is_(None))
        .order_by(Allocation.allocation_date.desc())
        .all()
    )

    # Inject readable names
    for alloc in allocations:
        alloc.asset_name = alloc.asset.name if alloc.asset else None
        alloc.employee_name = alloc.employee.full_name if alloc.employee else None
        alloc.allocated_by_name = alloc.allocator.full_name if alloc.allocator else None

    return allocations


# -------- Current employee allocations
@router.get("/my", response_model=list[AllocationOut])
def get_my_allocations(
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allocations = (
        db.query(Allocation)
        .options(
            joinedload(Allocation.asset),
            joinedload(Allocation.employee),
            joinedload(Allocation.allocator)
        )
        .filter(
            Allocation.employee_id == user.id,
            Allocation.deleted_at.is_(None)
        )
        .order_by(Allocation.allocation_date.desc())
        .all()
    )

    for alloc in allocations:
        alloc.asset_name = alloc.asset.name if alloc.asset else None
        alloc.employee_name = alloc.employee.full_name if alloc.employee else None
        alloc.allocated_by_name = alloc.allocator.full_name if alloc.allocator else None

    return allocations
