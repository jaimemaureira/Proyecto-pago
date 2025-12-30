import os
from typing import Optional

# Integración opcional con Twilio
# Configurar variables de entorno:
# TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER

def _twilio_client():
    try:
        from twilio.rest import Client  # type: ignore
    except Exception:
        return None
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    if not sid or not token:
        return None
    try:
        return Client(sid, token)
    except Exception:
        return None


def send_sms(phone_e164: str, message: str) -> bool:
    """Envía un SMS. Si Twilio no está configurado, hace fallback a consola.

    Args:
        phone_e164: Número en formato +56XXXXXXXXX (o E.164)
        message: Texto del SMS
    Returns:
        True si se envió (o simulado), False si falló.
    """
    client = _twilio_client()
    from_number = os.getenv("TWILIO_FROM_NUMBER")

    if client and from_number:
        try:
            client.messages.create(to=phone_e164, from_=from_number, body=message)
            return True
        except Exception:
            return False

    # Fallback: sin Twilio, solo log a consola
    print(f"[SMS FAKE] to={phone_e164} msg={message}")
    return True
