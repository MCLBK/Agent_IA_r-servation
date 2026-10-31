from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Traveler, User
from app.schemas import TravelerOut, TravelerCreate
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/travelers", tags=["travelers"])


@router.get("", response_model=list[TravelerOut])
def list_travelers(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Traveler)
        .filter(Traveler.agency_id == user.agency_id)
        .order_by(Traveler.last_name)
        .all()
    )


@router.get("/{traveler_id}", response_model=TravelerOut)
def get_traveler(traveler_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = db.query(Traveler).filter(Traveler.id == traveler_id, Traveler.agency_id == user.agency_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Voyageur introuvable")
    return t


@router.post("", response_model=TravelerOut)
def create_traveler(data: TravelerCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = Traveler(agency_id=user.agency_id, **data.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.put("/{traveler_id}", response_model=TravelerOut)
def update_traveler(
    traveler_id: int,
    data: TravelerCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    t = db.query(Traveler).filter(Traveler.id == traveler_id, Traveler.agency_id == user.agency_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Voyageur introuvable")
    for key, value in data.model_dump().items():
        setattr(t, key, value)
    db.commit()
    db.refresh(t)
    return t
