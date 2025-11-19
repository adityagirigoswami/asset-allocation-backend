from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from api.routes.admin_routes import employees_router
from db.auth import get_db
from core.security import require_admin, get_current_user
from api.models.return_requests import ReturnRequest
from api.models.allocations import Allocation
from api.models.assets import Asset
from api.models.assets_histories import AssetHistory
from api.utils.enums import AssetStatus
from datetime import datetime, timezone
from datetime import timezone
from api.schemas.return_request_schemas import (
    ReturnRequestCreate, ReturnRequestOut, ReturnRequestApprove
)

router = APIRouter(prefix="/requests", tags=["Return Requests"])
employees_router = APIRouter(prefix="/employees/me", tags=["employees"])

def add_return_request_names(req, db):
    """
    Inject asset_name and employee_name into return request response.
    """
    alloc = db.query(Allocation).options(
        joinedload(Allocation.asset),
        joinedload(Allocation.employee)
    ).filter(Allocation.id == req.allocation_id).first()

    req.asset_name = alloc.asset.name if alloc and alloc.asset else None
    req.employee_name = alloc.employee.full_name if alloc and alloc.employee else None

    return req

# -------- Create return request (Employee)
@router.post("", response_model=ReturnRequestOut)
def create_return_request(payload: ReturnRequestCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    alloc = db.query(Allocation).filter(
        Allocation.id == payload.allocation_id, 
        Allocation.deleted_at.is_(None)
    ).first()

    if not alloc:
        raise HTTPException(404, "Allocation not found")

    if alloc.employee_id != user.id:
        raise HTTPException(403, "You can't request return of another user's allocation")

    if alloc.returned_at:
        raise HTTPException(409, "Already returned")

    req = ReturnRequest(
        allocation_id=payload.allocation_id,
        requested_by=user.id,
        description=payload.description
    )

    db.add(req)
    db.commit()
    db.refresh(req)

    return add_return_request_names(req, db)


@employees_router.get("/requests", response_model=list[ReturnRequestOut])
def my_requests(db: Session = Depends(get_db), user=Depends(get_current_user)):
    requests = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.requested_by == user.id, ReturnRequest.deleted_at.is_(None))
        .order_by(ReturnRequest.created_at.desc())
        .all()
    )

    return [add_return_request_names(req, db) for req in requests]



# -------- List pending approvals (Admin)
@router.get("/pending", response_model=list[ReturnRequestOut], dependencies=[Depends(require_admin)])
def pending_requests(db: Session = Depends(get_db)):
    requests = (
        db.query(ReturnRequest)
        .filter(ReturnRequest.approved_at.is_(None), ReturnRequest.deleted_at.is_(None))
        .order_by(ReturnRequest.created_at.asc())
        .all()
    )

    return [add_return_request_names(req, db) for req in requests]



# -------- Approve return request (Admin)
@router.post("/{id}/approve", response_model=ReturnRequestOut, dependencies=[Depends(require_admin)])
def approve_return(id: str, payload: ReturnRequestApprove, db: Session = Depends(get_db), admin=Depends(get_current_user)):

    req = db.query(ReturnRequest).filter(ReturnRequest.id == id, ReturnRequest.deleted_at.is_(None)).first()
    if not req:
        raise HTTPException(404, "Return request not found")

    if req.approved_at:
        raise HTTPException(409, "Already approved")

    alloc = db.query(Allocation).filter(Allocation.id == req.allocation_id).first()
    if alloc.returned_at:
        raise HTTPException(409, "Already returned")

    asset = db.query(Asset).filter(Asset.id == alloc.asset_id).first()

    # FIX 1: Use datetime.now(timezone.utc) to set returned_at
    alloc.returned_at = datetime.now(timezone.utc)
    old = asset.status
    asset.status = AssetStatus.available

    db.add(AssetHistory(
        asset_id=asset.id,
        user_id=admin.id,
        from_status=old,
        to_status=AssetStatus.available,
        event_metadata={"reason": "return_approved", "alloc": str(alloc.id)}
    ))

    # FIX 2: Use datetime.now(timezone.utc) to set approved_at
    req.approved_at = datetime.now(timezone.utc)
    req.decision_note = payload.decision_note

    db.commit()
    db.refresh(req)

    return add_return_request_names(req, db)