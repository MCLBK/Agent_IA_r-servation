from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Destination, Flight, Hotel, Package, User
from app.schemas import (
    DestinationCreate, DestinationUpdate, DestinationOut,
    FlightCreate, FlightOut,
    HotelCreate, HotelOut,
    PackageCreate, PackageOut,
)
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/catalog", tags=["catalog"])


# ── Destinations ──

@router.get("/destinations", response_model=list[DestinationOut])
def list_destinations(
    active_only: bool = True,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Destination).filter(Destination.agency_id == user.agency_id)
    if active_only:
        q = q.filter(Destination.is_active == True)
    return q.order_by(Destination.name).all()


@router.post("/destinations", response_model=DestinationOut)
def create_destination(
    data: DestinationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dest = Destination(agency_id=user.agency_id, **data.model_dump())
    db.add(dest)
    db.commit()
    db.refresh(dest)
    return dest


@router.get("/destinations/{dest_id}", response_model=DestinationOut)
def get_destination(dest_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dest = db.query(Destination).filter(Destination.id == dest_id, Destination.agency_id == user.agency_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination introuvable")
    return dest


@router.put("/destinations/{dest_id}", response_model=DestinationOut)
def update_destination(
    dest_id: int,
    data: DestinationUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dest = db.query(Destination).filter(Destination.id == dest_id, Destination.agency_id == user.agency_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination introuvable")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(dest, key, value)
    db.commit()
    db.refresh(dest)
    return dest


@router.delete("/destinations/{dest_id}")
def delete_destination(dest_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dest = db.query(Destination).filter(Destination.id == dest_id, Destination.agency_id == user.agency_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination introuvable")
    dest.is_active = False
    db.commit()
    return {"message": "Destination desactivee"}


# ── Flights ──

@router.get("/flights", response_model=list[FlightOut])
def list_flights(
    destination_id: int | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Flight).filter(Flight.agency_id == user.agency_id)
    if destination_id:
        q = q.filter(Flight.destination_id == destination_id)
    flights = q.order_by(Flight.price_per_adult).all()
    result = []
    for f in flights:
        out = FlightOut.model_validate(f)
        if f.destination:
            out.destination_name = f.destination.name
        result.append(out)
    return result


@router.post("/flights", response_model=FlightOut)
def create_flight(data: FlightCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    flight = Flight(agency_id=user.agency_id, **data.model_dump())
    db.add(flight)
    db.commit()
    db.refresh(flight)
    return flight


@router.put("/flights/{flight_id}", response_model=FlightOut)
def update_flight(
    flight_id: int,
    data: FlightCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    flight = db.query(Flight).filter(Flight.id == flight_id, Flight.agency_id == user.agency_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Vol introuvable")
    for key, value in data.model_dump().items():
        setattr(flight, key, value)
    db.commit()
    db.refresh(flight)
    return flight


@router.delete("/flights/{flight_id}")
def delete_flight(flight_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    flight = db.query(Flight).filter(Flight.id == flight_id, Flight.agency_id == user.agency_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Vol introuvable")
    flight.is_available = False
    db.commit()
    return {"message": "Vol desactive"}


# ── Hotels ──

@router.get("/hotels", response_model=list[HotelOut])
def list_hotels(
    destination_id: int | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Hotel).filter(Hotel.agency_id == user.agency_id)
    if destination_id:
        q = q.filter(Hotel.destination_id == destination_id)
    hotels = q.order_by(Hotel.price_per_night).all()
    result = []
    for h in hotels:
        out = HotelOut.model_validate(h)
        if h.destination:
            out.destination_name = h.destination.name
        result.append(out)
    return result


@router.post("/hotels", response_model=HotelOut)
def create_hotel(data: HotelCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hotel = Hotel(agency_id=user.agency_id, **data.model_dump())
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return hotel


@router.put("/hotels/{hotel_id}", response_model=HotelOut)
def update_hotel(
    hotel_id: int,
    data: HotelCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id, Hotel.agency_id == user.agency_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel introuvable")
    for key, value in data.model_dump().items():
        setattr(hotel, key, value)
    db.commit()
    db.refresh(hotel)
    return hotel


@router.delete("/hotels/{hotel_id}")
def delete_hotel(hotel_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id, Hotel.agency_id == user.agency_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel introuvable")
    hotel.is_available = False
    db.commit()
    return {"message": "Hotel desactive"}


# ── Packages ──

@router.get("/packages", response_model=list[PackageOut])
def list_packages(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    packages = db.query(Package).filter(Package.agency_id == user.agency_id).all()
    result = []
    for p in packages:
        out = PackageOut.model_validate(p)
        if p.flight:
            out.flight = FlightOut.model_validate(p.flight)
        if p.hotel:
            out.hotel = HotelOut.model_validate(p.hotel)
        result.append(out)
    return result


@router.post("/packages", response_model=PackageOut)
def create_package(data: PackageCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    package = Package(agency_id=user.agency_id, **data.model_dump())
    db.add(package)
    db.commit()
    db.refresh(package)
    return package
