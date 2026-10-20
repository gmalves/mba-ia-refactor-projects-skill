class ValidationError(Exception):
    """Erro de validação de regra de negócio (mapeado para HTTP 400)."""

    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(mensagem)
