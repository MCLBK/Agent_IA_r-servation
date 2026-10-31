from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Agency
from app.schemas import LoginRequest, TokenResponse, UserOut
from app.services.auth_service import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.is_active == True).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = create_access_token({"sub": str(user.id), "agency_id": user.agency_id, "role": user.role})
    agency = db.query(Agency).filter(Agency.id == user.agency_id).first()

    return TokenResponse(
        access_token=token,
        user=UserOut(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            agency_id=user.agency_id,
            agency_name=agency.name if agency else "",
        ),
    )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agency = db.query(Agency).filter(Agency.id == user.agency_id).first()
    return UserOut(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        agency_id=user.agency_id,
        agency_name=agency.name if agency else "",
    )
