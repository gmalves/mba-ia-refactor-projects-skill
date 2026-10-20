from services.errors import ValidationError

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
CATEGORIA_PADRAO = "geral"
MIN_NOME = 2
MAX_NOME = 200

_MENSAGENS_OBRIGATORIOS = {
    "nome": "Nome é obrigatório",
    "preco": "Preço é obrigatório",
    "estoque": "Estoque é obrigatório",
}


def _numero(valor, mensagem):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidationError(mensagem)
    return valor


def validar_produto(dados, validar_nome_e_categoria=True):
    """Valida o payload de criação/atualização de produto.

    Na criação valida também tamanho do nome e categoria; na atualização
    mantém o comportamento original (presença + valores não negativos).
    """
    if not dados:
        raise ValidationError("Dados inválidos")

    for campo, mensagem in _MENSAGENS_OBRIGATORIOS.items():
        if campo not in dados:
            raise ValidationError(mensagem)

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    categoria = dados.get("categoria", CATEGORIA_PADRAO)
    preco = _numero(dados["preco"], "Preço deve ser numérico")
    estoque = _numero(dados["estoque"], "Estoque deve ser numérico")

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")

    if validar_nome_e_categoria:
        if len(nome) < MIN_NOME:
            raise ValidationError("Nome muito curto")
        if len(nome) > MAX_NOME:
            raise ValidationError("Nome muito longo")
        if categoria not in CATEGORIAS_VALIDAS:
            raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    return {"nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque, "categoria": categoria}
