# Workflow de avaliação diagnóstica formativa para análise tática de partida de futebol
# Autor: Vinicius Camargo

import uuid
from llm_service import interpretar_submissao
from pre_block import PRE_BLOCK


CLASSIFICACAO_LABELS = {
    "completamente_correto": "✅ Completamente Correto",
    "parcialmente_correto": "🟡 Parcialmente Correto",
    "completamente_incorreto": "❌ Completamente Incorreto",
}

RECOMENDACAO_LABELS = {
    "Prosseguir": "O aprendiz pode avançar para o próximo bloco.",
    "Progressão condicional": "O aprendiz pode avançar, mas precisa de atenção em pontos específicos.",
    "Retrabalho": "O aprendiz deve revisar e resubmeter antes de avançar.",
}


def _texto_normalizado(valor) -> str:
    return str(valor or "").strip().lower()


def _tem_lacuna_relevante(resposta_llm: dict) -> bool:
    lacuna = (resposta_llm.get("lacuna_principal") or "").strip()
    perfil = (resposta_llm.get("perfil_deficiencia") or "").strip()
    racional = (resposta_llm.get("racional") or "").strip()

    if lacuna:
        return True

    sinais = [
        "superficial",
        "generalização",
        "generalizacao",
        "sem detalhar",
        "carece",
        "não detalha",
        "nao detalha",
        "não demonstra",
        "nao demonstra",
        "parcialmente baseada",
        "baseada no resultado",
        "falta",
        "lacuna",
        "incompleta",
        "incompleto",
        "insuficiente",
        "frágil",
        "fragil",
    ]

    texto = f"{perfil} {racional}".lower()
    return any(sinal in texto for sinal in sinais)


def _vfu_agregaria_valor(resposta_llm: dict) -> bool:
    """
    Decide se vale a pena perguntar uma VFU.
    Ideia: perguntar quando há base parcial e lacuna verificável.
    """
    classificacao = _texto_normalizado(resposta_llm.get("classificacao"))
    nivel_confianca = _texto_normalizado(resposta_llm.get("nivel_confianca"))
    lacuna = (resposta_llm.get("lacuna_principal") or "").strip()

    if classificacao == "parcialmente_correto":
        return True

    if classificacao == "completamente_incorreto" and nivel_confianca in {"baixo", "medio", "médio"}:
        return True

    if lacuna and nivel_confianca in {"baixo", "medio", "médio"}:
        return True

    return False


def _deve_forcar_vfu(resposta_llm: dict, vfus_usados: int, max_vfus: int) -> bool:
    """
    Mesmo que o LLM peça classificação, o workflow pode forçar VFU
    se ainda houver incerteza relevante e o orçamento permitir.
    """
    if vfus_usados >= max_vfus:
        return False

    if not _tem_lacuna_relevante(resposta_llm):
        return False

    return _vfu_agregaria_valor(resposta_llm)


def _gerar_pergunta_vfu_fallback(resposta_llm: dict) -> str:
    lacuna = (resposta_llm.get("lacuna_principal") or "").strip()
    hipotese = (resposta_llm.get("hipotese_diagnostica") or "").strip()

    if lacuna:
        return (
            "Explique com base em evidências concretas da partida como você sustenta sua análise, "
            f"principalmente no ponto: {lacuna}"
        )

    if hipotese:
        return (
            "Apresente a evidência observável que confirma sua hipótese diagnóstica: "
            f"{hipotese}"
        )

    return (
        "Quais evidências observáveis da partida sustentam sua conclusão "
        "e como elas demonstram a relação causal da sua análise tática?"
    )


def _normalizar_resposta_llm(resposta_llm: dict) -> dict:
    """
    Garante chaves mínimas e valores seguros para o workflow não quebrar.
    """
    if not isinstance(resposta_llm, dict):
        resposta_llm = {}

    acao = _texto_normalizado(resposta_llm.get("acao"))
    if acao not in {"vfu", "classificar"}:
        acao = "classificar"

    resposta_llm["acao"] = acao
    resposta_llm["classificacao"] = resposta_llm.get("classificacao", "completamente_incorreto")
    resposta_llm["recomendacao"] = resposta_llm.get("recomendacao", "Retrabalho")
    resposta_llm["lacuna_principal"] = resposta_llm.get("lacuna_principal", "")
    resposta_llm["perfil_deficiencia"] = resposta_llm.get("perfil_deficiencia", "")
    resposta_llm["nivel_confianca"] = resposta_llm.get("nivel_confianca", "medio")
    resposta_llm["racional"] = resposta_llm.get("racional", "")
    resposta_llm["hipotese_diagnostica"] = resposta_llm.get("hipotese_diagnostica", "")
    resposta_llm["pergunta_vfu"] = resposta_llm.get("pergunta_vfu", "")

    return resposta_llm


def iniciar_sessao(nome_aprendiz: str, submissao: str):
    """
    Estágios 1-5 do fluxograma:
    Pre-Block → Submissão → Interpretação → Hipótese → Verificação de suficiência

    Retorna:
      (resultado_api, sessao)
    """
    sessao = {
        "id": str(uuid.uuid4()),
        "nome_aprendiz": nome_aprendiz,
        "submissao_inicial": submissao,
        "historico_vfus": [],
        "estado": "em_andamento",
        "resultado": None,
        "estagio_atual": "interpretacao_inicial",
        "ultimo_vfu_pergunta": "",
    }

    resultado = _processar_estagio(sessao)
    return resultado, sessao


def responder_vfu(sessao: dict, resposta_vfu: str) -> dict:
    """
    Estágios 6-8 do fluxograma:
    VFU enviado → Resposta recebida → Reanálise
    """
    ultimo_vfu = sessao.get("ultimo_vfu_pergunta", "")

    sessao["historico_vfus"].append({
        "pergunta": ultimo_vfu,
        "resposta": resposta_vfu,
    })

    sessao["estagio_atual"] = "reanalise_pos_vfu"
    return _processar_estagio(sessao)


def _processar_estagio(sessao: dict) -> dict:
    """
    Núcleo do workflow:
    hipótese → suficiência → VFU ou classificação → output teacher-facing
    """
    submissao = sessao["submissao_inicial"]
    historico = sessao["historico_vfus"]
    max_vfus = PRE_BLOCK["politica_vfu"]["max_vfus"]

    resposta_llm = interpretar_submissao(submissao, historico)
    resposta_llm = _normalizar_resposta_llm(resposta_llm)

    vfus_usados = len(historico)
    acao = resposta_llm["acao"]

    # Se o LLM quis classificar cedo demais, o workflow pode forçar VFU.
    if acao == "classificar" and _deve_forcar_vfu(resposta_llm, vfus_usados, max_vfus):
        acao = "vfu"
        resposta_llm["acao"] = "vfu"

        if not resposta_llm.get("pergunta_vfu"):
            resposta_llm["pergunta_vfu"] = _gerar_pergunta_vfu_fallback(resposta_llm)

        if not resposta_llm.get("hipotese_diagnostica"):
            resposta_llm["hipotese_diagnostica"] = (
                "Há evidência parcial, mas ainda existe lacuna diagnóstica que exige verificação adicional."
            )

    # Stop rule: não pode passar do limite de VFUs
    if vfus_usados >= max_vfus and acao == "vfu":
        acao = "classificar"
        resposta_llm["acao"] = "classificar"

        if not resposta_llm.get("classificacao"):
            resposta_llm["classificacao"] = "parcialmente_correto"

        if not resposta_llm.get("recomendacao"):
            resposta_llm["recomendacao"] = "Progressão condicional"

    # Emite VFU
    if acao == "vfu":
        pergunta_vfu = resposta_llm.get("pergunta_vfu") or _gerar_pergunta_vfu_fallback(resposta_llm)

        sessao["ultimo_vfu_pergunta"] = pergunta_vfu
        sessao["estagio_atual"] = "aguardando_resposta_vfu"
        sessao["estado"] = "em_andamento"

        return {
            "estado": "aguardando_vfu",
            "sessao_id": sessao["id"],
            "numero_vfu": vfus_usados + 1,
            "pergunta_vfu": pergunta_vfu,
            "hipotese_diagnostica": resposta_llm.get("hipotese_diagnostica", ""),
            "lacuna_principal": resposta_llm.get("lacuna_principal", ""),
            "vfus_usados": vfus_usados,
            "max_vfus": max_vfus,
        }

    # Classificação final
    classificacao = resposta_llm.get("classificacao", "completamente_incorreto")
    recomendacao = resposta_llm.get("recomendacao", "Retrabalho")

    sessao["estado"] = "concluido"
    sessao["estagio_atual"] = "output_professor"
    sessao["resultado"] = resposta_llm

    return {
        "estado": "concluido",
        "sessao_id": sessao["id"],
        "nome_aprendiz": sessao["nome_aprendiz"],
        "classificacao": classificacao,
        "classificacao_label": CLASSIFICACAO_LABELS.get(classificacao, classificacao),
        "recomendacao": recomendacao,
        "recomendacao_descricao": RECOMENDACAO_LABELS.get(recomendacao, ""),
        "lacuna_principal": resposta_llm.get("lacuna_principal"),
        "perfil_deficiencia": resposta_llm.get("perfil_deficiencia", ""),
        "nivel_confianca": resposta_llm.get("nivel_confianca", "medio"),
        "racional": resposta_llm.get("racional", ""),
        "vfus_realizados": vfus_usados,
        "historico_vfus": historico,
    }