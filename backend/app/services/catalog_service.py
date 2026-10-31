from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models import Destination, Flight, Hotel, Package


def search_destinations(
    db: Session,
    agency_id: int,
    budget: float | None = None,
    destination_type: str | None = None,
    query: str | None = None,
    limit: int = 3,
) -> list[Destination]:
    q = db.query(Destination).filter(
        Destination.agency_id == agency_id,
        Destination.is_active == True,
    )
    if destination_type:
        q = q.filter(Destination.destination_type.ilike(f"%{destination_type}%"))
    if query:
        q = q.filter(
            (Destination.name.ilike(f"%{query}%"))
            | (Destination.country.ilike(f"%{query}%"))
            | (Destination.description.ilike(f"%{query}%"))
        )
    destinations = q.all()

    if budget is not None:
        scored = []
        for d in destinations:
            min_flight = (
                db.query(Flight)
                .filter(Flight.destination_id == d.id, Flight.agency_id == agency_id, Flight.is_available == True)
                .order_by(Flight.price_per_adult)
                .first()
            )
            if min_flight and min_flight.price_per_adult <= budget:
                scored.append((d, min_flight.price_per_adult))
        scored.sort(key=lambda x: x[1])
        return [s[0] for s in scored[:limit]]

    return destinations[:limit]


def search_flights(
    db: Session,
    agency_id: int,
    destination_id: int | None = None,
    departure_city: str | None = None,
    max_price: float | None = None,
    max_stops: int | None = None,
    limit: int = 3,
) -> list[Flight]:
    q = db.query(Flight).filter(
        Flight.agency_id == agency_id,
        Flight.is_available == True,
    )
    if destination_id:
        q = q.filter(Flight.destination_id == destination_id)
    if departure_city:
        q = q.filter(Flight.departure_city.ilike(f"%{departure_city}%"))
    if max_price is not None:
        q = q.filter(Flight.price_per_adult <= max_price)
    if max_stops is not None:
        q = q.filter(Flight.stops <= max_stops)

    return q.order_by(Flight.price_per_adult).limit(limit).all()


def search_hotels(
    db: Session,
    agency_id: int,
    destination_id: int | None = None,
    max_price_per_night: float | None = None,
    min_category: int | None = None,
    limit: int = 3,
) -> list[Hotel]:
    q = db.query(Hotel).filter(
        Hotel.agency_id == agency_id,
        Hotel.is_available == True,
    )
    if destination_id:
        q = q.filter(Hotel.destination_id == destination_id)
    if max_price_per_night is not None:
        q = q.filter(Hotel.price_per_night <= max_price_per_night)
    if min_category is not None:
        q = q.filter(Hotel.category >= min_category)

    return q.order_by(Hotel.price_per_night).limit(limit).all()


def search_packages(
    db: Session,
    agency_id: int,
    destination_id: int | None = None,
    max_price: float | None = None,
    limit: int = 3,
) -> list[Package]:
    q = db.query(Package).filter(
        Package.agency_id == agency_id,
        Package.is_available == True,
    )
    if destination_id:
        q = q.join(Flight).filter(Flight.destination_id == destination_id)
    if max_price is not None:
        q = q.filter(Package.price_per_adult <= max_price)

    return q.limit(limit).all()


def verify_availability(
    db: Session,
    agency_id: int,
    flight_id: int | None = None,
    hotel_id: int | None = None,
) -> dict:
    result = {"verified_at": datetime.now(timezone.utc).isoformat(), "available": True, "details": {}}

    if flight_id:
        flight = db.query(Flight).filter(Flight.id == flight_id, Flight.agency_id == agency_id).first()
        if not flight:
            return {"verified_at": result["verified_at"], "available": False, "details": {"error": "Vol introuvable"}}
        result["details"]["flight"] = {
            "id": flight.id,
            "available": flight.is_available and flight.available_seats > 0,
            "price_per_adult": flight.price_per_adult,
            "available_seats": flight.available_seats,
        }
        if not result["details"]["flight"]["available"]:
            result["available"] = False

    if hotel_id:
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id, Hotel.agency_id == agency_id).first()
        if not hotel:
            return {"verified_at": result["verified_at"], "available": False, "details": {"error": "Hotel introuvable"}}
        result["details"]["hotel"] = {
            "id": hotel.id,
            "available": hotel.is_available,
            "price_per_night": hotel.price_per_night,
        }
        if not result["details"]["hotel"]["available"]:
            result["available"] = False

    return result
