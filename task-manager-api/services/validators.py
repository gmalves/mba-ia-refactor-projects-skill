"""Validação central de entrada (constantes + regras reutilizadas pelos services)."""
import re
from datetime import datetime

from services.errors import ValidationError

VALID_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_ROLES = ["user", "admin", "manager"]

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200
MIN_PASSWORD_LENGTH = 4
MIN_PRIORITY = 1
MAX_PRIORITY = 5

DEFAULT_PRIORITY = 3
DEFAULT_COLOR = "#000000"

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")


def validate_title_required(title):
    """Valida título na criação (presença obrigatória + tamanho)."""
    if not title:
        raise ValidationError("Título é obrigatório")
    validate_title_length(title)


def validate_title_length(title):
    """Valida apenas o tamanho do título (usado na atualização)."""
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError("Título muito curto")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError("Título muito longo")


def validate_status(status):
    if status not in VALID_STATUSES:
        raise ValidationError("Status inválido")


def validate_priority(priority):
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ValidationError("Prioridade deve ser entre 1 e 5")


def validate_role(role):
    if role not in VALID_ROLES:
        raise ValidationError("Role inválido")


def validate_email_format(email):
    if not EMAIL_PATTERN.match(email):
        raise ValidationError("Email inválido")


def parse_priority(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError("Prioridade inválida")


def parse_due_date(value):
    """Converte 'YYYY-MM-DD' em datetime; ``None``/vazio vira ``None``."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError):
        raise ValidationError("Formato de data inválido. Use YYYY-MM-DD")
