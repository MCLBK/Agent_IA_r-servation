import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from app.config import get_settings

logger = logging.getLogger(__name__)


def _get_frontend_url():
    settings = get_settings()
    return getattr(settings, "FRONTEND_URL", "https://agent-ia-r-servation.vercel.app")


def _build_booking_html(booking, flight, hotel, agency) -> str:
    dep_date = booking.departure_date.strftime("%d/%m/%Y") if booking.departure_date else "-"
    ret_date = booking.return_date.strftime("%d/%m/%Y") if booking.return_date else "-"
    created = booking.created_at.strftime("%d/%m/%Y a %Hh%M") if booking.created_at else "-"
    tracking_url = f"{_get_frontend_url()}/tracking?ref={booking.reference}"

    flight_html = ""
    if flight:
        duration_h = flight.duration_minutes // 60
        duration_m = flight.duration_minutes % 60
        stops = "Direct" if flight.stops == 0 else f"{flight.stops} escale(s)"
        flight_html = f"""
        <tr>
            <td style="padding:16px;background:#f8fafc;border-radius:8px;">
                <h3 style="margin:0 0 8px;color:#1B3A5C;font-size:16px;">Vol {flight.airline} ({flight.flight_number})</h3>
                <p style="margin:4px 0;color:#475569;font-size:14px;">
                    {flight.departure_city} ({flight.departure_airport}) &rarr; {flight.arrival_city} ({flight.arrival_airport})
                </p>
                <p style="margin:4px 0;color:#475569;font-size:14px;">
                    Depart : {flight.departure_time} | Arrivee : {flight.arrival_time} | Duree : {duration_h}h{duration_m:02d} | {stops}
                </p>
            </td>
        </tr>
        <tr><td style="height:12px;"></td></tr>
        """

    hotel_html = ""
    if hotel:
        stars = "★" * hotel.category
        hotel_html = f"""
        <tr>
            <td style="padding:16px;background:#f8fafc;border-radius:8px;">
                <h3 style="margin:0 0 8px;color:#1B3A5C;font-size:16px;">{hotel.name} {stars}</h3>
                <p style="margin:4px 0;color:#475569;font-size:14px;">{hotel.city} · {hotel.meal_plan}</p>
                <p style="margin:4px 0;color:#475569;font-size:14px;">{hotel.price_per_night:.0f} EUR / nuit</p>
            </td>
        </tr>
        <tr><td style="height:12px;"></td></tr>
        """

    payment_html = ""
    if agency.payment_link_template:
        link = agency.payment_link_template.replace("{reference}", booking.reference)
        payment_html = f"""
        <tr>
            <td style="padding:20px;text-align:center;">
                <a href="{link}"
                   style="display:inline-block;background:#C9A84C;color:#ffffff;font-weight:600;
                          text-decoration:none;padding:14px 32px;border-radius:8px;font-size:15px;">
                    Proceder au paiement
                </a>
            </td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
    <body style="margin:0;padding:0;font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:#f1f5f9;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;background:#ffffff;">
            <!-- Header -->
            <tr>
                <td style="background:#1B3A5C;padding:32px 24px;text-align:center;">
                    <h1 style="margin:0;color:#C9A84C;font-size:24px;font-weight:700;">{agency.name}</h1>
                    <p style="margin:8px 0 0;color:#94a3b8;font-size:13px;">Confirmation de reservation</p>
                </td>
            </tr>

            <!-- Reference -->
            <tr>
                <td style="padding:28px 24px 8px;">
                    <table width="100%" cellpadding="0" cellspacing="0" style="background:#eff6ff;border-radius:8px;">
                        <tr>
                            <td style="padding:20px;text-align:center;">
                                <p style="margin:0 0 4px;color:#475569;font-size:13px;">Reference de reservation</p>
                                <p style="margin:0;color:#1B3A5C;font-size:28px;font-weight:700;letter-spacing:2px;">{booking.reference}</p>
                                <p style="margin:8px 0 0;color:#64748b;font-size:13px;">Enregistree le {created}</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- Details -->
            <tr>
                <td style="padding:20px 24px 8px;">
                    <h2 style="margin:0 0 16px;color:#1B3A5C;font-size:18px;">Details du voyage</h2>
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding:6px 0;color:#475569;font-size:14px;width:50%;">Dates :</td>
                            <td style="padding:6px 0;color:#1e293b;font-size:14px;font-weight:600;">{dep_date} au {ret_date}</td>
                        </tr>
                        <tr>
                            <td style="padding:6px 0;color:#475569;font-size:14px;">Voyageurs :</td>
                            <td style="padding:6px 0;color:#1e293b;font-size:14px;font-weight:600;">
                                {booking.num_adults} adulte(s)
                                {f", {booking.num_children} enfant(s)" if booking.num_children else ""}
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:6px 0;color:#475569;font-size:14px;">Statut :</td>
                            <td style="padding:6px 0;font-size:14px;">
                                <span style="background:#fef3c7;color:#92400e;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">
                                    En attente de confirmation
                                </span>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- Flight -->
            <tr>
                <td style="padding:16px 24px 0;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                        {flight_html}
                        {hotel_html}
                    </table>
                </td>
            </tr>

            <!-- Total -->
            <tr>
                <td style="padding:16px 24px;">
                    <table width="100%" cellpadding="0" cellspacing="0"
                           style="background:#1B3A5C;border-radius:8px;">
                        <tr>
                            <td style="padding:20px;text-align:center;">
                                <p style="margin:0 0 4px;color:#94a3b8;font-size:13px;">Montant total</p>
                                <p style="margin:0;color:#C9A84C;font-size:32px;font-weight:700;">
                                    {booking.total_price:.2f} {booking.currency}
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            {payment_html}

            <!-- Tracking -->
            <tr>
                <td style="padding:16px 24px 8px;text-align:center;">
                    <a href="{tracking_url}"
                       style="display:inline-block;background:#1B3A5C;color:#ffffff;font-weight:600;
                              text-decoration:none;padding:12px 28px;border-radius:8px;font-size:14px;">
                        Suivre ma reservation
                    </a>
                </td>
            </tr>
            <tr>
                <td style="padding:8px 24px 24px;text-align:center;">
                    <p style="color:#64748b;font-size:12px;">
                        Ou utilisez la reference <strong>{booking.reference}</strong> sur notre page de suivi.
                    </p>
                </td>
            </tr>

            <!-- Footer -->
            <tr>
                <td style="background:#f8fafc;padding:20px 24px;border-top:1px solid #e2e8f0;">
                    <p style="margin:0;color:#94a3b8;font-size:11px;text-align:center;">
                        {agency.name} · Ceci est un email automatique de confirmation.
                        <br>Pour toute question, contactez {agency.escalation_email or "votre conseiller"}.
                        <br><em>Reservation de demonstration.</em>
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def _build_booking_text(booking, flight, hotel, agency) -> str:
    dep_date = booking.departure_date.strftime("%d/%m/%Y") if booking.departure_date else "-"
    ret_date = booking.return_date.strftime("%d/%m/%Y") if booking.return_date else "-"

    lines = [
        f"{agency.name} - Confirmation de reservation",
        f"{'=' * 50}",
        f"",
        f"Reference : {booking.reference}",
        f"Statut : En attente de confirmation",
        f"Dates : {dep_date} au {ret_date}",
        f"Voyageurs : {booking.num_adults} adulte(s)"
        + (f", {booking.num_children} enfant(s)" if booking.num_children else ""),
        f"",
    ]

    if flight:
        lines += [
            f"--- Vol ---",
            f"{flight.airline} ({flight.flight_number})",
            f"{flight.departure_city} ({flight.departure_airport}) {flight.departure_time}"
            f" -> {flight.arrival_city} ({flight.arrival_airport}) {flight.arrival_time}",
            f"",
        ]

    if hotel:
        lines += [
            f"--- Hotel ---",
            f"{hotel.name} {'*' * hotel.category}",
            f"{hotel.city} · {hotel.meal_plan}",
            f"{hotel.price_per_night:.0f} EUR / nuit",
            f"",
        ]

    tracking_url = f"{_get_frontend_url()}/tracking?ref={booking.reference}"
    lines += [
        f"--- Total ---",
        f"{booking.total_price:.2f} {booking.currency}",
        f"",
        f"Suivez votre reservation : {tracking_url}",
        f"Reference : {booking.reference}",
        f"",
        f"Reservation de demonstration.",
    ]
    return "\n".join(lines)


def send_booking_confirmation(booking, flight, hotel, agency):
    if not booking.contact_email:
        logger.info("No contact email for booking %s — skipping email", booking.reference)
        return False

    settings = get_settings()
    smtp_host = getattr(settings, "SMTP_HOST", "")
    smtp_user = getattr(settings, "SMTP_USER", "")
    smtp_password = getattr(settings, "SMTP_PASSWORD", "")

    if not smtp_host or not smtp_user:
        logger.info(
            "SMTP not configured — booking %s confirmation email skipped. "
            "Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD to enable.",
            booking.reference,
        )
        return False

    smtp_port = int(getattr(settings, "SMTP_PORT", 587))
    from_name = getattr(settings, "SMTP_FROM_NAME", agency.name)
    from_email = getattr(settings, "SMTP_FROM_EMAIL", smtp_user)

    subject = f"Confirmation de reservation {booking.reference} — {agency.name}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = booking.contact_email
    msg["Reply-To"] = agency.escalation_email or from_email

    text_body = _build_booking_text(booking, flight, hotel, agency)
    html_body = _build_booking_html(booking, flight, hotel, agency)

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info("Booking confirmation email sent to %s for %s", booking.contact_email, booking.reference)
        return True
    except Exception as e:
        logger.error("Failed to send booking email for %s: %s", booking.reference, e)
        return False
