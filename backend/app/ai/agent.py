import copy
import json
import re
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from app.models import Agency, Conversation, Message, Destination, Flight, Hotel, Package
from app.ai.providers import get_provider, DemoProvider
from app.ai.prompts import SYSTEM_PROMPT, EXTRACTION_PROMPT
from app.services.catalog_service import (
    search_destinations,
    search_flights,
    search_hotels,
    search_packages,
    verify_availability,
)
from app.services.booking_service import create_booking


STEPS = [
    "greeting",
    "collect_criteria",
    "recommend_destinations",
    "compare_flights",
    "compare_hotels",
    "select_offer",
    "collect_traveler_info",
    "verify_price",
    "show_summary",
    "confirm_booking",
    "booking_complete",
    "escalated",
]


class TravelAgent:
    def __init__(self, db: Session, agency: Agency):
        self.db = db
        self.agency = agency
        self.provider = get_provider()

    async def handle_message(self, session_id: str | None, user_message: str) -> dict:
        if not session_id:
            session_id = str(uuid.uuid4())

        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.session_id == session_id, Conversation.agency_id == self.agency.id)
            .first()
        )

        if not conversation:
            conversation = Conversation(
                agency_id=self.agency.id,
                session_id=session_id,
                status="active",
                travel_project={},
                current_step="greeting",
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

        msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=user_message,
        )
        self.db.add(msg)

        project = copy.deepcopy(conversation.travel_project or {})
        extracted = await self._extract_info(user_message, project)
        project = self._merge_project(project, extracted)
        conversation.travel_project = project
        flag_modified(conversation, "travel_project")

        step = conversation.current_step
        intent = extracted.get("intent", "")

        if self._should_escalate(user_message, intent):
            conversation.current_step = "escalated"
            conversation.needs_human = True
            conversation.escalation_reason = self._get_escalation_reason(user_message, intent)
            response_text = self._escalation_response(conversation.escalation_reason)
            offers = None
            booking = None

        elif isinstance(self.provider, DemoProvider):
            response_text, step, offers, booking = await self._demo_flow(
                conversation, project, user_message, extracted
            )
            conversation.current_step = step
        else:
            response_text, step, offers, booking = await self._llm_flow(
                conversation, project, user_message
            )
            conversation.current_step = step

        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            metadata_={"step": conversation.current_step, "offers": offers},
        )
        self.db.add(assistant_msg)
        conversation.travel_project = project
        flag_modified(conversation, "travel_project")
        conversation.last_message_at = datetime.now(timezone.utc)
        self.db.commit()

        return {
            "message": response_text,
            "session_id": session_id,
            "step": conversation.current_step,
            "travel_project": project,
            "offers": offers,
            "booking": booking,
            "needs_human": conversation.needs_human,
        }

    async def _extract_info(self, message: str, project: dict) -> dict:
        if isinstance(self.provider, DemoProvider):
            return self._demo_extract(message, project)

        prompt = EXTRACTION_PROMPT.format(message=message, travel_project=json.dumps(project, ensure_ascii=False))
        return await self.provider.extract_json(prompt)

    def _demo_extract(self, message: str, project: dict) -> dict:
        msg = message.lower()
        extracted = {}

        budget_match = re.search(r"(\d[\d\s]*)\s*(?:euros?|eur|€)", msg)
        if budget_match:
            extracted["budget"] = float(budget_match.group(1).replace(" ", ""))
            extracted["currency"] = "EUR"

        adults_match = re.search(r"(\d+)\s*(?:adultes?|personnes?|voyageurs?)", msg)
        if adults_match:
            extracted["num_adults"] = int(adults_match.group(1))
        elif any(w in msg for w in ["deux personnes", "en couple", "nous deux"]):
            extracted["num_adults"] = 2

        children_match = re.search(r"(\d+)\s*enfants?", msg)
        if children_match:
            extracted["num_children"] = int(children_match.group(1))

        months = {
            "janvier": "01", "fevrier": "02", "mars": "03", "avril": "04",
            "mai": "05", "juin": "06", "juillet": "07", "aout": "08",
            "septembre": "09", "octobre": "10", "novembre": "11", "decembre": "12",
            "décembre": "12", "février": "02", "août": "08",
        }
        for month_name, month_num in months.items():
            if month_name in msg:
                year = 2027 if int(month_num) <= 6 else 2026
                extracted["departure_date"] = f"{year}-{month_num}-15"
                extracted["flexible_dates"] = True
                break

        date_match = re.search(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})", msg)
        if date_match:
            d, m, y = date_match.groups()
            extracted["departure_date"] = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
            extracted["flexible_dates"] = False

        types_map = {
            "plage": "plage", "soleil": "plage", "mer": "plage", "balnéaire": "plage",
            "culture": "culture", "histoire": "culture", "musée": "culture", "patrimoine": "culture",
            "aventure": "aventure", "sport": "aventure", "randonnée": "aventure", "trek": "aventure",
            "famille": "famille", "enfant": "famille",
            "romantique": "romantique", "lune de miel": "romantique",
        }
        for kw, dtype in types_map.items():
            if kw in msg:
                extracted.setdefault("preferences", []).append(dtype)

        departure_cities = {
            "paris": "Paris", "lyon": "Lyon", "marseille": "Marseille",
            "toulouse": "Toulouse", "nice": "Nice", "bordeaux": "Bordeaux",
            "nantes": "Nantes", "lille": "Lille", "bruxelles": "Bruxelles",
            "cotonou": "Cotonou", "abidjan": "Abidjan", "dakar": "Dakar",
            "casablanca": "Casablanca", "lome": "Lome", "douala": "Douala",
            "nairobi": "Nairobi", "le caire": "Le Caire", "dubai": "Dubai",
            "istanbul": "Istanbul", "londres": "Londres", "new york": "New York",
            "accra": "Accra", "tunis": "Tunis", "addis abeba": "Addis Abeba",
            "johannesburg": "Johannesburg", "lagos": "Lagos",
            "libreville": "Libreville", "kinshasa": "Kinshasa",
            "bamako": "Bamako", "ouagadougou": "Ouagadougou",
            "niamey": "Niamey", "conakry": "Conakry",
        }
        dep_triggers = ["départ", "depart", "partir de", "depuis", "au départ", "au depart", "de retour"]
        has_dep_trigger = any(t in msg for t in dep_triggers)
        needs_dep_city = not project.get("departure_city") and project.get("destination")
        for key, city_name in departure_cities.items():
            if key in msg and (has_dep_trigger or needs_dep_city):
                extracted["departure_city"] = city_name
                break

        dest_names = [d.name.lower() for d in self.db.query(Destination).filter(
            Destination.agency_id == self.agency.id, Destination.is_active == True
        ).all()]
        for dn in dest_names:
            if dn in msg:
                dest = self.db.query(Destination).filter(
                    Destination.agency_id == self.agency.id,
                    Destination.name.ilike(dn),
                ).first()
                if dest:
                    extracted["destination"] = dest.name
                    extracted["selected_destination_id"] = dest.id

        if any(w in msg for w in ["visa", "vaccin", "sécurité", "securite", "passeport", "douane", "santé"]):
            extracted["intent"] = "formalities"
        elif any(w in msg for w in ["annuler", "annulation", "rembourser"]):
            extracted["intent"] = "cancel"
        elif any(w in msg for w in ["modifier", "changer", "modification"]):
            extracted["intent"] = "modify"
        elif any(w in msg for w in ["réserver", "reserver", "confirmer", "je confirme", "c'est bon", "on prend", "je prends"]):
            extracted["intent"] = "book"
        elif any(w in msg for w in ["vol", "vols", "avion", "billet"]):
            extracted["intent"] = "search_flights"
        elif any(w in msg for w in ["hôtel", "hotel", "hébergement", "logement", "chambre"]):
            extracted["intent"] = "search_hotels"
        elif any(w in msg for w in ["forfait", "package", "séjour complet", "tout compris"]):
            extracted["intent"] = "compare"
        elif any(w in msg for w in ["destination", "où aller", "idée", "inspiration", "suggère", "recommand"]):
            extracted["intent"] = "inspiration"
        elif any(w in msg for w in ["groupe", "circuit", "sur mesure", "multi-destination"]):
            extracted["intent"] = "complex"

        if "option 1" in msg or "option a" in msg or "la première" in msg or "le premier" in msg:
            extracted["user_choice"] = 1
        elif "option 2" in msg or "option b" in msg or "la deuxième" in msg or "le deuxième" in msg:
            extracted["user_choice"] = 2
        elif "option 3" in msg or "option c" in msg or "la troisième" in msg:
            extracted["user_choice"] = 3

        airlines = self.db.query(Flight.airline).filter(
            Flight.agency_id == self.agency.id
        ).distinct().all()
        for (airline,) in airlines:
            if airline.lower() in msg:
                extracted["selected_airline"] = airline

        hotel_names = self.db.query(Hotel.name).filter(
            Hotel.agency_id == self.agency.id
        ).all()
        for (hname,) in hotel_names:
            if hname.lower() in msg or any(part.lower() in msg for part in hname.split() if len(part) > 3):
                extracted["selected_hotel_name"] = hname

        return extracted

    def _merge_project(self, project: dict, extracted: dict) -> dict:
        for key, value in extracted.items():
            if value is not None and key != "intent" and key != "user_choice":
                if key == "preferences" and key in project:
                    existing = project[key] if isinstance(project[key], list) else []
                    merged = list(set(existing + value))
                    project[key] = merged
                else:
                    project[key] = value
        return project

    def _should_escalate(self, message: str, intent: str) -> bool:
        if intent in ("formalities", "complex"):
            return True
        msg = message.lower()
        triggers = [
            "visa", "vaccin", "sécurité du pays", "ambassade",
            "groupe de plus de", "circuit sur mesure",
            "mobilité réduite", "fauteuil roulant",
            "mineur non accompagné", "remise", "réduction spéciale",
            "parler à un conseiller", "parler à un humain", "un agent",
        ]
        return any(t in msg for t in triggers)

    def _get_escalation_reason(self, message: str, intent: str) -> str:
        if intent == "formalities":
            return "Question sur les formalites de voyage (visa, sante, securite)"
        if intent == "complex":
            return "Demande de voyage complexe (groupe, circuit, multi-destinations)"
        msg = message.lower()
        if "mobilité" in msg or "fauteuil" in msg:
            return "Besoin particulier necessitant verification aupres des prestataires"
        if "remise" in msg or "réduction" in msg:
            return "Demande de tarif special"
        if "conseiller" in msg or "humain" in msg or "agent" in msg:
            return "Le voyageur souhaite parler a un conseiller"
        return "Situation necessitant l'intervention d'un conseiller"

    def _escalation_response(self, reason: str) -> str:
        if "formalit" in reason.lower():
            return (
                "Pour les questions relatives aux visas, conditions d'entree et exigences sanitaires, "
                "je vous recommande de consulter le site officiel du ministere des Affaires etrangeres "
                "de votre pays. Je transmets egalement votre demande a un conseiller specialise qui "
                "pourra vous accompagner. Il vous contactera dans les plus brefs delais."
            )
        return (
            "Je comprends votre demande. Pour vous offrir le meilleur accompagnement, "
            "je transmets votre dossier a l'un de nos conseillers specialises. "
            "Il prendra contact avec vous tres prochainement avec toutes les informations de notre echange."
        )

    async def _demo_flow(self, conversation, project, message, extracted) -> tuple:
        step = conversation.current_step
        intent = extracted.get("intent", "")
        user_choice = extracted.get("user_choice")
        offers = None
        booking = None

        if step == "greeting":
            has_destination = project.get("destination") or project.get("selected_destination_id")
            has_dates = project.get("departure_date")
            has_travelers = project.get("num_adults")
            has_budget = project.get("budget")

            if has_destination and has_dates and has_travelers:
                return await self._demo_flow_search(conversation, project, extracted)

            if has_destination:
                if not has_dates:
                    return (
                        f"Excellent choix ! Quand souhaitez-vous partir ? "
                        f"Avez-vous des dates precises ou une periode de preference ?",
                        "collect_criteria", None, None,
                    )
                if not has_travelers:
                    return (
                        "Parfait ! Combien de voyageurs seront du voyage ? "
                        "(nombre d'adultes, et d'enfants le cas echeant avec leurs ages)",
                        "collect_criteria", None, None,
                    )

            if has_budget or any(p in (extracted.get("preferences") or []) for p in ["plage", "culture", "aventure", "famille", "romantique"]):
                destinations = search_destinations(
                    self.db, self.agency.id,
                    budget=project.get("budget"),
                    destination_type=(extracted.get("preferences") or [None])[0] if extracted.get("preferences") else None,
                )
                if destinations:
                    offers = self._format_destinations(destinations)
                    text = self._build_destination_recommendation(destinations, project)
                    return text, "recommend_destinations", offers, None

            welcome = self.agency.welcome_message or (
                f"Bonjour ! Je suis {self.agency.agent_name}, votre assistant voyage. "
                f"Je suis la pour vous aider a trouver le sejour ideal.\n\n"
                f"Pour commencer, parlez-moi de votre projet : "
                f"ou aimeriez-vous partir ? Quand ? Avec qui ? Quel est votre budget ?"
            )
            return welcome, "collect_criteria", None, None

        if step == "collect_criteria":
            has_destination = project.get("destination") or project.get("selected_destination_id")
            has_dates = project.get("departure_date")
            has_travelers = project.get("num_adults")

            if not has_destination and not intent:
                if project.get("budget") or project.get("preferences"):
                    destinations = search_destinations(
                        self.db, self.agency.id,
                        budget=project.get("budget"),
                        destination_type=project.get("preferences", [None])[0] if project.get("preferences") else None,
                    )
                    if destinations:
                        offers = self._format_destinations(destinations)
                        text = self._build_destination_recommendation(destinations, project)
                        return text, "recommend_destinations", offers, None

                return (
                    "Pour vous proposer les meilleures offres, j'aurais besoin de quelques precisions. "
                    "Quelle destination vous ferait envie ? Ou si vous hesitez, dites-moi vos envies "
                    "(plage, culture, aventure...) et votre budget, je vous suggererai des destinations.",
                    "collect_criteria", None, None,
                )

            if has_destination and not has_dates:
                return (
                    f"Tres bien ! Quand souhaitez-vous partir "
                    f"{'pour ' + project.get('destination', '') if project.get('destination') else ''} ? "
                    f"Indiquez-moi vos dates ou une periode approximative.",
                    "collect_criteria", None, None,
                )

            if has_destination and has_dates and not has_travelers:
                return (
                    "Combien de personnes voyageront ? "
                    "(nombre d'adultes, et d'enfants avec leurs ages le cas echeant)",
                    "collect_criteria", None, None,
                )

            if has_destination and has_dates and has_travelers:
                if not project.get("departure_city"):
                    return (
                        "De quelle ville souhaitez-vous partir ? "
                        "(Par exemple : Paris, Cotonou, Abidjan, Dakar, Casablanca, Dubai...)",
                        "collect_criteria", None, None,
                    )
                return await self._demo_flow_search(conversation, project, extracted)

            if project.get("budget") or project.get("preferences"):
                destinations = search_destinations(
                    self.db, self.agency.id,
                    budget=project.get("budget"),
                    destination_type=project.get("preferences", [None])[0] if project.get("preferences") else None,
                )
                if destinations:
                    offers = self._format_destinations(destinations)
                    text = self._build_destination_recommendation(destinations, project)
                    return text, "recommend_destinations", offers, None

            return (
                "D'accord ! Pouvez-vous me preciser votre destination ou vos envies de voyage ?",
                "collect_criteria", None, None,
            )

        if step == "recommend_destinations":
            if user_choice or project.get("selected_destination_id"):
                dest_id = project.get("selected_destination_id")
                if user_choice and not dest_id:
                    dests = search_destinations(self.db, self.agency.id, budget=project.get("budget"))
                    if user_choice <= len(dests):
                        dest = dests[user_choice - 1]
                        project["selected_destination_id"] = dest.id
                        project["destination"] = dest.name
                        conversation.travel_project = project

                if not project.get("departure_date"):
                    return (
                        f"Excellent choix ! Quand souhaitez-vous partir pour {project.get('destination', 'cette destination')} ?",
                        "collect_criteria", None, None,
                    )
                if not project.get("num_adults"):
                    return (
                        "Combien de personnes voyageront ?",
                        "collect_criteria", None, None,
                    )
                if not project.get("departure_city"):
                    return (
                        "De quelle ville souhaitez-vous partir ? "
                        "(Par exemple : Paris, Cotonou, Abidjan, Dakar, Casablanca, Dubai...)",
                        "collect_criteria", None, None,
                    )
                return await self._demo_flow_search(conversation, project, extracted)

            return (
                "Quelle destination vous interesse parmi celles proposees ? "
                "Vous pouvez aussi me donner d'autres criteres pour affiner ma recherche.",
                "recommend_destinations", None, None,
            )

        if step in ("compare_flights", "compare_hotels"):
            return await self._demo_flow_search(conversation, project, extracted)

        if step == "select_offer":
            if intent == "book" or user_choice:
                return (
                    "Parfait ! Pour finaliser votre reservation, j'ai besoin des informations de chaque voyageur.\n\n"
                    "Pour le voyageur principal, pouvez-vous me communiquer :\n"
                    "- Nom et prenom (tels qu'ils figurent sur votre document de voyage)\n"
                    "- Date de naissance\n"
                    "- Adresse e-mail\n"
                    "- Numero de telephone",
                    "collect_traveler_info", None, None,
                )
            return (
                "Souhaitez-vous reserver l'une de ces offres ? "
                "Dites-moi laquelle vous interesse ou si vous aimeriez voir d'autres options.",
                "select_offer", None, None,
            )

        if step == "collect_traveler_info":
            names = self._extract_names(message)
            if names or "@" in message or re.search(r"\d{2}[/\-]\d{2}[/\-]\d{4}", message):
                project.setdefault("traveler_info", {})
                if names:
                    project["traveler_info"]["name"] = " ".join(names)
                email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", message)
                if email_match:
                    project["traveler_info"]["email"] = email_match.group()
                    project["contact_email"] = email_match.group()
                phone_match = re.search(r"(?:\+?\d[\d\s\-.]{7,})", message)
                if phone_match:
                    project["traveler_info"]["phone"] = phone_match.group().strip()
                    project["contact_phone"] = phone_match.group().strip()
                dob_match = re.search(r"(\d{2})[/\-](\d{2})[/\-](\d{4})", message)
                if dob_match:
                    d, m, y = dob_match.groups()
                    project["traveler_info"]["date_of_birth"] = f"{y}-{m}-{d}"

                conversation.travel_project = project

                info = project.get("traveler_info", {})
                missing = []
                if not info.get("name"):
                    missing.append("nom et prenom")
                if not info.get("date_of_birth"):
                    missing.append("date de naissance")
                if not info.get("email"):
                    missing.append("adresse e-mail")
                if not info.get("phone"):
                    missing.append("numero de telephone")

                if missing:
                    return (
                        f"Merci ! Il me manque encore : {', '.join(missing)}.",
                        "collect_traveler_info", None, None,
                    )

                summary = self._build_summary(project)
                return summary, "show_summary", None, None

            return (
                "Pour la reservation, j'ai besoin de :\n"
                "- Nom et prenom (comme sur votre document de voyage)\n"
                "- Date de naissance (JJ/MM/AAAA)\n"
                "- E-mail\n"
                "- Telephone",
                "collect_traveler_info", None, None,
            )

        if step == "show_summary":
            if intent == "book" or any(w in message.lower() for w in ["confirme", "oui", "c'est bon", "d'accord", "ok", "valide", "je confirme"]):
                booking_data = self._prepare_booking(project)
                try:
                    booking_obj = create_booking(self.db, self.agency.id, booking_data)
                    booking = {
                        "reference": booking_obj.reference,
                        "status": booking_obj.status,
                        "total_price": booking_obj.total_price,
                    }
                    payment_info = ""
                    if self.agency.payment_link_template:
                        payment_info = f"\n\nPour finaliser le reglement, utilisez ce lien securise : {self.agency.payment_link_template}"

                    return (
                        f"Votre reservation a bien ete enregistree !\n\n"
                        f"**Reference : {booking_obj.reference}**\n"
                        f"**Montant total : {booking_obj.total_price:.2f} {booking_obj.currency}**\n"
                        f"**Statut : En attente de confirmation**\n\n"
                        f"Un conseiller va verifier votre dossier et proceder a l'emission de vos documents de voyage. "
                        f"Vous recevrez une confirmation par e-mail.{payment_info}\n\n"
                        f"Suivez votre reservation a tout moment sur notre page de suivi avec la reference **{booking_obj.reference}**.\n\n"
                        f"*Il s'agit d'une reservation de demonstration.*\n\n"
                        f"Puis-je vous aider pour autre chose ?",
                        "booking_complete", None, booking,
                    )
                except Exception as e:
                    return (
                        f"Un probleme est survenu lors de l'enregistrement : {str(e)}. "
                        f"Souhaitez-vous reessayer ou parler a un conseiller ?",
                        "show_summary", None, None,
                    )
            return (
                "Souhaitez-vous confirmer cette reservation ? "
                "Repondez 'oui' pour confirmer ou dites-moi si vous souhaitez modifier quelque chose.",
                "show_summary", None, None,
            )

        if step == "booking_complete":
            return (
                "Merci pour votre confiance ! Puis-je vous aider pour un autre voyage ?",
                "booking_complete", None, None,
            )

        return (
            "Comment puis-je vous aider ?",
            step, None, None,
        )

    async def _demo_flow_search(self, conversation, project, extracted):
        intent = extracted.get("intent", "")
        dest_id = project.get("selected_destination_id")

        if not dest_id and project.get("destination"):
            dest = self.db.query(Destination).filter(
                Destination.agency_id == self.agency.id,
                Destination.name.ilike(f"%{project['destination']}%"),
            ).first()
            if dest:
                dest_id = dest.id
                project["selected_destination_id"] = dest_id

        if not dest_id:
            destinations = search_destinations(
                self.db, self.agency.id,
                budget=project.get("budget"),
            )
            if destinations:
                offers = self._format_destinations(destinations)
                text = self._build_destination_recommendation(destinations, project)
                return text, "recommend_destinations", offers, None
            return (
                "Je n'ai malheureusement pas de destination correspondant a vos criteres dans notre catalogue. "
                "Souhaitez-vous ajuster votre budget ou vos preferences ?",
                "collect_criteria", None, None,
            )

        user_choice = extracted.get("user_choice")

        selected_airline = extracted.get("selected_airline")
        selected_hotel_name = extracted.get("selected_hotel_name")

        dep_city = project.get("departure_city")

        flight_selected = user_choice or selected_airline
        if intent == "search_hotels" or (conversation.current_step == "compare_flights" and flight_selected):
            if conversation.current_step == "compare_flights":
                flights = search_flights(self.db, self.agency.id, destination_id=dest_id, departure_city=dep_city)
                if selected_airline:
                    for f in flights:
                        if f.airline.lower() == selected_airline.lower():
                            project["selected_flight_id"] = f.id
                            break
                elif user_choice and user_choice <= len(flights):
                    project["selected_flight_id"] = flights[user_choice - 1].id

            hotels = search_hotels(self.db, self.agency.id, destination_id=dest_id)
            if hotels:
                offers = self._format_hotels(hotels, project)
                text = self._build_hotel_comparison(hotels, project)
                return text, "compare_hotels", offers, None
            return (
                "Aucun hotel disponible pour cette destination. Souhaitez-vous essayer une autre destination ?",
                "collect_criteria", None, None,
            )

        hotel_selected = user_choice or selected_hotel_name
        if conversation.current_step == "compare_hotels" and hotel_selected:
            hotels = search_hotels(self.db, self.agency.id, destination_id=dest_id)
            if selected_hotel_name:
                for h in hotels:
                    if h.name.lower() == selected_hotel_name.lower() or selected_hotel_name.lower() in h.name.lower():
                        project["selected_hotel_id"] = h.id
                        break
            elif user_choice and user_choice <= len(hotels):
                project["selected_hotel_id"] = hotels[user_choice - 1].id
            conversation.travel_project = project

            avail = verify_availability(
                self.db, self.agency.id,
                flight_id=project.get("selected_flight_id"),
                hotel_id=project.get("selected_hotel_id"),
            )
            if not avail["available"]:
                return (
                    "Desole, cette offre n'est plus disponible. Souhaitez-vous voir d'autres options ?",
                    "compare_hotels", None, None,
                )

            summary = self._build_summary(project)
            if not project.get("traveler_info", {}).get("name"):
                return (
                    f"{summary}\n\nPour finaliser, j'ai besoin de vos informations :\n"
                    "- Nom et prenom (comme sur votre document de voyage)\n"
                    "- Date de naissance\n"
                    "- E-mail\n"
                    "- Telephone",
                    "collect_traveler_info", None, None,
                )
            return summary, "show_summary", None, None

        flights = search_flights(self.db, self.agency.id, destination_id=dest_id, departure_city=dep_city)
        if flights:
            offers = self._format_flights(flights, project)
            text = self._build_flight_comparison(flights, project)
            return text, "compare_flights", offers, None

        if dep_city:
            flights_any = search_flights(self.db, self.agency.id, destination_id=dest_id)
            if flights_any:
                dep_cities = list({f.departure_city for f in flights_any})
                return (
                    f"Aucun vol direct depuis {dep_city} pour cette destination. "
                    f"Des vols sont disponibles au depart de : {', '.join(dep_cities)}. "
                    f"Souhaitez-vous partir d'une de ces villes ?",
                    "collect_criteria", None, None,
                )

        return (
            "Aucun vol disponible pour cette destination. Souhaitez-vous essayer une autre destination ?",
            "collect_criteria", None, None,
        )

    async def _llm_flow(self, conversation, project, message):
        system = SYSTEM_PROMPT.format(
            agent_name=self.agency.agent_name,
            agency_name=self.agency.name,
            travel_project=json.dumps(project, ensure_ascii=False, indent=2),
            agent_instructions=self.agency.agent_instructions or "",
        )

        messages = []
        for m in conversation.messages[-20:]:
            messages.append({"role": m.role, "content": m.content})

        dest_id = project.get("selected_destination_id")
        catalog_context = ""
        if dest_id:
            flights = search_flights(self.db, self.agency.id, destination_id=dest_id, limit=3)
            hotels = search_hotels(self.db, self.agency.id, destination_id=dest_id, limit=3)
            if flights:
                catalog_context += "\nVOLS DISPONIBLES :\n"
                for f in flights:
                    catalog_context += (
                        f"- {f.airline} {f.flight_number}: {f.departure_city} ({f.departure_airport}) {f.departure_time} -> "
                        f"{f.arrival_city} ({f.arrival_airport}) {f.arrival_time}, "
                        f"{f.duration_minutes}min, {f.stops} escale(s), {f.price_per_adult}EUR/adulte, "
                        f"bagages: {json.dumps(f.baggage_included)}\n"
                    )
            if hotels:
                catalog_context += "\nHOTELS DISPONIBLES :\n"
                for h in hotels:
                    catalog_context += (
                        f"- {h.name} {'*' * h.category}: {h.city}, {h.price_per_night}EUR/nuit, "
                        f"{h.meal_plan}, equipements: {', '.join(h.amenities or [])}\n"
                    )
        else:
            destinations = search_destinations(self.db, self.agency.id, budget=project.get("budget"), limit=3)
            if destinations:
                catalog_context += "\nDESTINATIONS CATALOGUE :\n"
                for d in destinations:
                    min_flight = self.db.query(Flight).filter(
                        Flight.destination_id == d.id, Flight.agency_id == self.agency.id
                    ).order_by(Flight.price_per_adult).first()
                    price_info = f", vol a partir de {min_flight.price_per_adult}EUR" if min_flight else ""
                    catalog_context += f"- {d.name} ({d.country}): {d.description[:100]}{price_info}\n"

        if catalog_context:
            messages.append({"role": "system", "content": f"CATALOGUE DISPONIBLE :{catalog_context}"})

        response = await self.provider.generate(system, messages)
        return response, conversation.current_step, None, None

    def _format_destinations(self, destinations):
        return [
            {
                "type": "destination",
                "id": d.id,
                "name": d.name,
                "country": d.country,
                "description": d.description,
                "image_url": d.image_url,
                "highlights": d.highlights or [],
                "best_season": d.best_season,
                "destination_type": d.destination_type,
            }
            for d in destinations
        ]

    def _format_flights(self, flights, project):
        num_adults = project.get("num_adults", 1)
        num_children = project.get("num_children", 0)
        return [
            {
                "type": "flight",
                "id": f.id,
                "airline": f.airline,
                "flight_number": f.flight_number,
                "departure": f"{f.departure_city} ({f.departure_airport})",
                "arrival": f"{f.arrival_city} ({f.arrival_airport})",
                "departure_time": f.departure_time,
                "arrival_time": f.arrival_time,
                "duration_minutes": f.duration_minutes,
                "stops": f.stops,
                "baggage": f.baggage_included,
                "price_per_adult": f.price_per_adult,
                "total_price": f.price_per_adult * num_adults + f.price_per_child * num_children,
                "currency": f.currency,
                "cancellation": f.cancellation_policy,
                "modification": f.modification_policy,
                "seats": f.available_seats,
            }
            for f in flights
        ]

    def _format_hotels(self, hotels, project):
        nights = 7
        if project.get("departure_date") and project.get("return_date"):
            from datetime import date
            try:
                d1 = date.fromisoformat(project["departure_date"])
                d2 = date.fromisoformat(project["return_date"])
                nights = (d2 - d1).days
            except (ValueError, TypeError):
                pass

        return [
            {
                "type": "hotel",
                "id": h.id,
                "name": h.name,
                "category": h.category,
                "city": h.city,
                "description": h.description,
                "image_url": h.image_url,
                "amenities": h.amenities or [],
                "meal_plan": h.meal_plan,
                "price_per_night": h.price_per_night,
                "total_price": h.price_per_night * nights,
                "nights": nights,
                "currency": h.currency,
                "cancellation": h.cancellation_policy,
            }
            for h in hotels
        ]

    def _build_destination_recommendation(self, destinations, project):
        budget_text = f" pour un budget de {project['budget']:.0f} {project.get('currency', 'EUR')}" if project.get("budget") else ""
        text = f"Voici les destinations que je vous recommande depuis notre catalogue{budget_text} :\n\n"
        for i, d in enumerate(destinations, 1):
            min_flight = self.db.query(Flight).filter(
                Flight.destination_id == d.id, Flight.agency_id == self.agency.id, Flight.is_available == True
            ).order_by(Flight.price_per_adult).first()
            price_info = f" (vol a partir de {min_flight.price_per_adult:.0f} EUR/pers.)" if min_flight else ""
            highlights = ", ".join(d.highlights[:3]) if d.highlights else ""
            text += f"**Option {i} : {d.name}, {d.country}**{price_info}\n"
            text += f"{d.description[:200]}\n"
            if highlights:
                text += f"Points forts : {highlights}\n"
            if d.best_season:
                text += f"Meilleure saison : {d.best_season}\n"
            text += "\n"
        text += "Quelle destination vous interesse ? Ou souhaitez-vous ajuster vos criteres ?"
        return text

    def _build_flight_comparison(self, flights, project):
        num_adults = project.get("num_adults", 1)
        num_children = project.get("num_children", 0)
        dest_name = project.get("destination", "votre destination")
        text = f"Voici les vols disponibles pour {dest_name} dans notre catalogue :\n\n"
        for i, f in enumerate(flights, 1):
            total = f.price_per_adult * num_adults + f.price_per_child * num_children
            duration_h = f.duration_minutes // 60
            duration_m = f.duration_minutes % 60
            stops_text = "direct" if f.stops == 0 else f"{f.stops} escale(s)"
            baggage = f.baggage_included or {}
            bag_text = f"cabine {baggage.get('cabin', 'inclus')}"
            if baggage.get("checked"):
                bag_text += f" + soute {baggage['checked']}"
            text += (
                f"**Option {i} : {f.airline}** ({f.flight_number})\n"
                f"  Depart : {f.departure_city} ({f.departure_airport}) a {f.departure_time}\n"
                f"  Arrivee : {f.arrival_city} ({f.arrival_airport}) a {f.arrival_time}\n"
                f"  Duree : {duration_h}h{duration_m:02d} | {stops_text}\n"
                f"  Bagages : {bag_text}\n"
                f"  **Prix total ({num_adults} adulte(s){f', {num_children} enfant(s)' if num_children else ''}) : {total:.2f} EUR**\n"
                f"  Annulation : {f.cancellation_policy or 'Selon conditions'}\n\n"
            )
        text += f"_Prix verifies le {datetime.now(timezone.utc).strftime('%d/%m/%Y a %H:%M')} UTC._\n"
        text += "_Comparaison portant sur les offres du catalogue de l'agence._\n\n"
        text += "Quel vol vous convient ? Ensuite je vous montrerai les hotels disponibles."
        return text

    def _build_hotel_comparison(self, hotels, project):
        nights = 7
        if project.get("departure_date") and project.get("return_date"):
            from datetime import date
            try:
                d1 = date.fromisoformat(project["departure_date"])
                d2 = date.fromisoformat(project["return_date"])
                nights = (d2 - d1).days
            except (ValueError, TypeError):
                pass

        text = f"Voici les hotels disponibles :\n\n"
        for i, h in enumerate(hotels, 1):
            total = h.price_per_night * nights
            stars = h.category * " etoile" if h.category else ""
            amenities = ", ".join((h.amenities or [])[:5])
            text += (
                f"**Option {i} : {h.name}** {'*' * h.category}\n"
                f"  {h.city} | {h.meal_plan.replace('-', ' ').capitalize()}\n"
                f"  Equipements : {amenities}\n"
                f"  **Prix total ({nights} nuits) : {total:.2f} EUR**\n"
                f"  ({h.price_per_night:.2f} EUR/nuit)\n"
                f"  Annulation : {h.cancellation_policy or 'Selon conditions'}\n\n"
            )
        text += f"_Prix verifies le {datetime.now(timezone.utc).strftime('%d/%m/%Y a %H:%M')} UTC._\n"
        text += "_Comparaison portant sur les offres du catalogue de l'agence._\n\n"
        text += "Quel hotel vous interesse ?"
        return text

    def _build_summary(self, project):
        flight = None
        hotel = None
        if project.get("selected_flight_id"):
            flight = self.db.query(Flight).filter(Flight.id == project["selected_flight_id"]).first()
        if project.get("selected_hotel_id"):
            hotel = self.db.query(Hotel).filter(Hotel.id == project["selected_hotel_id"]).first()

        num_adults = project.get("num_adults", 1)
        num_children = project.get("num_children", 0)
        nights = 7

        total = 0
        text = "**RECAPITULATIF DE VOTRE RESERVATION**\n\n"
        text += f"Destination : {project.get('destination', 'N/A')}\n"
        text += f"Voyageurs : {num_adults} adulte(s)"
        if num_children:
            text += f", {num_children} enfant(s)"
        text += "\n"

        if project.get("departure_date"):
            text += f"Dates : {project['departure_date']}"
            if project.get("return_date"):
                text += f" au {project['return_date']}"
            text += "\n"

        if flight:
            flight_total = flight.price_per_adult * num_adults + flight.price_per_child * num_children
            total += flight_total
            text += (
                f"\n**Vol** : {flight.airline} {flight.flight_number}\n"
                f"  {flight.departure_city} ({flight.departure_time}) -> {flight.arrival_city} ({flight.arrival_time})\n"
                f"  Prix : {flight_total:.2f} EUR\n"
            )

        if hotel:
            hotel_total = hotel.price_per_night * nights
            total += hotel_total
            text += (
                f"\n**Hotel** : {hotel.name} {'*' * hotel.category}\n"
                f"  {hotel.city} | {hotel.meal_plan}\n"
                f"  {nights} nuits : {hotel_total:.2f} EUR\n"
            )

        if project.get("traveler_info"):
            info = project["traveler_info"]
            text += f"\n**Voyageur principal** : {info.get('name', 'N/A')}\n"
            if info.get("date_of_birth"):
                text += f"  Date de naissance : {info['date_of_birth']}\n"
            if info.get("email"):
                text += f"  E-mail : {info['email']}\n"

        text += f"\n**PRIX TOTAL : {total:.2f} EUR**\n"
        text += f"_Prix verifie le {datetime.now(timezone.utc).strftime('%d/%m/%Y a %H:%M')} UTC._\n\n"
        text += "Confirmez-vous cette reservation ? (repondez 'oui' pour confirmer)"

        project["computed_total"] = total
        return text

    def _prepare_booking(self, project):
        num_adults = project.get("num_adults", 1)
        num_children = project.get("num_children", 0)
        total = project.get("computed_total", 0)

        if total == 0:
            flight = None
            hotel = None
            nights = 7
            if project.get("selected_flight_id"):
                flight = self.db.query(Flight).filter(Flight.id == project["selected_flight_id"]).first()
            if project.get("selected_hotel_id"):
                hotel = self.db.query(Hotel).filter(Hotel.id == project["selected_hotel_id"]).first()
            if flight:
                total += flight.price_per_adult * num_adults + flight.price_per_child * num_children
            if hotel:
                total += hotel.price_per_night * nights

        info = project.get("traveler_info", {})
        traveler_details = [{"name": info.get("name", ""), "date_of_birth": info.get("date_of_birth", "")}]

        dep_date = None
        ret_date = None
        if project.get("departure_date"):
            try:
                from datetime import date
                dep_date = date.fromisoformat(project["departure_date"])
                if project.get("return_date"):
                    ret_date = date.fromisoformat(project["return_date"])
                else:
                    from datetime import timedelta
                    ret_date = dep_date + timedelta(days=7)
            except (ValueError, TypeError):
                pass

        return {
            "flight_id": project.get("selected_flight_id"),
            "hotel_id": project.get("selected_hotel_id"),
            "departure_date": dep_date,
            "return_date": ret_date,
            "check_in_date": dep_date,
            "check_out_date": ret_date,
            "num_adults": num_adults,
            "num_children": num_children,
            "num_infants": project.get("num_infants", 0),
            "traveler_details": traveler_details,
            "contact_email": project.get("contact_email", info.get("email", "")),
            "contact_phone": project.get("contact_phone", info.get("phone", "")),
            "special_requests": "",
            "total_price": total,
            "currency": project.get("currency", "EUR"),
        }

    def _extract_names(self, message):
        words = message.strip().split()
        names = []
        for w in words:
            clean = re.sub(r"[^a-zA-ZÀ-ÿ\-']", "", w)
            if clean and len(clean) >= 2 and clean[0].isupper():
                names.append(clean)
        return names if len(names) >= 2 else []
