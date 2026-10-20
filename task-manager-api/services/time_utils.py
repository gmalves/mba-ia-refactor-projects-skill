"""Utilitários de data/hora.

Substitui a API deprecated ``datetime.utcnow()``. O valor retornado é UTC
naive para manter a compatibilidade com o armazenamento e a serialização
existentes (sem offset ``+00:00`` nas respostas).
"""
from datetime import datetime, timezone


def utcnow():
    """Instante UTC atual como datetime naive (compatível com o storage legado)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
