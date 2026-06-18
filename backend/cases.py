CASOS_DEMO = [
    {
        "id": "C01",
        "nome": "Ana Silva",
        "vfus_esperados": 0,
        "classificacao_esperada": "completamente_correto",
        "descricao": "Resposta completa com evidências sólidas",
        "submissao": """
Analisei a partida entre Flamengo e Palmeiras (2x1). O Flamengo utilizou um sistema 4-3-3
com pressão alta no campo adversário, o que ficou evidente pela estatística de 67% de posse
de bola e 18 finalizações contra apenas 7 do Palmeiras.

A pressão alta forçou erros de passe na saída de bola do Palmeiras — foram 23 erros de passe
do time paulista no primeiro tempo, número acima da média deles na temporada (14 por jogo).
Isso gerou os dois primeiros gols em transições rápidas após recuperação de bola no campo
adversário, característica típica do sistema de pressão alta.

No segundo tempo, o Flamengo recuou para um 4-5-1 após o segundo gol, reduzindo as linhas
e priorizando a manutenção do resultado. A queda para 41% de posse no segundo tempo confirma
essa mudança tática intencional. O gol do Palmeiras veio de uma jogada de bola parada,
não de uma ruptura tática do sistema defensivo montado.

Conclusão: o resultado reflete uma superioridade tática clara, não apenas qualidade individual,
evidenciada pelos dados de pressão, recuperação de bola e aproveitamento de transições.
""",
    },
    {
        "id": "C02",
        "nome": "Bruno Oliveira",
        "vfus_esperados": 0,
        "classificacao_esperada": "completamente_incorreto",
        "descricao": "Resposta baseada só em placar e estatísticas genéricas",
        "submissao": """
O São Paulo venceu o Athletico-PR por 3x1. O São Paulo teve 61% de posse de bola,
acertou 87% dos passes e finalizou 16 vezes. O Athletico finalizou apenas 5 vezes.

O time de São Paulo jogou muito bem e mereceu a vitória. Os números mostram
claramente que o São Paulo foi superior em todos os aspectos do jogo.
O Athletico não conseguiu desenvolver seu jogo e acabou sendo dominado.

Os três gols do São Paulo mostram a eficiência do time. O placar de 3x1 reflete
bem o que aconteceu em campo. Foi uma vitória tranquila e merecida para o São Paulo.
""",
    },
    {
        "id": "C03",
        "nome": "Carla Mendes",
        "vfus_esperados": 1,
        "classificacao_esperada": "completamente_correto",
        "descricao": "Primeira VFU resolve a lacuna causal",
        "submissao": """
O Santos jogou com 4-3-3 e teve 54% de posse de bola contra o Corinthians.
O time pressionou bastante e criou várias chances de gol. O Corinthians ficou
recuado durante quase todo o jogo, o que mostra que a tática do Santos funcionou.

O Santos finalizou 14 vezes e venceu por 2x0. Os dois gols foram em jogadas
trabalhadas, não em bola parada. O time do Corinthians errou muitos passes
quando tentou sair jogando.

Acredito que o sistema 4-3-3 foi bem executado e que isso explica a vitória.
O time que tem mais posse geralmente controla melhor o jogo e isso ficou
evidente aqui.
""",
        "respostas_vfu": [
            "A pressão pós-perda foi importante porque o Santos recuperava a bola rapidamente depois de perder a posse, o que impedia o Corinthians de sair jogando com segurança.",
        ],
    },
    {
    "id": "C04",
    "nome": "Diego Ferreira",
    "vfus_esperados": 1,
    "classificacao_esperada": "completamente_incorreto",
    "descricao": "Primeira submissão gera hipótese diagnóstica; VFU confirma misconception estrutural",
    "submissao": """
O São Paulo venceu o Athletico-PR por 3x1. O São Paulo teve 61% de posse de bola,
acertou 87% dos passes e finalizou 16 vezes. O Athletico finalizou apenas 5 vezes.

Esses números mostram que o São Paulo foi superior durante a partida.
O time controlou melhor o jogo e por isso mereceu a vitória.

O placar de 3x1 confirma que o São Paulo foi mais eficiente em campo.
""",
    "respostas_vfu": [
        "A superioridade do São Paulo aparece porque o time teve mais posse, mais passes certos e mais finalizações, então isso prova que foi melhor taticamente."
    ],
},
{
        "id": "C05",
        "nome": "Eva Costa",
        "vfus_esperados": 2,
        "classificacao_esperada": "completamente_correto",
        "descricao": "Duas VFUs são necessárias para fechar a lacuna, mas o caso evolui para correto",
        "submissao": """
O Santos jogou com 4-3-3 e manteve mais posse de bola. O time controlou o jogo
porque esteve mais tempo com a bola e criou mais chances. O Corinthians ficou
recuando e isso já mostra a superioridade do Santos.

Os números de posse e finalizações indicam que o Santos foi melhor in campo.
O time conseguiu vencer porque atacou mais e foi mais constante no jogo.
""",
        "respostas_vfu": [
            # Resposta 1: Entrega os dados e estatísticas cobrados, mas deixa uma leve ponta solta na transição
            "Analisando os dados do scout, o Santos fechou a partida com 61% de posse de bola e realizou 16 finalizações contra apenas 5 do Corinthians. Essa superioridade estatística se materializou porque os pontas espetaram a defesa adversária, obrigando o bloco do Corinthians a recuar de forma crônica para proteger a própria área.",
            
            # Resposta 2: Entrega o mecanismo tático de sustentação (pressão pós-perda) e mata a lacuna
            "Para sustentar essa presença no campo de ataque sem sofrer contragolpes, o Santos aplicou uma transição defensiva agressiva. No momento exato da perda da posse, o bloco avançado subia a pressão no portador da bola em menos de 5 segundos, enquanto a linha defensiva se mantinha compacta e alta para interceptar qualquer tentativa de ligação direta do Corinthians."
        ],
    },
    {
        "id": "C06",
        "nome": "Fernando Lima",
        "vfus_esperados": 2,
        "classificacao_esperada": "completamente_incorreto",
        "descricao": "Duas VFUs são necessárias para fechar a lacuna, mas o caso evolui para incorreto",
        "submissao": """
O Corinthians jogou com 4-3-3 e manteve mais posse de bola. O time controlou o jogo
porque esteve mais tempo com a bola e criou mais chances. O Santos ficou
recuado e isso já mostra a superioridade do Corinthians.

Os números de posse e finalizações indicam que o Corinthians foi melhor em campo.
O time conseguiu vencer porque atacou mais e foi mais constante no jogo.
""",
        "respostas_vfu": [
            "A posse do Santos ajudou a empurrar o Corinthians para trás, mas ainda falta explicar melhor como isso se conectou com a pressão após a perda da bola.",
            "Além disso, o Santos mantinha uma recomposição rápida e uma estrutura defensiva compacta, o que reduzia a saída limpa do Corinthians depois das recuperações.",
        ],
    }
]
