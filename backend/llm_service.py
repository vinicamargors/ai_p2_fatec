# Serviço de LLM para avaliação diagnóstica formativa em análise tática de futebol
# Autor: Vinicius Camargo

import os
import json
import re
from google import genai
from dotenv import load_dotenv
from pre_block import PRE_BLOCK

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

ACOES_VALIDAS = {"vfu", "classificar"}
CLASSIFICACOES_VALIDAS = {
    "completamente_correto": "Prosseguir",
    "parcialmente_correto": "Progressão condicional",
    "completamente_incorreto": "Retrabalho",
}
CONFIANCAS_VALIDAS = {"alto", "medio", "baixo"}


def _limpar_json_texto(texto: str) -> str:
    texto = texto.strip()

    if texto.startswith("```"):
        texto = re.sub(r"^```[a-zA-Z0-9]*\n?", "", texto)
        texto = re.sub(r"\n?```$", "", texto)

    texto = texto.strip()

    try:
        json.loads(texto)
        return texto
    except Exception:
        pass

    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        return match.group(0)

    raise ValueError("Resposta do modelo não contém JSON válido.")


def _montar_prompt_sistema():
    pb = PRE_BLOCK
    return f"""Você é um avaliador diagnóstico formativo especializado em análise tática de futebol.

Seu papel é EXCLUSIVAMENTE diagnóstico — não é tutor, não dá respostas, não ensina.

=== PRE-BLOCK (ÂNCORA ANTI-ALUCINAÇÃO) ===
Você SÓ pode classificar com base nas evidências abaixo.
Nunca baseie classificação em fluência de linguagem, tamanho da resposta ou impressão geral.

OBJETIVOS DO BLOCO:
{json.dumps(pb["objetivos"], ensure_ascii=False, indent=2)}

EVIDÊNCIAS ESPERADAS:
{json.dumps(pb["evidencias_esperadas"], ensure_ascii=False, indent=2)}

PADRÕES DE MISCONCEPTION:
{json.dumps(pb["padroes_misconception"], ensure_ascii=False, indent=2)}

CRITÉRIOS DA RUBRICA:
{json.dumps(pb["criterios_rubrica"], ensure_ascii=False, indent=2)}

STOP RULE:
{pb["stop_rule"]}

POLÍTICA DE VFU:
{pb["politica_vfu"]["quando_perguntar"]}

CLASSIFICAÇÕES POSSÍVEIS:
- completamente_correto → {pb["classificacoes"]["completamente_correto"]["recomendacao"]}
- parcialmente_correto → {pb["classificacoes"]["parcialmente_correto"]["recomendacao"]}
- completamente_incorreto → {pb["classificacoes"]["completamente_incorreto"]["recomendacao"]}

=== REGRAS DE OURO ===
1. NUNCA classifique baseado apenas em linguagem fluente ou resposta longa.
2. NUNCA faça mais de {pb["politica_vfu"]["max_vfus"]} VFUs no total.
3. NUNCA invente evidências que o aprendiz não apresentou.
4. Se a evidência já for suficiente, classifique imediatamente.
5. Se a base evidencial mínima estiver ausente e nova pergunta dificilmente mudar a ação pedagógica, classifique imediatamente.
6. Só faça VFU se ainda houver incerteza relevante em UM ponto principal.
7. A VFU deve ser curta, focada e diagnóstica — não pode ser tutoria aberta.
8. Responda SEMPRE em JSON válido, sem explicação fora do JSON.
"""


def _montar_prompt_avaliacao(submissao, historico_vfus):
    historico_str = ""
    if historico_vfus:
        historico_str = "\n=== HISTÓRICO DE VFUs ===\n"
        for i, par in enumerate(historico_vfus, 1):
            historico_str += (
                f"\nVFU {i}: {par['pergunta']}\n"
                f"Resposta: {par['resposta']}\n"
            )

    vfus_usados = len(historico_vfus)
    pb = PRE_BLOCK
    max_vfus = pb["politica_vfu"]["max_vfus"]

    limite_msg = ""
    if vfus_usados >= max_vfus:
        limite_msg = "VOCÊ ATINGIU O LIMITE DE VFUs. CLASSIFIQUE AGORA OBRIGATORIAMENTE."

    return f"""=== SUBMISSÃO DO APRENDIZ ===
{submissao}
{historico_str}

=== INSTRUÇÃO ===
VFUs já realizados: {vfus_usados} de {max_vfus} permitidos.
{limite_msg}

Analise a submissão contra o Pre-Block.

Regras decisórias:
- Se faltar evidência mínima e for improvável que nova pergunta mude a decisão pedagógica, classifique agora.
- Se houver entendimento funcional, mas ainda existir uma incerteza principal relevante, faça UMA VFU curta e focada.
- Se a evidência já for suficiente, classifique agora.
- Não faça tutoria aberta, não peça redação longa e não faça mais de uma pergunta.

Responda em JSON com EXATAMENTE um dos formatos abaixo.

Se precisar de VFU (apenas se vfus_usados < {max_vfus}):
{{
  "acao": "vfu",
  "pergunta_vfu": "pergunta focada e direta aqui",
  "hipotese_diagnostica": "o que foi identificado até agora",
  "lacuna_principal": "qual ponto específico ainda está incerto"
}}

Se já tem evidência suficiente para classificar:
{{
  "acao": "classificar",
  "classificacao": "completamente_correto" | "parcialmente_correto" | "completamente_incorreto",
  "recomendacao": "Prosseguir" | "Progressão condicional" | "Retrabalho",
  "lacuna_principal": "descrição da lacuna ou null se completamente correto",
  "perfil_deficiencia": "resumo dos critérios atendidos e não atendidos",
  "nivel_confianca": "alto" | "medio" | "baixo",
  "racional": "justificativa baseada exclusivamente nas evidências do Pre-Block"
}}
"""


def _normalizar_resultado(resultado: dict, historico_vfus: list) -> dict:
    vfus_usados = len(historico_vfus)
    max_vfus = PRE_BLOCK["politica_vfu"]["max_vfus"]

    if not isinstance(resultado, dict):
        raise ValueError("Resultado do modelo não é um objeto JSON.")

    acao = resultado.get("acao")
    if acao not in ACOES_VALIDAS:
        raise ValueError(f"Ação inválida recebida do modelo: {acao}")

    if vfus_usados >= max_vfus and acao == "vfu":
        resultado = {
            "acao": "classificar",
            "classificacao": "parcialmente_correto",
            "recomendacao": "Progressão condicional",
            "lacuna_principal": resultado.get("lacuna_principal") or "Limite de VFUs atingido com incerteza remanescente",
            "perfil_deficiencia": resultado.get("hipotese_diagnostica") or "Evidência parcial com incerteza residual após limite de follow-ups",
            "nivel_confianca": "medio",
            "racional": "O limite de VFUs foi atingido; pela stop rule, a decisão deve ser encerrada com base na evidência acumulada.",
        }
        acao = "classificar"

    if acao == "vfu":
        pergunta = (resultado.get("pergunta_vfu") or "").strip()
        if not pergunta:
            raise ValueError("Modelo retornou ação 'vfu' sem pergunta_vfu.")
        resultado["pergunta_vfu"] = pergunta
        resultado["hipotese_diagnostica"] = (resultado.get("hipotese_diagnostica") or "").strip()
        resultado["lacuna_principal"] = (resultado.get("lacuna_principal") or "").strip()
        return resultado

    classificacao = resultado.get("classificacao")
    if classificacao not in CLASSIFICACOES_VALIDAS:
        raise ValueError(f"Classificação inválida: {classificacao}")

    recomendacao_esperada = CLASSIFICACOES_VALIDAS[classificacao]
    recomendacao = resultado.get("recomendacao")
    if recomendacao != recomendacao_esperada:
        resultado["recomendacao"] = recomendacao_esperada

    confianca = resultado.get("nivel_confianca")
    if confianca not in CONFIANCAS_VALIDAS:
        resultado["nivel_confianca"] = "medio"

    if classificacao == "completamente_correto":
        resultado["lacuna_principal"] = None

    if not resultado.get("perfil_deficiencia"):
        resultado["perfil_deficiencia"] = "Não informado explicitamente pelo modelo."

    if not resultado.get("racional"):
        resultado["racional"] = "Classificação baseada na evidência acumulada em relação ao Pre-Block."

    return resultado


def interpretar_submissao(submissao: str, historico_vfus: list | None = None) -> dict:
    historico_vfus = historico_vfus or []

    prompt_sistema = _montar_prompt_sistema()
    prompt_avaliacao = _montar_prompt_avaliacao(submissao, historico_vfus)

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt_avaliacao,
        config={
            "system_instruction": prompt_sistema,
            "temperature": 0.1,
            "response_mime_type": "application/json",
        },
    )

    texto = _limpar_json_texto(response.text)
    resultado = json.loads(texto)
    return _normalizar_resultado(resultado, historico_vfus)


def avaliar_submissao_inicial(submissao: str) -> dict:
    return interpretar_submissao(submissao=submissao, historico_vfus=[])


def reavaliar_com_vfu(submissao: str, historico_vfus: list) -> dict:
    return interpretar_submissao(submissao=submissao, historico_vfus=historico_vfus)