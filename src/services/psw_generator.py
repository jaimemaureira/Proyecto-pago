import secrets
import string

def generate_password(length: int = 16) -> str:
    password = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(secrets.choice(password) for _ in range(length))