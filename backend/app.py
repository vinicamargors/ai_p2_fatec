# Backend Flask para avaliação diagnóstica formativa com LLM em análise tática de futebol
# Autor: Vinicius Camargo

import os

import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from workflow import iniciar_sessao, responder_vfu
from cases import CASOS_DEMO

app = Flask(__name__)
CORS(app)

# Armazena sessões ativas em memória
sessoes_ativas = {}


@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "mensagem": "P2 Fatec — Avaliação Formativa com LLM"
    })


@app.route("/casos", methods=["GET"])
def listar_casos():
    """
    Retorna os casos de demo para o frontend carregar.
    """
    casos_resumo = [
        {
            "id": c["id"],
            "nome": c["nome"],
            "descricao": c["descricao"],
            "vfus_esperados": c["vfus_esperados"],
            "classificacao_esperada": c["classificacao_esperada"],
            "submissao": c["submissao"],
            "respostas_vfu": c.get("respostas_vfu", []),
        }
        for c in CASOS_DEMO
    ]
    return jsonify({"casos": casos_resumo})


@app.route("/avaliar", methods=["POST"])
def avaliar():
    """
    Inicia uma nova sessão de avaliação.
    Body:
    {
      "nome": "Ana Silva",
      "submissao": "texto da submissão"
    }
    """
    data = request.get_json(silent=True) or {}

    nome = data.get("nome", "").strip()
    submissao = data.get("submissao", "").strip()

    if not nome or not submissao:
        return jsonify({"erro": "nome e submissao são obrigatórios"}), 400

    try:
        resultado, sessao = iniciar_sessao(nome, submissao)
        sessao_id = sessao["id"]

        # Só guarda em memória se a sessão ainda está em andamento
        if resultado["estado"] == "aguardando_vfu":
            sessoes_ativas[sessao_id] = sessao

        # O frontend usa esse id para responder VFUs
        resultado["sessao_id"] = sessao_id

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            "erro": "Falha ao iniciar avaliação",
            "detalhe": str(e)
        }), 500


@app.route("/responder-vfu", methods=["POST"])
def responder():
    """
    Envia resposta do aprendiz para uma VFU.
    Body:
    {
      "sessao_id": "...",
      "resposta": "texto da resposta"
    }
    """
    data = request.get_json(silent=True) or {}

    sessao_id = data.get("sessao_id", "").strip()
    resposta = data.get("resposta", "").strip()

    if not sessao_id or not resposta:
        return jsonify({"erro": "sessao_id e resposta são obrigatórios"}), 400

    sessao = sessoes_ativas.get(sessao_id)
    if not sessao:
        return jsonify({"erro": "Sessão não encontrada ou já encerrada"}), 404

    try:
        resultado = responder_vfu(sessao, resposta)

        # Se ainda precisa de VFU, mantém sessão viva
        if resultado["estado"] == "aguardando_vfu":
            sessoes_ativas[sessao_id] = sessao
        else:
            # Caso concluído: remove da memória
            sessoes_ativas.pop(sessao_id, None)

        resultado["sessao_id"] = sessao_id
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            "erro": "Falha ao processar resposta da VFU",
            "detalhe": str(e)
        }), 500


@app.route("/sessoes", methods=["GET"])
def listar_sessoes():
    """
    Endpoint auxiliar de debug.
    Pode remover depois se quiser.
    """
    resumo = []
    for sessao_id, sessao in sessoes_ativas.items():
        resumo.append({
            "sessao_id": sessao_id,
            "nome_aprendiz": sessao.get("nome_aprendiz"),
            "estado": sessao.get("estado"),
            "estagio_atual": sessao.get("estagio_atual"),
            "vfus_realizados": len(sessao.get("historico_vfus", [])),
        })

    return jsonify({
        "total": len(resumo),
        "sessoes": resumo
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )