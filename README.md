Plaintext
# ⚽ AvaliaFut — Micro-Avaliação Formativa com GenAI & Máquina de Estados

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Gemini-3.1--Flash--Lite-orange?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Docker](https://img.shields.io/badge/Docker-Nginx--Alpine-blue?logo=docker&logoColor=white)](https://www.docker.com/)

> **Projeto de Implementation Prática — P2 FATEC Carapicuíba (2026)**
> Baseado no framework científico: *Artifact-Grounded Formative Micro-Assessment with GenAI Verification Follow-Ups*.

---

## 📌 1. Visão Geral do Projeto & Contexto

O **AvaliaFut** é uma plataforma inteligente de micro-avaliação formativa projetada especificamente para o módulo de **Análise Tática de Futebol em um Curso de Treinadores Amadores**. 

O sistema automatiza o diagnóstico de competências analíticas de novos técnicos através de uma arquitetura modular que combina uma **Máquina de Estados em Python** com o poder de inferência do modelo **Gemini-3.1-Flash-Lite**. Em vez de realizar correções binárias e estáticas (estilo "certo ou errado"), o sistema engaja o aluno em rodadas dinâmicas de perguntas de acompanhamento (*Verification Follow-Ups* — VFUs) para investigar a profundidade do seu raciocínio tático.

---

## 🚨 2. O Problema Central: O Fenômeno da "Falsa Maestria"

Com a popularização massiva de LLMs (como ChatGPT, Claude e Gemini), surgiu um grande gargalo pedagógico: **a eloquência gerada por IA**. Alunos conseguem produzir narrativas extremamente fluidas, elegantes, cheias de jargões midiáticos e superficialmente convincentes, ocultando uma completa ausência de entendimento prático e causal. É a chamada **Falsa Maestria (*False Mastery*)**.

### Como o AvaliaFut resolve isso?
O sistema adota quatro compromissos estritos:
1. **Baseado em Artefatos (*Artifact-Grounded*):** O julgamento da IA depende exclusivamente de evidências extraídas daquilo que o aluno mensurou ou observou (scouts, estatísticas, dinâmicas de jogo).
2. **Formativo:** O resultado final apoia a progressão do aluno através de feedbacks acionáveis, em vez de apenas atribuir uma nota punitiva.
3. **Limitado (*Bounded*):** A interação é estritamente controlada por regras de negócio. O orçamento máximo é de **2 VFUs**, impedindo conversas abertas ou alucinações.
4. **Focado no Professor (*Teacher-Facing*):** O produto final da esteira é um relatório cirúrgico para o docente, detalhando a lacuna principal, o racional técnico da nota e a recomendação pedagógica de avanço.

---

## 🛠️ 3. Fundamentação Metodológica (O Fluxograma do Slide 8)

O coração do backend foi codificado seguindo rigorosamente as **10 etapas operacionais** propostas no referencial teórico da disciplina (*Evidence to Decision Workflow*):

[1. Pré-Block Modeling]
│
[2. Submissão do Aluno] ──> [3. Interpretação de Evidências] ──> [4. Hipótese Diagnóstica]
│
┌───────────────────────────────────────────────────────────────┘
▼
[5. Suficiência / Stop Rule?] ──(Sim)──> [8. Classificação Final] ──> [9. Output Professor] ──> [10. Recomendação]
│
(Não)
▼
[6. Verification Follow-Up (VFU)] ──> [7. Reanálise da Resposta] ──> (Retorna ao ponto 5)


1. **Pre-Block Modeling:** O professor define imutavelmente no código as rubricas, objetivos e padrões de erro comum (*misconceptions*).
2. **Student Submission:** O aluno insere a sua análise tática inicial sobre uma partida (ex: Santos vs Corinthians).
3. **Initial Evidence Interpretation:** O LLM avalia a submissão estritamente contra as regras do Pré-Block.
4. **Diagnostic Hypothesis:** A IA formula internamente quais competências foram demonstradas e quais estão ausentes.
5. **Sufficient Evidence Check / Stop Rule:** O sistema roda regras lógicas em Python para verificar se há dados suficientes para classificar ou se o teto de iterações estourou.
6. **Verification Follow-Up (VFU):** Se houver uma lacuna crítica, a IA gera uma pergunta curta e cirúrgica direcionada ao ponto cego do aluno.
7. **Response Reanalysis:** O aluno responde à VFU e o motor assíncrono junta a resposta ao histórico para reavaliação completa.
8. **Final Classification:** O aluno recebe uma classificação categórica: *Completely Correct*, *Partially Correct* ou *Completely Incorrect*.
9. **Teacher-Facing Output:** Geração de um Racional claro, Perfil de Deficiência e Nível de Confiança da análise.
10. **Progression Recommendation:** Sugestão de conduta pedagógica direta: *Proceed* (Avançar), *Conditional Progression* (Avanço Condicional) ou *Rework* (Refazer a Atividade).

---

## 🛡️ 4. Blindagem Anti-Alucinação e Engenharia de Prompt

Para garantir o determinismo do software e impedir que a IA mude de opinião, actue de forma frouxa ou invente critérios, implementamos três camadas de proteção de engenharia:

* **Ancoragem de Dados (`pre_block.py`):** O modelo não possui liberdade criativa para julgar o que é certo ou errado. Os critérios lógicos e os padrões de erro conceituais são injetados de forma estática no contexto de cada requisição.
* **Determinismo Térmico:** Configuração de `temperature: 0.1` na chamada da API do Gemini, forçando o modelo a utilizar o caminho lógico mais provável e consistente, eliminando variações indesejadas.
* **Tipagem Estruturada Nativa:** O parâmetro `"response_mime_type": "application/json"` é configurado no SDK oficial. Isso força a IA a responder obedecendo estritamente um contrato de schema JSON predefinido, mitigando qualquer tentativa de cuspir texto livre que quebraria o frontend.

---

## 📊 5. Matriz de Validação: Os 6 Casos de Teste (Requisito P2)

Para validar a integridade do workflow e provar a estabilidade da máquina de estados, o sistema conta com uma massa de testes contendo **6 perfis de aprendizes** meticulosamente calibrados:

| ID | Nome do Aprendiz | VFUs Executados | Classificação Esperada | Recomendação Pedagógica | Comportamento do Caso / Justificativa |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **C01** | Ana Silva | **0** | `completamente_correto` | **Proceed** | **Perfeito:** Submissão inicial impecável. Traz sistema tático (4-3-3), dados estatísticos exatos do scout e relação causal clara. O sistema valida 0 gaps e aprova de primeira. |
| **C02** | Bruno Oliveira | **0** | `completamente_incorreto` | **Rework** | **Nulo/Superficial:** Texto genérico baseado apenas em placar final e clichês ("jogou bem porque venceu"). A ausência de evidência é tão brutal que o sistema recusa gastar tokens com VFUs e reprova direto. |
| **C03** | Carla Mendes | **1** | `completamente_correto` | **Proceed** | **Ajuste de Escala:** Traz uma ótima análise, mas erra ou oculta a origem/escala das métricas de posse de bola. Toma **1 VFU**, responde corrigindo o dado e avança com sucesso. |
| **C04** | Diego Ferreira | **1** | `completamente_incorreto` | **Rework** | **Falsa Maestria Frouxa:** Linguagem rebuscada que confunde a configuração tática com o desempenho real. Toma **1 VFU** para explicar a causa-efeito, falha em fundamentar e cai no filtro. |
| **C05** | Eva Costa | **2** | `completamente_correto` | **Proceed** | **Evolução Gradual:** Submissão inicial crua. Na VFU 1, traz os dados secos mas sem tática. Na VFU 2, após nova pressão da IA, detalha a mecânica defensiva (pressão pós-perda), conquistando a aprovação no limite do orçamento. |
| **C06** | Fernando Lima | **2** | `completamente_incorreto` | **Rework** | **Teimosia Teórica:** Inicia defendendo uma tese inconsistente. Passa pela VFU 1 entregando dados rasos, mas na VFU 2 abandona a lógica técnica e apela para o senso comum ("venceu por raça"). Reprovado após esgotar o orçamento. |

---

## 💻 6. Stack Tecnológica & Ferramentas

* **Backend:** Python 3.10+ / Flask v3.1.0 (API Rest leve e modular)
* **Servidor WSGI:** Gunicorn v22.0.0 (Pronto para ambiente de produção)
* **IA Motor:** Google GenAI SDK v1.16.0 / Modelo **Gemini-3.1-Flash-Lite**
* **Frontend:** HTML5 nativo, CSS3 estruturado com CSS Variables (Dark Theme) e Vanilla Enterprise JavaScript (Fetch API assíncrona)
* **Segurança de Comunicação:** Flask-CORS integrado para liberação segura de chamadas cross-origin.

---

## 🚀 7. Como Executar o Projeto Localmente

### Pré-requisitos
* Python 3.10 ou superior instalado.
* Uma chave de API do Google Gemini (`GEMINI_API_KEY`).

### Passo 1: Clonar o Repositório e Configurar o Ambiente do Backend
```bash
# Clonar o repositório
git clone [https://github.com/vinicamargors/ai_p2_fatec.git](https://github.com/vinicamargors/ai_p2_fatec.git)
cd ai_p2_fatec/backend

# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
# No Linux/macOS:
source venv/bin/activate
# No Windows (PowerShell):
.\\venv\\Scripts\\Activate.ps1

# Instalar as dependências estritas
pip install -r requirements.txt
Passo 2: Configurar as Variáveis de Ambiente
Crie um arquivo chamado .env dentro da pasta /backend:

Snippet de código
GEMINI_API_KEY=seu_token_real_da_google_aqui
GEMINI_MODEL=gemini-3.1-flash-lite
PORT=5000
Passo 3: Inicializar a API do Backend
Bash
python app.py
O servidor backend estará rodando localmente em http://localhost:5000. Você pode validar a saúde da API acessando o endpoint http://localhost:5000/api/health.

Passo 4: Executar o Frontend
Como o frontend foi desenvolvido utilizando Vanilla JavaScript puro e otimizado, você não precisa instalar pacotes do npm.

Certifique-se de que a variável API_URL no arquivo frontend/js/api.js está apontando para o seu backend local:

JavaScript
const API_URL = "http://localhost:5000/api";
Abra o arquivo frontend/index.html diretamente em qualquer navegador moderno ou utilize a extensão Live Server do VS Code.

🐳 8. Deploy e Conteinerização (Nível Produção)
O projeto está totalmente configurado para deploy automatizado na plataforma Render, dividido em duas arquiteturas isoladas:

Backend (Web Service Linux): Configurado via Procfile nativo disparando o servidor WSGI de alta performance:

Plaintext
web: gunicorn app:app
Frontend (Static Site conteinerizado via Docker): O repositório possui um Dockerfile otimizado que encapsula o código estático em um servidor Nginx ultra-leve rodando em ambiente Alpine Linux, tratando dinamicamente as portas de escuta injetadas pelo ambiente.

👥 9. Autores e Desenvolvimento
Trabalho desenvolvido como entrega oficial da disciplina de Inteligência Artificial da FATEC Carapicuíba (2026).

Vinicius Camargo - PO & Desenvolvimento Geral do Sistema

Este projeto é protegido sob a licença MIT. Sinta-se livre para clonar, estudar e evoluir a esteira de controle de estados!
