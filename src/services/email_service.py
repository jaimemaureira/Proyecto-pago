from flask_mail import Message
from src.extensions import mail

def send_set_password_email(to_email: str, nombre: str, link: str) -> None:
    subject = "Crea tu contraseña - Proyecto Pago"
    body = f"""Hola {nombre},

Para crear tu contraseña y activar tu acceso, entra aquí:

{link}

Este enlace expira pronto por seguridad.
Si no solicitaste esto, ignora este correo.

Saludos,
Proyecto Pago
"""
    msg = Message(subject=subject, recipients=[to_email], body=body)
    mail.send(msg)
