from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, Date,
    ForeignKey, JSON, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


# ──────────────────────────────────────────────
# AGENCY (tenant)
# ──────────────────────────────────────────────

class Agency(Base):
    __tablename__ = "agencies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, default="")
    logo_url = Column(String(500), default="")
    primary_color = Column(String(7), default="#1B3A5C")
    secondary_color = Column(String(7), default="#C9A84C")
    currency = Column(String(3), default="EUR")
    timezone = Column(String(50), default="Europe/Paris")

    agent_name = Column(String(100), default="Assistant Voyage")
    agent_tone = Column(String(50), default="chaleureux")
    welcome_message = Column(Text, default="Bonjour ! Je suis votre assistant voyage. Comment puis-je vous aider aujourd'hui ?")
    agent_instructions = Column(Text, default="")

    payment_link_template = Column(String(500), default="")
    escalation_email = Column(String(200), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    users = relationship("User", back_populates="agency")
    destinations = relationship("Destination", back_populates="agency")
    flights = relationship("Flight", back_populates="agency")
    hotels = relationship("Hotel", back_populates="agency")
    packages = relationship("Package", back_populates="agency")
    bookings = relationship("Booking", back_populates="agency")
    conversations = relationship("Conversation", back_populates="agency")
    travelers = relationship("Traveler", back_populates="agency")


# ──────────────────────────────────────────────
# USER (agency staff)
# ──────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(20), default="agent")  # admin, agent
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    agency = relationship("Agency", back_populates="users")
    assigned_conversations = relationship("Conversation", back_populates="assigned_agent", foreign_keys="Conversation.assigned_agent_id")
    assigned_bookings = relationship("Booking", back_populates="assigned_agent", foreign_keys="Booking.assigned_agent_id")


# ──────────────────────────────────────────────
# DESTINATION
# ──────────────────────────────────────────────

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    country = Column(String(100), nullable=False)
    description = Column(Text, default="")
    image_url = Column(String(500), default="")
    highlights = Column(JSON, default=list)
    best_season = Column(String(100), default="")
    avg_temperature = Column(String(50), default="")
    flight_duration_from_paris = Column(String(50), default="")
    destination_type = Column(String(50), default="")  # plage, culture, aventure, famille
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    agency = relationship("Agency", back_populates="destinations")
    flights = relationship("Flight", back_populates="destination")
    hotels = relationship("Hotel", back_populates="destination")

    __table_args__ = (
        Index("ix_dest_agency_active", "agency_id", "is_active"),
    )


# ──────────────────────────────────────────────
# FLIGHT
# ──────────────────────────────────────────────

class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=False, index=True)

    airline = Column(String(100), nullable=False)
    flight_number = Column(String(20), default="")
    departure_city = Column(String(100), nullable=False)
    departure_airport = Column(String(10), nullable=False)
    departure_time = Column(String(5), nullable=False)  # "08:30"
    arrival_city = Column(String(100), nullable=False)
    arrival_airport = Column(String(10), nullable=False)
    arrival_time = Column(String(5), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    stops = Column(Integer, default=0)
    stop_cities = Column(JSON, default=list)

    baggage_included = Column(JSON, default=dict)  # {"cabin": "10kg", "checked": "23kg"}
    price_per_adult = Column(Float, nullable=False)
    price_per_child = Column(Float, nullable=False)
    price_per_infant = Column(Float, default=0)
    currency = Column(String(3), default="EUR")

    cancellation_policy = Column(Text, default="")
    modification_policy = Column(Text, default="")
    available_seats = Column(Integer, default=50)
    is_available = Column(Boolean, default=True)

    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    departure_days = Column(JSON, default=list)  # [1, 3, 5] = lun, mer, ven

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    agency = relationship("Agency", back_populates="flights")
    destination = relationship("Destination", back_populates="flights")


# ──────────────────────────────────────────────
# HOTEL
# ──────────────────────────────────────────────

class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=False, index=True)

    name = Column(String(200), nullable=False)
    category = Column(Integer, default=3)  # stars
    address = Column(String(300), default="")
    city = Column(String(100), nullable=False)
    description = Column(Text, default="")
    image_url = Column(String(500), default="")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    amenities = Column(JSON, default=list)  # ["piscine", "wifi", "spa", "restaurant"]
    room_types = Column(JSON, default=list)  # [{"name": "Standard", "price_per_night": 80, ...}]
    meal_plan = Column(String(50), default="petit-dejeuner")  # petit-dejeuner, demi-pension, all-inclusive

    price_per_night = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    cancellation_policy = Column(Text, default="")
    is_available = Column(Boolean, default=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    agency = relationship("Agency", back_populates="hotels")
    destination = relationship("Destination", back_populates="hotels")


# ──────────────────────────────────────────────
# PACKAGE (forfait vol + hotel)
# ──────────────────────────────────────────────

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)

    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    price_per_adult = Column(Float, nullable=False)
    price_per_child = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0)
    is_available = Column(Boolean, default=True)

    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    agency = relationship("Agency", back_populates="packages")
    flight = relationship("Flight")
    hotel = relationship("Hotel")


# ──────────────────────────────────────────────
# TRAVELER
# ──────────────────────────────────────────────

class Traveler(Base):
    __tablename__ = "travelers"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False, index=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    email = Column(String(200), default="")
    phone = Column(String(30), default="")
    nationality = Column(String(50), default="")
    preferences = Column(JSON, default=dict)

    gdpr_consent = Column(Boolean, default=False)
    gdpr_consent_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    agency = relationship("Agency", back_populates="travelers")
    conversations = relationship("Conversation", back_populates="traveler")
    bookings = relationship("Booking", back_populates="traveler")


# ──────────────────────────────────────────────
# CONVERSATION
# ──────────────────────────────────────────────

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    traveler_id = Column(Integer, ForeignKey("travelers.id"), nullable=True)

    status = Column(String(20), default="active")  # active, completed, escalated, abandoned
    channel = Column(String(20), default="web")
    travel_project = Column(JSON, default=dict)
    current_step = Column(String(50), default="greeting")

    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    escalation_reason = Column(Text, default="")
    needs_human = Column(Boolean, default=False)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    last_message_at = Column(DateTime, default=utcnow)

    agency = relationship("Agency", back_populates="conversations")
    traveler = relationship("Traveler", back_populates="conversations")
    assigned_agent = relationship("User", back_populates="assigned_conversations", foreign_keys=[assigned_agent_id])
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")


# ──────────────────────────────────────────────
# MESSAGE
# ──────────────────────────────────────────────

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)

    role = Column(String(20), nullable=False)  # user, assistant, system, agent
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)

    conversation = relationship("Conversation", back_populates="messages")


# ──────────────────────────────────────────────
# BOOKING
# ──────────────────────────────────────────────

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False, index=True)
    reference = Column(String(20), unique=True, nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    traveler_id = Column(Integer, ForeignKey("travelers.id"), nullable=True)

    status = Column(String(20), default="pending")  # pending, confirmed, cancelled, modified
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)

    departure_date = Column(Date, nullable=True)
    return_date = Column(Date, nullable=True)
    check_in_date = Column(Date, nullable=True)
    check_out_date = Column(Date, nullable=True)

    num_adults = Column(Integer, default=1)
    num_children = Column(Integer, default=0)
    num_infants = Column(Integer, default=0)
    traveler_details = Column(JSON, default=list)

    contact_email = Column(String(200), default="")
    contact_phone = Column(String(30), default="")
    special_requests = Column(Text, default="")

    total_price = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    payment_status = Column(String(20), default="pending")  # pending, paid, refunded

    price_verified_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, default="")

    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_demo = Column(Boolean, default=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    agency = relationship("Agency", back_populates="bookings")
    traveler = relationship("Traveler", back_populates="bookings")
    conversation = relationship("Conversation")
    flight = relationship("Flight")
    hotel = relationship("Hotel")
    package = relationship("Package")
    assigned_agent = relationship("User", back_populates="assigned_bookings", foreign_keys=[assigned_agent_id])


# ──────────────────────────────────────────────
# AUDIT LOG
# ──────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), default="")
    entity_id = Column(Integer, nullable=True)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)
