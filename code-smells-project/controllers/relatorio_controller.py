from flask import jsonify

from services import relatorio_service


def vendas():
    relatorio = relatorio_service.vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200
