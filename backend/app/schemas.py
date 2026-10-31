from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class UserOut(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    agency_id: int
    agency_name: str = ""

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# AGENCY
# ──────────────────────────────────────────────

class AgencyOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    primary_color: str
    secondary_color: str
    currency: str
    agent_name: str
    welcome_message: str

    class Config:
        from_attributes = True

class AgencySettingsUpdate(BaseModel):
    agent_name: Optional[str] = None
    agent_tone: Optional[str] = None
    welcome_message: Optional[str] = None
    agent_instructions: Optional[str] = None
    currency: Optional[str] = None
    payment_link_template: Optional[str] = None
    escalation_email: Optional[str] = None


# ──────────────────────────────────────────────
# DESTINATION
# ──────────────────────────────────────────────

class DestinationCreate(BaseModel):
    name: str
    country: str
    description: str = ""
    image_url: str = ""
    highlights: list[str] = []
    best_season: str = ""
    avg_temperature: str = ""
    flight_duration_from_paris: str = ""
    destination_type: str = ""

class DestinationUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    highlights: Optional[list[str]] = None
    best_season: Optional[str] = None
    avg_temperature: Optional[str] = None
    destination_type: Optional[str] = None
    is_active: Optional[bool] = None

class DestinationOut(BaseModel):
    id: int
    name: str
    country: str
    description: str
    image_url: str
    highlights: list
    best_season: str
    avg_temperature: str
    flight_duration_from_paris: str
    destination_type: str
    is_active: bool

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# FLIGHT
# ──────────────────────────────────────────────

class FlightCreate(BaseModel):
    destination_id: int
    airline: str
    flight_number: str = ""
    departure_city: str
    departure_airport: str
    departure_time: str
    arrival_city: str
    arrival_airport: str
    arrival_time: str
    duration_minutes: int
    stops: int = 0
    stop_cities: list[str] = []
    baggage_included: dict = {}
    price_per_adult: float
    price_per_child: float
    price_per_infant: float = 0
    cancellation_policy: str = ""
    modification_policy: str = ""
    available_seats: int = 50
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    departure_days: list[int] = []

class FlightOut(BaseModel):
    id: int
    destination_id: int
    airline: str
    flight_number: str
    departure_city: str
    departure_airport: str
    departure_time: str
    arrival_city: str
    arrival_airport: str
    arrival_time: str
    duration_minutes: int
    stops: int
    stop_cities: list
    baggage_included: dict
    price_per_adult: float
    price_per_child: float
    price_per_infant: float
    currency: str
    cancellation_policy: str
    modification_policy: str
    available_seats: int
    is_available: bool
    destination_name: str = ""

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# HOTEL
# ──────────────────────────────────────────────

class HotelCreate(BaseModel):
    destination_id: int
    name: str
    category: int = 3
    address: str = ""
    city: str
    description: str = ""
    image_url: str = ""
    amenities: list[str] = []
    room_types: list[dict] = []
    meal_plan: str = "petit-dejeuner"
    price_per_night: float
    cancellation_policy: str = ""

class HotelOut(BaseModel):
    id: int
    destination_id: int
    name: str
    category: int
    address: str
    city: str
    description: str
    image_url: str
    amenities: list
    room_types: list
    meal_plan: str
    price_per_night: float
    currency: str
    cancellation_policy: str
    is_available: bool
    destination_name: str = ""

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# PACKAGE
# ──────────────────────────────────────────────

class PackageCreate(BaseModel):
    flight_id: int
    hotel_id: int
    name: str
    description: str = ""
    price_per_adult: float
    price_per_child: float
    discount_percentage: float = 0
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None

class PackageOut(BaseModel):
    id: int
    flight_id: int
    hotel_id: int
    name: str
    description: str
    price_per_adult: float
    price_per_child: float
    discount_percentage: float
    is_available: bool
    flight: Optional[FlightOut] = None
    hotel: Optional[HotelOut] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# TRAVELER
# ──────────────────────────────────────────────

class TravelerCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    email: str = ""
    phone: str = ""
    nationality: str = ""

class TravelerOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: Optional[date]
    email: str
    phone: str
    nationality: str
    preferences: dict
    gdpr_consent: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# BOOKING
# ──────────────────────────────────────────────

class BookingCreate(BaseModel):
    flight_id: Optional[int] = None
    hotel_id: Optional[int] = None
    package_id: Optional[int] = None
    departure_date: Optional[date] = None
    return_date: Optional[date] = None
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    num_adults: int = 1
    num_children: int = 0
    num_infants: int = 0
    traveler_details: list[dict] = []
    contact_email: str = ""
    contact_phone: str = ""
    special_requests: str = ""
    total_price: float
    traveler_id: Optional[int] = None
    conversation_id: Optional[int] = None

class BookingOut(BaseModel):
    id: int
    reference: str
    status: str
    departure_date: Optional[date]
    return_date: Optional[date]
    check_in_date: Optional[date]
    check_out_date: Optional[date]
    num_adults: int
    num_children: int
    num_infants: int
    traveler_details: list
    contact_email: str
    contact_phone: str
    special_requests: str
    total_price: float
    currency: str
    payment_status: str
    is_demo: bool
    created_at: datetime
    confirmed_at: Optional[datetime]
    flight: Optional[FlightOut] = None
    hotel: Optional[HotelOut] = None
    destination_name: str = ""

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# CONVERSATION
# ──────────────────────────────────────────────

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    metadata_: dict = Field(default={}, alias="metadata_")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class ConversationOut(BaseModel):
    id: int
    session_id: str
    status: str
    channel: str
    travel_project: dict
    current_step: str
    needs_human: bool
    escalation_reason: str
    created_at: datetime
    last_message_at: datetime
    message_count: int = 0
    traveler_name: str = ""

    class Config:
        from_attributes = True

class ConversationDetail(ConversationOut):
    messages: list[MessageOut] = []

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    agency_slug: str = "demo"

class ChatResponse(BaseModel):
    message: str
    session_id: str
    step: str
    travel_project: dict
    offers: Optional[list] = None
    booking: Optional[dict] = None
    needs_human: bool = False


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_conversations: int
    active_conversations: int
    total_bookings: int
    confirmed_bookings: int
    pending_bookings: int
    total_revenue: float
    escalated_conversations: int
    conversion_rate: float
    recent_bookings: list[BookingOut] = []
    recent_conversations: list[ConversationOut] = []
    top_destinations: list[dict] = []
