"""Exceções de domínio mapeadas pelo error handler central para HTTP."""


class ValidationError(Exception):
    """Erro de validação de entrada/regra → HTTP 400."""


class UnauthorizedError(Exception):
    """Credenciais inválidas → HTTP 401."""


class ForbiddenError(Exception):
    """Acesso proibido (ex.: usuário inativo) → HTTP 403."""


class NotFoundError(Exception):
    """Recurso não encontrado → HTTP 404."""


class ConflictError(Exception):
    """Conflito de estado (ex.: email duplicado) → HTTP 409."""
