from werkzeug.security import generate_password_hash
import secrets, string

def generate_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(secrets.choice(alphabet) for _ in range(length))

plain_password = generate_password(16)
print("Generated:", plain_password)
print("Hash:", generate_password_hash(plain_password))