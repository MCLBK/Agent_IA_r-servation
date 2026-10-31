from datetime import date
from sqlalchemy.orm import Session
from app.models import Agency, User, Destination, Flight, Hotel, Package
from app.services.auth_service import hash_password


def seed_demo_data(db: Session):
    if db.query(Agency).first():
        return

    agency = Agency(
        name="Voyages Horizon",
        slug="demo",
        description="Agence de voyages partenaire GrowUp AI - Donnees de demonstration",
        primary_color="#1B3A5C",
        secondary_color="#C9A84C",
        currency="EUR",
        agent_name="Horizon",
        agent_tone="chaleureux",
        welcome_message=(
            "Bonjour ! Je suis Horizon, votre assistant voyage.\n\n"
            "Je suis la pour vous aider a trouver le sejour ideal : "
            "destinations, vols, hotels... Dites-moi simplement ce qui vous ferait envie !"
        ),
        payment_link_template="https://demo.growupai.com/paiement/{reference}",
        escalation_email="conseillers@voyages-horizon.demo",
    )
    db.add(agency)
    db.flush()

    admin = User(
        agency_id=agency.id,
        email="admin@demo.com",
        password_hash=hash_password("admin123"),
        first_name="Marie",
        last_name="Dupont",
        role="admin",
    )
    agent_user = User(
        agency_id=agency.id,
        email="agent@demo.com",
        password_hash=hash_password("agent123"),
        first_name="Thomas",
        last_name="Martin",
        role="agent",
    )
    db.add_all([admin, agent_user])
    db.flush()

    # ── Destinations ──

    marrakech = Destination(
        agency_id=agency.id,
        name="Marrakech",
        country="Maroc",
        description=(
            "Ville imperiale aux mille couleurs, Marrakech seduit par ses souks animes, "
            "ses palais somptueux et sa gastronomie genereuse. Entre la place Jemaa el-Fna "
            "et les jardins de Majorelle, chaque ruelle raconte une histoire."
        ),
        image_url="https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=800",
        highlights=["Medina et souks", "Jardins de Majorelle", "Gastronomie", "Hammams traditionnels"],
        best_season="Octobre a avril",
        avg_temperature="25°C",
        flight_duration_from_paris="3h30",
        destination_type="culture",
    )

    lisbonne = Destination(
        agency_id=agency.id,
        name="Lisbonne",
        country="Portugal",
        description=(
            "Capitale lumineuse du Portugal, Lisbonne charme par ses ruelles pavees, "
            "ses tramways historiques et ses pasteis de nata. Une ville a taille humaine "
            "ou la douceur de vivre se marie a une scene culturelle effervescente."
        ),
        image_url="https://images.unsplash.com/photo-1585208798174-6cedd86e019a?w=800",
        highlights=["Quartier de l'Alfama", "Tramway 28", "Pasteis de Belem", "Bord de mer a Cascais"],
        best_season="Avril a octobre",
        avg_temperature="22°C",
        flight_duration_from_paris="2h30",
        destination_type="culture",
    )

    bali = Destination(
        agency_id=agency.id,
        name="Bali",
        country="Indonesie",
        description=(
            "Ile des dieux, Bali offre des rizieres en terrasses spectaculaires, "
            "des temples millenaires et des plages de reve. Un paradis tropical "
            "ou spiritualite et nature se rejoignent."
        ),
        image_url="https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800",
        highlights=["Rizieres de Tegallalang", "Temple d'Uluwatu", "Plages de Seminyak", "Snorkeling"],
        best_season="Mai a septembre",
        avg_temperature="28°C",
        flight_duration_from_paris="16h",
        destination_type="plage",
    )

    santorin = Destination(
        agency_id=agency.id,
        name="Santorin",
        country="Grece",
        description=(
            "Joyau des Cyclades, Santorin enchante avec ses maisons blanches et bleues "
            "perchees sur la caldeira, ses couchers de soleil legendaires et ses plages "
            "de sable noir volcanique."
        ),
        image_url="https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?w=800",
        highlights=["Coucher de soleil a Oia", "Plage Rouge", "Vins locaux", "Villages perches"],
        best_season="Mai a octobre",
        avg_temperature="26°C",
        flight_duration_from_paris="3h30",
        destination_type="romantique",
    )

    dubai = Destination(
        agency_id=agency.id,
        name="Dubai",
        country="Emirats Arabes Unis",
        description=(
            "Metropole futuriste entre desert et mer, Dubai impressionne par son architecture "
            "audacieuse, ses centres commerciaux demesures et ses experiences uniques. "
            "Un melange fascinant de tradition et de modernite."
        ),
        image_url="https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800",
        highlights=["Burj Khalifa", "Desert safari", "Shopping", "Plages"],
        best_season="Novembre a mars",
        avg_temperature="30°C",
        flight_duration_from_paris="6h30",
        destination_type="aventure",
    )

    db.add_all([marrakech, lisbonne, bali, santorin, dubai])
    db.flush()

    # ── Flights ──

    flights = [
        Flight(agency_id=agency.id, destination_id=marrakech.id,
               airline="Royal Air Maroc", flight_number="AT789",
               departure_city="Paris", departure_airport="CDG",
               departure_time="08:30", arrival_city="Marrakech", arrival_airport="RAK",
               arrival_time="11:00", duration_minutes=210, stops=0,
               baggage_included={"cabin": "10 kg", "checked": "23 kg"},
               price_per_adult=189, price_per_child=149, price_per_infant=30,
               cancellation_policy="Annulation gratuite jusqu'a 48h avant le depart",
               modification_policy="Modification possible moyennant 50 EUR",
               available_seats=42, valid_from=date(2026, 11, 1), valid_until=date(2027, 3, 31)),

        Flight(agency_id=agency.id, destination_id=marrakech.id,
               airline="Transavia", flight_number="TO3456",
               departure_city="Paris", departure_airport="ORY",
               departure_time="14:15", arrival_city="Marrakech", arrival_airport="RAK",
               arrival_time="16:45", duration_minutes=210, stops=0,
               baggage_included={"cabin": "10 kg"},
               price_per_adult=129, price_per_child=109, price_per_infant=25,
               cancellation_policy="Non remboursable - avoir valable 12 mois",
               modification_policy="Modification payante (35 EUR + difference tarifaire)",
               available_seats=15, valid_from=date(2026, 11, 1), valid_until=date(2027, 3, 31)),

        Flight(agency_id=agency.id, destination_id=marrakech.id,
               airline="Air France", flight_number="AF1478",
               departure_city="Paris", departure_airport="CDG",
               departure_time="19:00", arrival_city="Marrakech", arrival_airport="RAK",
               arrival_time="21:30", duration_minutes=210, stops=0,
               baggage_included={"cabin": "12 kg", "checked": "23 kg"},
               price_per_adult=249, price_per_child=199, price_per_infant=35,
               cancellation_policy="Annulation gratuite jusqu'a 24h avant le depart",
               modification_policy="Modification gratuite",
               available_seats=28, valid_from=date(2026, 11, 1), valid_until=date(2027, 3, 31)),

        Flight(agency_id=agency.id, destination_id=lisbonne.id,
               airline="TAP Portugal", flight_number="TP435",
               departure_city="Paris", departure_airport="ORY",
               departure_time="07:45", arrival_city="Lisbonne", arrival_airport="LIS",
               arrival_time="09:15", duration_minutes=150, stops=0,
               baggage_included={"cabin": "8 kg", "checked": "23 kg"},
               price_per_adult=159, price_per_child=129, price_per_infant=25,
               cancellation_policy="Annulation gratuite jusqu'a 72h avant le depart",
               modification_policy="Modification possible moyennant 40 EUR",
               available_seats=35, valid_from=date(2026, 11, 1), valid_until=date(2027, 6, 30)),

        Flight(agency_id=agency.id, destination_id=lisbonne.id,
               airline="easyJet", flight_number="U23890",
               departure_city="Paris", departure_airport="CDG",
               departure_time="12:30", arrival_city="Lisbonne", arrival_airport="LIS",
               arrival_time="14:00", duration_minutes=150, stops=0,
               baggage_included={"cabin": "15 kg"},
               price_per_adult=89, price_per_child=79, price_per_infant=20,
               cancellation_policy="Non remboursable",
               modification_policy="Modification payante (45 EUR)",
               available_seats=8, valid_from=date(2026, 11, 1), valid_until=date(2027, 6, 30)),

        Flight(agency_id=agency.id, destination_id=santorin.id,
               airline="Aegean Airlines", flight_number="A3601",
               departure_city="Paris", departure_airport="CDG",
               departure_time="09:00", arrival_city="Santorin", arrival_airport="JTR",
               arrival_time="13:30", duration_minutes=210, stops=1, stop_cities=["Athenes"],
               baggage_included={"cabin": "10 kg", "checked": "23 kg"},
               price_per_adult=219, price_per_child=179, price_per_infant=30,
               cancellation_policy="Annulation gratuite jusqu'a 48h avant",
               modification_policy="Modification moyennant 55 EUR",
               available_seats=22, valid_from=date(2026, 11, 1), valid_until=date(2027, 10, 31)),

        Flight(agency_id=agency.id, destination_id=santorin.id,
               airline="Volotea", flight_number="V71234",
               departure_city="Paris", departure_airport="ORY",
               departure_time="06:30", arrival_city="Santorin", arrival_airport="JTR",
               arrival_time="11:15", duration_minutes=225, stops=0,
               baggage_included={"cabin": "10 kg"},
               price_per_adult=179, price_per_child=149, price_per_infant=25,
               cancellation_policy="Non remboursable - avoir possible",
               modification_policy="Modification payante",
               available_seats=12, valid_from=date(2027, 4, 1), valid_until=date(2027, 10, 31)),

        Flight(agency_id=agency.id, destination_id=dubai.id,
               airline="Emirates", flight_number="EK74",
               departure_city="Paris", departure_airport="CDG",
               departure_time="10:15", arrival_city="Dubai", arrival_airport="DXB",
               arrival_time="19:45", duration_minutes=390, stops=0,
               baggage_included={"cabin": "7 kg", "checked": "30 kg"},
               price_per_adult=399, price_per_child=329, price_per_infant=45,
               cancellation_policy="Annulation gratuite jusqu'a 24h avant",
               modification_policy="Modification gratuite",
               available_seats=50, valid_from=date(2026, 11, 1), valid_until=date(2027, 3, 31)),

        Flight(agency_id=agency.id, destination_id=bali.id,
               airline="Singapore Airlines", flight_number="SQ335",
               departure_city="Paris", departure_airport="CDG",
               departure_time="23:30", arrival_city="Bali", arrival_airport="DPS",
               arrival_time="20:00", duration_minutes=960, stops=1, stop_cities=["Singapour"],
               baggage_included={"cabin": "7 kg", "checked": "30 kg"},
               price_per_adult=649, price_per_child=529, price_per_infant=65,
               cancellation_policy="Annulation gratuite jusqu'a 48h",
               modification_policy="Modification moyennant 100 EUR",
               available_seats=18, valid_from=date(2026, 11, 1), valid_until=date(2027, 9, 30)),
    ]
    db.add_all(flights)
    db.flush()

    # ── Hotels ──

    hotels = [
        Hotel(agency_id=agency.id, destination_id=marrakech.id,
              name="Riad Les Orangers", category=4, city="Marrakech",
              address="12 Derb Sidi Ahmed, Medina",
              description="Riad authentique au coeur de la medina, avec patio et piscine",
              image_url="https://images.unsplash.com/photo-1548018560-c7196a4f5e0b?w=800",
              amenities=["Piscine", "Wifi", "Climatisation", "Restaurant", "Hammam", "Terrasse"],
              meal_plan="petit-dejeuner",
              price_per_night=85, cancellation_policy="Annulation gratuite jusqu'a 7 jours avant"),

        Hotel(agency_id=agency.id, destination_id=marrakech.id,
              name="Atlas Medina & Spa", category=5, city="Marrakech",
              address="Avenue Mohammed V, Gueliz",
              description="Hotel 5 etoiles avec spa, piscine exterieure et vue sur l'Atlas",
              image_url="https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800",
              amenities=["Spa", "Piscine", "Wifi", "Restaurant gastronomique", "Salle de sport", "Bar"],
              meal_plan="demi-pension",
              price_per_night=155, cancellation_policy="Annulation gratuite jusqu'a 48h avant"),

        Hotel(agency_id=agency.id, destination_id=marrakech.id,
              name="Dar Essalam", category=3, city="Marrakech",
              address="Rue Riad Zitoun El Kedim, Medina",
              description="Maison d'hotes charmante avec terrasse panoramique",
              image_url="https://images.unsplash.com/photo-1590073242678-70ee3fc28e8e?w=800",
              amenities=["Wifi", "Climatisation", "Terrasse", "Petit-dejeuner inclus"],
              meal_plan="petit-dejeuner",
              price_per_night=52, cancellation_policy="Non remboursable"),

        Hotel(agency_id=agency.id, destination_id=lisbonne.id,
              name="Hotel Alfama Terrace", category=4, city="Lisbonne",
              address="Rua dos Bacalhoeiros 8, Alfama",
              description="Hotel boutique avec terrasse panoramique sur le Tage",
              image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
              amenities=["Wifi", "Terrasse", "Bar", "Concierge", "Climatisation"],
              meal_plan="petit-dejeuner",
              price_per_night=110, cancellation_policy="Annulation gratuite jusqu'a 72h"),

        Hotel(agency_id=agency.id, destination_id=lisbonne.id,
              name="Lisbon Central Hostel+", category=2, city="Lisbonne",
              address="Rua Augusta 122, Baixa",
              description="Hebergement moderne en plein centre, chambres privees disponibles",
              image_url="https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800",
              amenities=["Wifi", "Cuisine commune", "Terrasse", "Casiers securises"],
              meal_plan="petit-dejeuner",
              price_per_night=45, cancellation_policy="Annulation gratuite jusqu'a 24h"),

        Hotel(agency_id=agency.id, destination_id=santorin.id,
              name="Caldera Sunset Suites", category=5, city="Oia",
              address="Oia Main Street",
              description="Suites avec piscine privee et vue imprenable sur la caldeira",
              image_url="https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800",
              amenities=["Piscine privee", "Wifi", "Vue caldeira", "Jacuzzi", "Concierge"],
              meal_plan="petit-dejeuner",
              price_per_night=280, cancellation_policy="Annulation gratuite jusqu'a 14 jours avant"),

        Hotel(agency_id=agency.id, destination_id=santorin.id,
              name="Fira Blue Rooms", category=3, city="Fira",
              address="Fira Center",
              description="Chambres confortables avec vue mer au centre de Fira",
              image_url="https://images.unsplash.com/photo-1602343168117-bb8ffe3e2e9f?w=800",
              amenities=["Wifi", "Climatisation", "Vue mer", "Terrasse commune"],
              meal_plan="petit-dejeuner",
              price_per_night=95, cancellation_policy="Annulation gratuite jusqu'a 48h"),

        Hotel(agency_id=agency.id, destination_id=dubai.id,
              name="Marina Bay Hotel", category=5, city="Dubai",
              address="Dubai Marina Walk",
              description="Hotel luxueux face a la Marina avec plage privee",
              image_url="https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800",
              amenities=["Plage privee", "Piscine", "Spa", "6 restaurants", "Salle de sport", "Wifi"],
              meal_plan="petit-dejeuner",
              price_per_night=195, cancellation_policy="Annulation gratuite jusqu'a 72h"),

        Hotel(agency_id=agency.id, destination_id=bali.id,
              name="Ubud Rice Terrace Villa", category=4, city="Ubud",
              address="Jalan Raya Tegallalang",
              description="Villa avec vue sur les rizieres, piscine a debordement et spa balinais",
              image_url="https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800",
              amenities=["Piscine a debordement", "Spa", "Wifi", "Restaurant", "Yoga", "Navette"],
              meal_plan="petit-dejeuner",
              price_per_night=75, cancellation_policy="Annulation gratuite jusqu'a 7 jours"),

        Hotel(agency_id=agency.id, destination_id=bali.id,
              name="Seminyak Beach Resort", category=5, city="Seminyak",
              address="Jalan Kayu Aya",
              description="Resort en bord de mer avec acces direct a la plage",
              image_url="https://images.unsplash.com/photo-1573843981267-be1999ff37cd?w=800",
              amenities=["Plage privee", "3 piscines", "Spa", "4 restaurants", "Bar de plage", "Wifi"],
              meal_plan="demi-pension",
              price_per_night=120, cancellation_policy="Annulation gratuite jusqu'a 48h"),
    ]
    db.add_all(hotels)
    db.flush()

    # ── Packages ──

    packages = [
        Package(agency_id=agency.id, flight_id=flights[1].id, hotel_id=hotels[0].id,
                name="Marrakech Essentiel - 7 nuits", description="Vol Transavia + Riad Les Orangers",
                price_per_adult=680, price_per_child=560, discount_percentage=8,
                valid_from=date(2026, 11, 1), valid_until=date(2027, 3, 31)),

        Package(agency_id=agency.id, flight_id=flights[3].id, hotel_id=hotels[3].id,
                name="Lisbonne Decouverte - 5 nuits", description="Vol TAP + Hotel Alfama Terrace",
                price_per_adult=699, price_per_child=580, discount_percentage=5,
                valid_from=date(2026, 11, 1), valid_until=date(2027, 6, 30)),

        Package(agency_id=agency.id, flight_id=flights[5].id, hotel_id=hotels[6].id,
                name="Santorin Romantique - 7 nuits", description="Vol Aegean + Fira Blue Rooms",
                price_per_adult=849, price_per_child=699, discount_percentage=10,
                valid_from=date(2027, 4, 1), valid_until=date(2027, 10, 31)),
    ]
    db.add_all(packages)
    db.commit()

    print(f"Donnees de demonstration creees pour '{agency.name}'")
    print(f"  - {len([marrakech, lisbonne, bali, santorin, dubai])} destinations")
    print(f"  - {len(flights)} vols")
    print(f"  - {len(hotels)} hotels")
    print(f"  - {len(packages)} forfaits")
    print(f"\nComptes de test :")
    print(f"  Admin : admin@demo.com / admin123")
    print(f"  Agent : agent@demo.com / agent123")
