from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Booking, Conversation, Flight, Destination, User
from app.schemas import DashboardStats, BookingOut, ConversationOut
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    aid = user.agency_id

    total_conversations = db.query(Conversation).filter(Conversation.agency_id == aid).count()
    active_conversations = db.query(Conversation).filter(
        Conversation.agency_id == aid, Conversation.status == "active"
    ).count()
    escalated = db.query(Conversation).filter(
        Conversation.agency_id == aid, Conversation.needs_human == True
    ).count()

    total_bookings = db.query(Booking).filter(Booking.agency_id == aid).count()
    confirmed = db.query(Booking).filter(Booking.agency_id == aid, Booking.status == "confirmed").count()
    pending = db.query(Booking).filter(Booking.agency_id == aid, Booking.status == "pending").count()

    revenue = db.query(func.coalesce(func.sum(Booking.total_price), 0)).filter(
        Booking.agency_id == aid, Booking.status.in_(["confirmed", "pending"])
    ).scalar()

    conversion = 0.0
    if total_conversations > 0:
        conversion = round(total_bookings / total_conversations * 100, 1)

    recent_bookings_q = (
        db.query(Booking)
        .filter(Booking.agency_id == aid)
        .order_by(Booking.created_at.desc())
        .limit(5)
        .all()
    )
    recent_bookings = []
    for b in recent_bookings_q:
        out = BookingOut.model_validate(b)
        if b.flight and b.flight.destination:
            out.destination_name = b.flight.destination.name
        recent_bookings.append(out)

    recent_conversations_q = (
        db.query(Conversation)
        .filter(Conversation.agency_id == aid)
        .order_by(Conversation.last_message_at.desc())
        .limit(5)
        .all()
    )
    recent_conversations = []
    for c in recent_conversations_q:
        out = ConversationOut.model_validate(c)
        out.message_count = len(c.messages)
        recent_conversations.append(out)

    top_dest_rows = (
        db.query(Destination.name, func.count(Booking.id).label("count"))
        .join(Flight, Flight.destination_id == Destination.id)
        .join(Booking, Booking.flight_id == Flight.id)
        .filter(Booking.agency_id == aid)
        .group_by(Destination.name)
        .order_by(func.count(Booking.id).desc())
        .limit(5)
        .all()
    )
    top_destinations = [{"name": r[0], "count": r[1]} for r in top_dest_rows]

    return DashboardStats(
        total_conversations=total_conversations,
        active_conversations=active_conversations,
        total_bookings=total_bookings,
        confirmed_bookings=confirmed,
        pending_bookings=pending,
        total_revenue=float(revenue),
        escalated_conversations=escalated,
        conversion_rate=conversion,
        recent_bookings=recent_bookings,
        recent_conversations=recent_conversations,
        top_destinations=top_destinations,
    )
