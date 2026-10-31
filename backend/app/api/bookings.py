from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Booking, User, Flight, Hotel
from app.schemas import BookingOut, BookingCreate, BookingPublicOut
from app.services.auth_service import get_current_user
from app.services.booking_service import create_booking, confirm_booking, cancel_booking

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingOut])
def list_bookings(
    status: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Booking).filter(Booking.agency_id == user.agency_id)
    if status:
        q = q.filter(Booking.status == status)
    bookings = q.order_by(Booking.created_at.desc()).all()
    result = []
    for b in bookings:
        out = BookingOut.model_validate(b)
        if b.flight:
            from app.schemas import FlightOut
            out.flight = FlightOut.model_validate(b.flight)
            if b.flight.destination:
                out.destination_name = b.flight.destination.name
        if b.hotel:
            from app.schemas import HotelOut
            out.hotel = HotelOut.model_validate(b.hotel)
        result.append(out)
    return result


@router.get("/track/{reference}", response_model=BookingPublicOut)
def track_booking(reference: str, email: str = "", db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.reference == reference.upper().strip()).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Reservation introuvable. Verifiez la reference.")
    if email and booking.contact_email and booking.contact_email.lower() != email.lower().strip():
        raise HTTPException(status_code=404, detail="Reservation introuvable. Verifiez la reference et l'email.")

    result = BookingPublicOut.model_validate(booking)
    if booking.flight:
        result.flight_summary = (
            f"{booking.flight.airline} {booking.flight.flight_number} — "
            f"{booking.flight.departure_city} ({booking.flight.departure_airport}) "
            f"{booking.flight.departure_time} → "
            f"{booking.flight.arrival_city} ({booking.flight.arrival_airport}) "
            f"{booking.flight.arrival_time}"
        )
        if booking.flight.destination:
            result.destination_name = booking.flight.destination.name
            result.destination_country = booking.flight.destination.country
    if booking.hotel:
        result.hotel_summary = (
            f"{booking.hotel.name} {'★' * booking.hotel.category} — "
            f"{booking.hotel.city} · {booking.hotel.meal_plan}"
        )
    return result


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    b = db.query(Booking).filter(Booking.id == booking_id, Booking.agency_id == user.agency_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Reservation introuvable")
    out = BookingOut.model_validate(b)
    if b.flight:
        from app.schemas import FlightOut
        out.flight = FlightOut.model_validate(b.flight)
        if b.flight.destination:
            out.destination_name = b.flight.destination.name
    if b.hotel:
        from app.schemas import HotelOut
        out.hotel = HotelOut.model_validate(b.hotel)
    return out


@router.post("/{booking_id}/confirm", response_model=BookingOut)
def confirm(booking_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return confirm_booking(db, user.agency_id, booking_id)


@router.post("/{booking_id}/cancel")
def cancel(booking_id: int, reason: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return cancel_booking(db, user.agency_id, booking_id, reason)
