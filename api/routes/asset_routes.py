from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from db.auth import get_db
from core.security import require_admin, get_current_user
from api.models.assets import Asset
from api.models.return_requests import ReturnRequest
from api.models.assets_histories import AssetHistory
from api.schemas.allocation_schemas import AllocationCreate, AllocationOut
from api.models.allocations import Allocation
from api.schemas.asset_dashboard_schemas import AssetDashboardSummary
from uuid import UUID
from api.schemas.asset_schemas import (
    AssetCreate, AssetUpdate, AssetOut, AssetStatusUpdate, AssetHistoryOut
)
from api.utils.enums import AssetStatus
from sqlalchemy.orm import selectinload


router = APIRouter(prefix="/assets", tags=["Assets"])
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
# -------- Create Asset (Admin)
@router.post("", response_model=AssetOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_asset(payload: AssetCreate, db: Session = Depends(get_db), admin=Depends(get_current_user)):
    # Prevent creating assets with "assigned" status (only allocation system can assign)
    if payload.status == AssetStatus.assigned:
        raise HTTPException(
            status_code=400,
            detail="Cannot create asset with 'assigned' status. Use the allocation system to assign assets."
        )
    
    if payload.tag_code:
        if db.query(Asset).filter(Asset.tag_code == payload.tag_code, Asset.deleted_at.is_(None)).first():
            raise HTTPException(409, "Tag code already exists")

    if payload.serial_number:
        if db.query(Asset).filter(Asset.serial_number == payload.serial_number, Asset.deleted_at.is_(None)).first():
            raise HTTPException(409, "Serial number already exists")

    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)

    # Log History
    hist = AssetHistory(
        asset_id=asset.id,
        user_id=admin.id,
        from_status=None,
        to_status=asset.status,
        event_metadata={"reason": "creation"}
    )
    db.add(hist)
    db.commit()

    return asset


# -------- List all assets
@router.get("", response_model=list[AssetOut],dependencies=[Depends(require_admin)])
def list_assets(db: Session = Depends(get_db)):
    return (db.query(Asset)
        .options(selectinload(Asset.category))
        .filter(Asset.deleted_at.is_(None))
        .order_by(Asset.updated_at.desc())
        .all())

# -------- Get asset by ID
@router.get("/{id}", response_model=AssetOut)
def get_asset(id: str, db: Session = Depends(get_db)):
    asset = (
        db.query(Asset)
        .options(selectinload(Asset.category))
        .filter(Asset.id == id, Asset.deleted_at.is_(None))
        .first()
        )
    if not asset:
        raise HTTPException(404, "Asset not found")
    return asset


# -------- Update asset (Admin)
@router.put("/{id}", response_model=AssetOut, dependencies=[Depends(require_admin)])
def update_asset(id: str, payload: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == id, Asset.deleted_at.is_(None)).first()
    if not asset:
        raise HTTPException(404, "Asset not found")

    # Validate dates if both are being updated
    if payload.purchase_date is not None and payload.warranty_expiry is not None:
        if payload.purchase_date > payload.warranty_expiry:
            raise HTTPException(400, "Purchase date cannot be after warranty expiry date")
    # If only one is being updated, check against existing value
    elif payload.purchase_date is not None and asset.warranty_expiry:
        if payload.purchase_date > asset.warranty_expiry:
            raise HTTPException(400, "Purchase date cannot be after warranty expiry date")
    elif payload.warranty_expiry is not None and asset.purchase_date:
        if asset.purchase_date > payload.warranty_expiry:
            raise HTTPException(400, "Purchase date cannot be after warranty expiry date")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(asset, k, v)
    
    # Update updated_at manually to ensure it's refreshed
    asset.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(asset)
    return asset


# -------- Soft delete
@router.delete("/{id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_asset(id: str, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == id, Asset.deleted_at.is_(None)).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    
    if asset.status == AssetStatus.assigned:
        # 400 Bad Request if the asset is currently assigned/allocated
        raise HTTPException(
            status_code=400,
            detail="Asset is currently assigned and cannot be deleted until it is unallocated."
        )

    asset.deleted_at = datetime.now(timezone.utc)
    db.commit()


# -------- Get asset history
@router.get("/{id}/history", response_model=list[AssetHistoryOut])
def get_asset_history(id: UUID , db: Session = Depends(get_db)):
    return (
        db.query(AssetHistory)
        .filter(AssetHistory.asset_id == id, AssetHistory.deleted_at.is_(None))
        .order_by(AssetHistory.id.desc())
        .all()
    )


# -------- Update status (Admin)
@router.put("/{id}/status", response_model=AssetOut, dependencies=[Depends(require_admin)])
def update_asset_status(
    id: UUID,
    payload: AssetStatusUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user)
):
    asset = db.query(Asset).filter(Asset.id == id, Asset.deleted_at.is_(None)).first()
    if not asset:
        raise HTTPException(404, "Asset not found")

    old_status = asset.status
    
    # Prevent changing FROM "assigned" status (must be returned via allocation system)
    if old_status == AssetStatus.assigned:
        raise HTTPException(
            status_code=400,
            detail="Cannot change status of an assigned asset. Please return the asset through the allocation system first."
        )
    
    # Prevent changing TO "assigned" status (only allocation system can assign)
    if payload.status == AssetStatus.assigned:
        raise HTTPException(
            status_code=400,
            detail="Cannot manually set asset status to 'assigned'. Use the allocation system to assign assets."
        )
    
    # Only allow transitions between: available, under_repair, and damaged
    allowed_statuses = {AssetStatus.available, AssetStatus.under_repair, AssetStatus.damaged}
    if payload.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status can only be changed between: available, under_repair, and damaged. Cannot set to '{payload.status.value}'"
        )
    
    asset.status = payload.status
    # Update updated_at to ensure sorting works correctly
    asset.updated_at = datetime.now(timezone.utc)

    hist = AssetHistory(
        asset_id=asset.id,
        user_id=admin.id,
        from_status=old_status,
        to_status=payload.status,
        event_metadata=payload.event_metadata or {}
    )
    db.add(hist)
    db.commit()
    db.refresh(asset)

    return asset


@router.get("/{asset_id}/allocations", response_model=list[AllocationOut])
def asset_allocations(asset_id: UUID, db: Session = Depends(get_db)):
    # Note: Changed asset_id type hint to UUID for consistency with UUID usage
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.deleted_at.is_(None)).first()
    
    if not asset:
        # Error for a non-existent asset ID
        raise HTTPException(
            status_code=404, 
            detail="No asset found with this ID."
        )
    
    allocations = (
        db.query(Allocation)
        .filter(Allocation.asset_id == asset_id, Allocation.deleted_at.is_(None))
        .order_by(Allocation.allocation_date.desc())
        .all()
    )

    if not allocations:
        # Check if the list of allocations is empty
        raise HTTPException(
            status_code=404, 
            detail=f"No active allocations found for asset ID: {asset_id}"
        )

    return allocations


@dashboard_router.get("", response_model=AssetDashboardSummary, dependencies=[Depends(require_admin)])
def asset_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns count of all asset statuses for admin dashboard.
    """

    total = db.query(Asset).filter(Asset.deleted_at.is_(None)).count()
    pending_requests = db.query(ReturnRequest).filter(ReturnRequest.approved_at.is_(None), ReturnRequest.deleted_at.is_(None)).count()

    available = db.query(Asset).filter(
        Asset.status == AssetStatus.available,
        Asset.deleted_at.is_(None)
    ).count()

    assigned = db.query(Asset).filter(
        Asset.status == AssetStatus.assigned,
        Asset.deleted_at.is_(None)
    ).count()

    under_repair = db.query(Asset).filter(
        Asset.status == AssetStatus.under_repair,
        Asset.deleted_at.is_(None)
    ).count()

    damaged = db.query(Asset).filter(
        Asset.status == AssetStatus.damaged,
        Asset.deleted_at.is_(None)
    ).count()

    return AssetDashboardSummary(
        total_assets=total,
        available=available,
        assigned=assigned,
        under_repair=under_repair,
        damaged=damaged,
        pending_requests = pending_requests
    )
