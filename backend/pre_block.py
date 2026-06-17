# Modelo de pré-block para análise tática de partida de futebol. O aprendiz deve interpretar dados reais de uma partida e justificar conclusões táticas com base em evidências concretas, não apenas impressões.
# Autor: Vinicius Camargo

PRE_BLOCK = {
    "titulo": "Análise Tática de Partida de Futebol",
    "descricao": (
        "Bloco de avaliação formativa sobre análise tática de futebol. "
        "O aprendiz deve interpretar dados reais de uma partida e justificar "
        "conclusões táticas com base em evidências concretas, não apenas impressões."
    ),

    "objetivos": [
        "Identificar o sistema tático utilizado pelo time com base em posicionamento e movimentação",
        "Interpretar estatísticas da partida (posse de bola, finalizações, desarmes) como evidências táticas",
        "Distinguir causa e efeito nos eventos da partida (ex: pressão alta causou erros de passe)",
        "Justificar conclusões táticas com dados concretos da partida",
        "Reconhecer limitações de uma análise baseada apenas em resultado final",
    ],

    "evidencias_esperadas": [
        "Menciona sistema tático com justificativa (ex: 4-3-3 com pressão alta)",
        "Cita ao menos uma estatística concreta (posse, chutes, passes certos %)",
        "Relaciona dado estatístico a decisão tática do treinador",
        "Explica pelo menos uma falha tática com evidência (não só 'o time jogou mal')",
        "Não baseia conclusão apenas no placar final",
    ],

    "padroes_misconception": [
        "Basear toda análise no placar sem mencionar dados táticos",
        "Confundir resultado com desempenho (ganhou logo jogou bem)",
        "Citar estatísticas sem conectá-las a decisões táticas",
        "Atribuir derrota a 'falta de vontade' ou 'azar' sem evidência tática",
        "Descrever lances isolados sem contexto tático do jogo",
        "Usar linguagem fluente e técnica sem apresentar nenhuma evidência concreta",
    ],

    "criterios_rubrica": {
        "identificacao_tatica": "Identifica sistema tático com justificativa baseada em posicionamento/movimentação",
        "uso_estatisticas": "Usa ao menos uma estatística concreta como evidência de decisão tática",
        "causa_efeito": "Estabelece relação causal entre tática e evento da partida",
        "conclusao_proporcional": "Conclusão final é proporcional às evidências apresentadas",
        "nao_baseia_no_placar": "Análise vai além do resultado e considera processo tático",
    },

    "politica_vfu": {
        "max_vfus": 2,
        "quando_perguntar": (
            "Fazer VFU apenas quando há incerteza diagnóstica relevante: "
            "o aprendiz apresentou alguma evidência mas há uma lacuna central não resolvida. "
            "NÃO fazer VFU quando a ausência de evidência já é suficiente para classificar."
        ),
        "exemplos_vfu": [
            "Que dado da partida justifica essa conclusão tática que você apresentou?",
            "Como as estatísticas de posse de bola se relacionam com o sistema tático que você identificou?",
            "Qual evidência concreta mostra que foi uma decisão tática do treinador e não um acidente de jogo?",
            "Por que o placar sozinho não é suficiente para essa conclusão que você tirou?",
            "Que diferença você observa entre o desempenho do time no primeiro e no segundo tempo, com base nos dados?",
        ],
    },

    "stop_rule": (
        "Encerrar quando: (1) evidência suficiente para classificar foi obtida, "
        "(2) misconception central foi identificado e VFU não o resolveu, "
        "(3) limite de 2 VFUs foi atingido. "
        "Nunca ultrapassar 2 VFUs. Nunca funcionar como tutor aberto."
    ),

    "classificacoes": {
        "completamente_correto": {
            "significado": "Base evidencial esperada demonstrada com interpretação coerente e conclusões proporcionais.",
            "condicao": "Todos os critérios da rubrica atendidos, nenhum misconception central presente.",
            "recomendacao": "Prosseguir",
        },
        "parcialmente_correto": {
            "significado": "Base funcional presente mas incompleta. Lacuna suave em ao menos um critério.",
            "condicao": "Núcleo da resposta presente mas falta evidência em unidades como estatísticas, causa-efeito ou conclusão proporcional.",
            "recomendacao": "Progressão condicional",
        },
        "completamente_incorreto": {
            "significado": "Base evidencial mínima não demonstrada.",
            "condicao": "Evidência ausente, baseada só no placar, ou comprometida por misconception central.",
            "recomendacao": "Retrabalho",
        },
    },
}