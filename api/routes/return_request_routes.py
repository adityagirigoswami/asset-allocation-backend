from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from db.auth import get_db
from core.security import require_admin, get_current_user
from api.models.return_requests import ReturnRequest
from api.models.allocations import Allocation
from api.models.assets import Asset
from api.models.assets_histories import AssetHistory
from api.utils.enums import AssetStatus
from api.schemas.return_request_schemas import (
    ReturnRequestCreate, ReturnRequestOut, ReturnRequestApprove
)

router = APIRouter(prefix="/return-requests", tags=["Return Requests"])

# -------- Create return request (Employee)
@router.post("", response_model=ReturnRequestOut)
def create_return_request(payload: ReturnRequestCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):

    alloc = db.query(Allocation).filter(Allocation.id == payload.allocation_id, Allocation.deleted_at.is_(None)).first()
    if not alloc:
        raise HTTPException(404, "Allocation not found")

    if alloc.employee_id != user.id:
        raise HTTPException(403, "You can't request return of another user's allocation")

    if alloc.returned_at is not None:
        raise HTTPException(409, "Already returned")

    req = ReturnRequest(
        allocation_id=payload.allocation_id,
        requested_by=user.id,
        description=payload.description
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


# -------- List my return requests
@router.get("/my", response_model=list[ReturnRequestOut])
def my_requests(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (
        db.query(ReturnRequest)
        .filter(ReturnRequest.requested_by == user.id, ReturnRequest.deleted_at.is_(None))
        .order_by(ReturnRequest.created_at.desc())
        .all()
    )


# -------- List pending approvals (Admin)
@router.get("/pending", response_model=list[ReturnRequestOut], dependencies=[Depends(require_admin)])
def pending_requests(db: Session = Depends(get_db)):
    return (
        db.query(ReturnRequest)
        .filter(ReturnRequest.approved_at.is_(None), ReturnRequest.deleted_at.is_(None))
        .order_by(ReturnRequest.created_at.asc())
        .all()
    )


# -------- Approve return request (Admin)
@router.post("/{id}/approve", response_model=ReturnRequestOut, dependencies=[Depends(require_admin)])
def approve_return(id: str, payload: ReturnRequestApprove, db: Session = Depends(get_db), admin=Depends(get_current_user)):

    req = db.query(ReturnRequest).filter(ReturnRequest.id == id, ReturnRequest.deleted_at.is_(None)).first()
    if not req:
        raise HTTPException(404, "Return request not found")

    if req.approved_at is not None:
        raise HTTPException(409, "Already approved")

    alloc = db.query(Allocation).filter(Allocation.id == req.allocation_id).first()
    if alloc.returned_at is not None:
        raise HTTPException(409, "Already returned")

    asset = db.query(Asset).filter(Asset.id == alloc.asset_id).first()

    # Mark allocation returned
    alloc.returned_at = datetime.utcnow()

    # Asset back to available
    old = asset.status
    asset.status = AssetStatus.available

    db.add(AssetHistory(
        asset_id=asset.id,
        user_id=admin.id,
        from_status=old,
        to_status=AssetStatus.available,
        event_metadata={"reason": "return_approved", "alloc": str(alloc.id)}
    ))

    req.approved_at = datetime.utcnow()
    req.decision_note = payload.decision_note

    db.commit()
    db.refresh(req)
    return req
