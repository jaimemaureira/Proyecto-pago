from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app

def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(
        secret_key=current_app.config["SECRET_KEY"],
        salt=current_app.config.get("SECURITY_PASSWORD_SALT", "pwd-reset-salt"),
    )

def make_reset_token(persona_id, reset_nonce) -> str:
    s = _serializer()
    payload = {"pid": str(persona_id), "nonce": str(reset_nonce)}
    return s.dumps(payload)

def verify_reset_token(token: str, max_age_seconds: int = 1800) -> dict | None:
    s = _serializer()
    try:
        return s.loads(token, max_age=max_age_seconds)
    except (SignatureExpired, BadSignature):
        return None