from models import pedido_model, produto_model, usuario_model
from services import notificacao_service
from services.errors import ValidationError


def criar(dados):
    """Valida e cria um pedido, orquestrando regras de negócio e notificações."""
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not itens or len(itens) == 0:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    if usuario_model.get_por_id(usuario_id) is None:
        raise ValidationError("Usuário não encontrado")

    itens_preparados = []
    for item in itens:
        produto_id = item.get("produto_id")
        quantidade = item.get("quantidade")

        if not produto_id:
            raise ValidationError("Produto ID é obrigatório")
        if isinstance(quantidade, bool) or not isinstance(quantidade, (int, float)):
            raise ValidationError("Quantidade inválida")
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValidationError("Quantidade deve ser positiva")

        produto = produto_model.get_por_id(produto_id)
        if produto is None:
            raise ValidationError("Produto " + str(produto_id) + " não encontrado")
        if produto["estoque"] < quantidade:
            raise ValidationError("Estoque insuficiente para " + produto["nome"])

        itens_preparados.append({
            "produto_id": produto_id,
            "quantidade": quantidade,
            "preco_unitario": produto["preco"],
        })

    resultado = pedido_model.criar(usuario_id, itens_preparados)
    notificacao_service.pedido_criado(resultado["pedido_id"], usuario_id)
    return resultado
