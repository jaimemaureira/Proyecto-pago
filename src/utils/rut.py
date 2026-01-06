import re
from typing import Tuple, Optional

try:
    # WTForms error type (solo si se usa como validador)
    from wtforms.validators import ValidationError
except Exception:  # pragma: no cover
    class ValidationError(Exception):  # fallback por si WTForms no está cargado
        pass


def clean_rut(rut: str) -> Optional[Tuple[str, str]]:
    """
    Normaliza un RUT ingresado y separa cuerpo y dígito verificador.
    Acepta formatos con puntos y guión, mayúsculas/minúsculas.

    Retorna (cuerpo, dv) si es parseable, o None si no.
    """
    if not rut:
        return None

    # Elimina cualquier carácter que no sea dígito o K/k
    cleaned = re.sub(r"[^0-9kK]", "", rut).upper()
    if len(cleaned) < 2:  # al menos 1 dígito de cuerpo + 1 DV
        return None

    body, dv = cleaned[:-1], cleaned[-1]
    if not body.isdigit():
        return None

    # Tamaño típico de cuerpo: 7-8 dígitos; aceptamos [1..8] para flexibilidad
    if not (1 <= len(body) <= 8):
        return None

    if dv not in "0123456789K":
        return None

    return body, dv


def compute_dv(body: str) -> str:
    """
    Calcula el dígito verificador usando el algoritmo módulo 11.
    """
    factors = [2, 3, 4, 5, 6, 7]
    total = 0
    factor_idx = 0

    # Recorre de derecha a izquierda
    for ch in reversed(body):
        total += int(ch) * factors[factor_idx]
        factor_idx = (factor_idx + 1) % len(factors)

    remainder = total % 11
    dv = 11 - remainder
    if dv == 11:
        return "0"
    if dv == 10:
        return "K"
    return str(dv)


def is_valid_rut(rut: str) -> bool:
    """Valida un RUT chileno completo."""
    parsed = clean_rut(rut)
    if not parsed:
        return False

    body, dv = parsed
    return compute_dv(body) == dv


def format_rut(body: str, dv: str) -> str:
    """
    Da formato estándar con puntos para miles y guión antes del DV.
    Ej: "12345678" + "5" -> "12.345.678-5".
    """
    # Agrupa de a 3 desde la derecha
    groups = []
    s = body
    while len(s) > 3:
        groups.append(s[-3:])
        s = s[:-3]
    if s:
        groups.append(s)
    formatted_body = ".".join(reversed(groups))
    return f"{formatted_body}-{dv}"


class RutValidator:
    """
    Validador para WTForms: verifica que el RUT sea válido.
    Uso: rut = StringField("RUT", validators=[DataRequired(), RutValidator()])
    """

    def __init__(self, message: Optional[str] = None, normalize: bool = False):
        self.message = message or "RUT inválido."
        # Si normalize=True, reescribe field.data con formato estándar
        self.normalize = normalize

    def __call__(self, form, field):  # type: ignore[override]
        data = (field.data or "").strip()
        if not is_valid_rut(data):
            raise ValidationError(self.message)

        if self.normalize:
            body, dv = clean_rut(data)  # type: ignore
            if body and dv:
                field.data = format_rut(body, dv)
