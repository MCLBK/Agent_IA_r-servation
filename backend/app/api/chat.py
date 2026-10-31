from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Agency
from app.schemas import ChatRequest, ChatResponse
from app.ai.agent import TravelAgent

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(data: ChatRequest, db: Session = Depends(get_db)):
    agency = db.query(Agency).filter(Agency.slug == data.agency_slug, Agency.is_active == True).first()
    if not agency:
        raise HTTPException(status_code=404, detail="Agence introuvable")

    agent = TravelAgent(db, agency)
    result = await agent.handle_message(data.session_id, data.message)
    return ChatResponse(**result)


@router.get("/agency/{slug}")
def get_agency_public(slug: str, db: Session = Depends(get_db)):
    agency = db.query(Agency).filter(Agency.slug == slug, Agency.is_active == True).first()
    if not agency:
        raise HTTPException(status_code=404, detail="Agence introuvable")
    return {
        "name": agency.name,
        "agent_name": agency.agent_name,
        "welcome_message": agency.welcome_message,
        "primary_color": agency.primary_color,
        "secondary_color": agency.secondary_color,
        "currency": agency.currency,
    }
