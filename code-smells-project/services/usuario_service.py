from services.errors import ValidationError


def validar_criacao(dados):
    """Valida o payload de criação de usuário; retorna (nome, email, senha)."""
    if not dados:
        raise ValidationError("Dados inválidos")

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")

    return nome, email, senha
