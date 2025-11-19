from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.auth import get_db
from core.security import require_admin
from api.models.categories import Category
from api.schemas.asset_schemas import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(prefix="/categories", tags=["Asset Categories"])

@router.post("", response_model=CategoryOut, dependencies=[Depends(require_admin)])
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    exists = db.query(Category).filter(Category.name == payload.name, Category.deleted_at.is_(None)).first()
    if exists:
        raise HTTPException(status_code=409, detail="Category already exists")

    cat = Category(**payload.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("", response_model=list[CategoryOut], dependencies=[Depends(require_admin)])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.deleted_at.is_(None)).order_by(Category.id.desc()).all()

@router.put("/{id}", response_model=CategoryOut, dependencies=[Depends(require_admin)])
def update_category(id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == id, Category.deleted_at.is_(None)).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    if payload.name:
        dupe = db.query(Category).filter(Category.name == payload.name, Category.deleted_at.is_(None)).first()
        if dupe and dupe.id != id:
            raise HTTPException(status_code=409, detail="Category name already exists")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)

    db.commit()
    db.refresh(cat)
    return cat
