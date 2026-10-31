import random
import string
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Booking, Flight, Hotel, Package, Traveler, Conversation
from app.services.catalog_service import verify_availability


def generate_reference() -> str:
    prefix = "GUA"
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=7))
    return f"{prefix}-{suffix}"


def create_booking(
    db: Session,
    agency_id: int,
    data: dict,
) -> Booking:
    flight_id = data.get("flight_id")
    hotel_id = data.get("hotel_id")
    package_id = data.get("package_id")

    availability = verify_availability(db, agency_id, flight_id=flight_id, hotel_id=hotel_id)
    if not availability["available"]:
        raise HTTPException(
            status_code=409,
            detail="L'offre n'est plus disponible. Veuillez vérifier les alternatives.",
        )

    existing = (
        db.query(Booking)
        .filter(
            Booking.agency_id == agency_id,
            Booking.contact_email == data.get("contact_email", ""),
            Booking.flight_id == flight_id,
            Booking.hotel_id == hotel_id,
            Booking.departure_date == data.get("departure_date"),
            Booking.status.in_(["pending", "confirmed"]),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Une réservation identique existe déjà.")

    ref = generate_reference()
    while db.query(Booking).filter(Booking.reference == ref).first():
        ref = generate_reference()

    booking = Booking(
        agency_id=agency_id,
        reference=ref,
        flight_id=flight_id,
        hotel_id=hotel_id,
        package_id=package_id,
        conversation_id=data.get("conversation_id"),
        traveler_id=data.get("traveler_id"),
        departure_date=data.get("departure_date"),
        return_date=data.get("return_date"),
        check_in_date=data.get("check_in_date"),
        check_out_date=data.get("check_out_date"),
        num_adults=data.get("num_adults", 1),
        num_children=data.get("num_children", 0),
        num_infants=data.get("num_infants", 0),
        traveler_details=data.get("traveler_details", []),
        contact_email=data.get("contact_email", ""),
        contact_phone=data.get("contact_phone", ""),
        special_requests=data.get("special_requests", ""),
        total_price=data["total_price"],
        currency=data.get("currency", "EUR"),
        price_verified_at=datetime.now(timezone.utc),
        status="pending",
        is_demo=True,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    if flight_id:
        flight = db.query(Flight).filter(Flight.id == flight_id).first()
        if flight and flight.available_seats > 0:
            flight.available_seats -= booking.num_adults + booking.num_children
            db.commit()

    return booking


def confirm_booking(db: Session, agency_id: int, booking_id: int) -> Booking:
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.agency_id == agency_id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation introuvable")
    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Seule une réservation en attente peut être confirmée")

    availability = verify_availability(db, agency_id, flight_id=booking.flight_id, hotel_id=booking.hotel_id)
    if not availability["available"]:
        raise HTTPException(status_code=409, detail="L'offre n'est plus disponible")

    booking.status = "confirmed"
    booking.confirmed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(booking)
    return booking


def cancel_booking(db: Session, agency_id: int, booking_id: int, reason: str = "") -> Booking:
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.agency_id == agency_id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Réservation introuvable")

    booking.status = "cancelled"
    booking.cancelled_at = datetime.now(timezone.utc)
    booking.cancellation_reason = reason

    if booking.flight_id:
        flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
        if flight:
            flight.available_seats += booking.num_adults + booking.num_children
    db.commit()
    db.refresh(booking)
    return booking
