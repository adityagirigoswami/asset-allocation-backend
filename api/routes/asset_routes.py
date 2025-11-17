from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from db.auth import get_db
from core.security import require_admin, get_current_user
from api.models.assets import Asset
from api.models.assets_histories import AssetHistory
from uuid import UUID
from api.utils.enums import AssetStatus
from api.schemas.asset_schemas import (
    AssetCreate, AssetUpdate, AssetOut, AssetStatusUpdate, AssetHistoryOut
)

router = APIRouter(prefix="/assets", tags=["Assets"])

# -------- Create Asset (Admin)
@router.post("", response_model=AssetOut, dependencies=[Depends(require_admin)])
def create_asset(payload: AssetCreate, db: Session = Depends(get_db), admin=Depends(get_current_user)):
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
    return db.query(Asset).filter(Asset.deleted_at.is_(None)).all()

# -------- Get asset by ID
@router.get("/{id}", response_model=AssetOut)
def get_asset(id: str, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == id, Asset.deleted_at.is_(None)).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    return asset


# -------- Update asset (Admin)
@router.put("/{id}", response_model=AssetOut, dependencies=[Depends(require_admin)])
def update_asset(id: str, payload: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == id, Asset.deleted_at.is_(None)).first()
    if not asset:
        raise HTTPException(404, "Asset not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(asset, k, v)

    db.commit()
    db.refresh(asset)
    return asset


# -------- Soft delete
@router.delete("/{id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_asset(id: str, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == id, Asset.deleted_at.is_(None)).first()
    if asset.status == "assigned":
        # 400 Bad Request if the asset is currently assigned/allocated
        raise HTTPException(
            status_code=400,
            detail="Asset is currently assigned and cannot be deleted until it is unallocated."
        )

    if not asset:
        raise HTTPException(404, "Asset not found")

    asset.deleted_at = datetime.utcnow()
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
    asset.status = payload.status

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
