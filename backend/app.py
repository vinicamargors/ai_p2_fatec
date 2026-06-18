# Backend Flask para avaliação diagnóstica formativa com LLM em análise tática de futebol
# Autor: Vinicius Camargo

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from workflow import iniciar_sessao, responder_vfu
from cases import CASOS_DEMO

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Armazena sessões ativas em memória
sessoes_ativas = {}


# ── Frontend ──────────────────────────────────────────────────────────────────

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """
    Serve os arquivos estáticos do frontend.
    Se o arquivo existir, retorna ele. Senão, retorna o index.html.
    """
    if path != '' and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


# ── API ───────────────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'mensagem': 'P2 Fatec — Avaliação Formativa com LLM'
    })


@app.route('/api/casos', methods=['GET'])
def listar_casos():
    casos_resumo = [
        {
            'id': c['id'],
            'nome': c['nome'],
            'descricao': c['descricao'],
            'vfus_esperados': c['vfus_esperados'],
            'classificacao_esperada': c['classificacao_esperada'],
            'submissao': c['submissao'],
            'respostas_vfu': c.get('respostas_vfu', []),
        }
        for c in CASOS_DEMO
    ]
    return jsonify({'casos': casos_resumo})


@app.route('/api/avaliar', methods=['POST'])
def avaliar():
    data = request.get_json(silent=True) or {}

    nome = data.get('nome', '').strip()
    submissao = data.get('submissao', '').strip()

    if not nome or not submissao:
        return jsonify({'erro': 'nome e submissao são obrigatórios'}), 400

    try:
        resultado, sessao = iniciar_sessao(nome, submissao)
        sessao_id = sessao['id']

        if resultado['estado'] == 'aguardando_vfu':
            sessoes_ativas[sessao_id] = sessao

        resultado['sessao_id'] = sessao_id
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'erro': 'Falha ao iniciar avaliação',
            'detalhe': str(e)
        }), 500


@app.route('/api/responder-vfu', methods=['POST'])
def responder():
    data = request.get_json(silent=True) or {}

    sessao_id = data.get('sessao_id', '').strip()
    resposta = data.get('resposta', '').strip()

    if not sessao_id or not resposta:
        return jsonify({'erro': 'sessao_id e resposta são obrigatórios'}), 400

    sessao = sessoes_ativas.get(sessao_id)
    if not sessao:
        return jsonify({'erro': 'Sessão não encontrada ou já encerrada'}), 404

    try:
        resultado = responder_vfu(sessao, resposta)

        if resultado['estado'] == 'aguardando_vfu':
            sessoes_ativas[sessao_id] = sessao
        else:
            sessoes_ativas.pop(sessao_id, None)

        resultado['sessao_id'] = sessao_id
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'erro': 'Falha ao processar resposta da VFU',
            'detalhe': str(e)
        }), 500


@app.route('/api/sessoes', methods=['GET'])
def listar_sessoes():
    resumo = [
        {
            'sessao_id': sid,
            'nome_aprendiz': s.get('nome_aprendiz'),
            'estado': s.get('estado'),
            'estagio_atual': s.get('estagio_atual'),
            'vfus_realizados': len(s.get('historico_vfus', [])),
        }
        for sid, s in sessoes_ativas.items()
    ]
    return jsonify({'total': len(resumo), 'sessoes': resumo})


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False
    )
