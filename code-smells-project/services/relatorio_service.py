from models import pedido_model

FAIXA_ALTA = 10000.0
DESCONTO_FAIXA_ALTA = 0.1
FAIXA_MEDIA = 5000.0
DESCONTO_FAIXA_MEDIA = 0.05
FAIXA_BAIXA = 1000.0
DESCONTO_FAIXA_BAIXA = 0.02


def vendas():
    """Calcula o relatório de vendas aplicando as faixas de desconto."""
    dados = pedido_model.resumo_vendas()
    faturamento = dados["faturamento_bruto"]
    total_pedidos = dados["total_pedidos"]

    desconto = 0.0
    if faturamento > FAIXA_ALTA:
        desconto = faturamento * DESCONTO_FAIXA_ALTA
    elif faturamento > FAIXA_MEDIA:
        desconto = faturamento * DESCONTO_FAIXA_MEDIA
    elif faturamento > FAIXA_BAIXA:
        desconto = faturamento * DESCONTO_FAIXA_BAIXA

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": dados["pedidos_pendentes"],
        "pedidos_aprovados": dados["pedidos_aprovados"],
        "pedidos_cancelados": dados["pedidos_cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
