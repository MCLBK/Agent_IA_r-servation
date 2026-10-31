from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Conversation, Message, User
from app.schemas import ConversationOut, ConversationDetail, MessageOut
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    status: str | None = None,
    needs_human: bool | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Conversation).filter(Conversation.agency_id == user.agency_id)
    if status:
        q = q.filter(Conversation.status == status)
    if needs_human is not None:
        q = q.filter(Conversation.needs_human == needs_human)
    convs = q.order_by(Conversation.last_message_at.desc()).all()
    result = []
    for c in convs:
        out = ConversationOut.model_validate(c)
        out.message_count = len(c.messages)
        if c.traveler:
            out.traveler_name = f"{c.traveler.first_name} {c.traveler.last_name}"
        result.append(out)
    return result


@router.get("/{conv_id}", response_model=ConversationDetail)
def get_conversation(conv_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.agency_id == user.agency_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    out = ConversationDetail.model_validate(c)
    out.message_count = len(c.messages)
    out.messages = [MessageOut.model_validate(m) for m in c.messages]
    if c.traveler:
        out.traveler_name = f"{c.traveler.first_name} {c.traveler.last_name}"
    return out


@router.post("/{conv_id}/assign")
def assign_conversation(
    conv_id: int,
    agent_id: int | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    c = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.agency_id == user.agency_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    c.assigned_agent_id = agent_id or user.id
    db.commit()
    return {"message": "Conversation assignee"}


@router.post("/{conv_id}/reply")
def agent_reply(
    conv_id: int,
    message: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    c = db.query(Conversation).filter(Conversation.id == conv_id, Conversation.agency_id == user.agency_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    msg = Message(
        conversation_id=c.id,
        role="agent",
        content=message,
        metadata_={"agent_user_id": user.id, "agent_name": f"{user.first_name} {user.last_name}"},
    )
    db.add(msg)
    c.needs_human = False
    c.assigned_agent_id = user.id
    db.commit()
    return {"message": "Reponse envoyee"}
