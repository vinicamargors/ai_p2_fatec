function mostrarPainelAvaliacao(caso) {
  document.getElementById("estado-inicial").classList.add("hidden");
  document.getElementById("painel-avaliacao").classList.remove("hidden");

  document.getElementById("bloco-loading").classList.add("hidden");
  document.getElementById("bloco-vfu").classList.add("hidden");
  document.getElementById("bloco-historico-vfus").classList.add("hidden");
  document.getElementById("bloco-resultado").classList.add("hidden");
  document.getElementById("bloco-resetar").classList.add("hidden");
  document.getElementById("bloco-submissao").classList.remove("hidden");
  document.getElementById("btn-avaliar").disabled = false;
  document.getElementById("historico-vfus-lista").innerHTML = "";

  atualizarEstagio(1);

  document.getElementById("aprendiz-nome").textContent = caso.nome;
  document.getElementById("aprendiz-descricao").textContent = caso.descricao;
  document.getElementById("aprendiz-avatar").textContent = caso.nome.charAt(0).toUpperCase();

  const vfuLabel = caso.vfus_esperados === 0 ? "0 VFUs"
    : caso.vfus_esperados === 1 ? "1 VFU" : "2 VFUs";
  document.getElementById("badge-vfus-esperados").textContent = vfuLabel;

  const badgeClass = getBadgeClassificacao(caso.classificacao_esperada);
  const badgeEl = document.getElementById("badge-classificacao-esperada");
  badgeEl.textContent = getLabelClassificacao(caso.classificacao_esperada);
  badgeEl.className = `badge ${badgeClass}`;

  // Modo demo: mostra submissão do caso
  // Modo livre: mostra textarea editável
  const isModoLivre = caso.id === "LIVRE";
  document.getElementById("texto-submissao").classList.toggle("hidden", isModoLivre);
  document.getElementById("textarea-submissao-livre").classList.toggle("hidden", !isModoLivre);

  if (!isModoLivre) {
    document.getElementById("texto-submissao").textContent = caso.submissao.trim();
  }
}

function atualizarEstagio(ativo) {
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById(`estagio-${i}`);
    el.classList.remove("ativo", "concluido");
    if (i < ativo) el.classList.add("concluido");
    else if (i === ativo) el.classList.add("ativo");
  }
}

async function iniciarAvaliacao() {
  const caso = state.casoAtual;
  if (!caso) return;

  let submissao = "";
  if (caso.id === "LIVRE") {
    submissao = document.getElementById("textarea-submissao-livre").value.trim();
    if (!submissao) {
      alert("Digite a submissão do aprendiz antes de avaliar.");
      return;
    }
  } else {
    submissao = caso.submissao.trim();
  }

  document.getElementById("btn-avaliar").disabled = true;
  document.getElementById("bloco-submissao").classList.add("hidden");
  document.getElementById("bloco-loading").classList.remove("hidden");
  atualizarEstagio(2);

  try {
    const resultado = await apiAvaliar(caso.nome, submissao);
    document.getElementById("bloco-loading").classList.add("hidden");
    processarResultado(resultado);
  } catch (e) {
    document.getElementById("bloco-loading").classList.add("hidden");
    document.getElementById("bloco-submissao").classList.remove("hidden");
    document.getElementById("btn-avaliar").disabled = false;
    atualizarEstagio(1);
    alert("Erro ao conectar com o backend: " + e.message);
  }
}

function processarResultado(resultado) {
  console.log("Resultado recebido:", resultado);

  if (resultado.estado === "aguardando_vfu") {
    state.sessaoId = resultado.sessao_id;
    mostrarVFU(resultado);
  } else if (resultado.estado === "concluido") {
    mostrarResultado(resultado);
  } else {
    alert("Estado inesperado: " + resultado.estado);
  }
}

function mostrarVFU(resultado) {
  atualizarEstagio(3);

  const blocoVfu = document.getElementById("bloco-vfu");
  blocoVfu.classList.remove("hidden");

  document.getElementById("vfu-contador").textContent =
    `VFU ${resultado.numero_vfu}/${resultado.max_vfus}`;

  document.getElementById("vfu-hipotese").textContent =
    resultado.hipotese_diagnostica
      ? `💡 Hipótese atual: ${resultado.hipotese_diagnostica}`
      : "";

  document.getElementById("vfu-pergunta").textContent = resultado.pergunta_vfu;

  // Pré-carrega resposta demo ou deixa vazio para modo livre
  const caso = state.casoAtual;
  const respostaDemo = caso.id === "LIVRE"
    ? ""
    : (caso.respostas_vfu?.[state.vfuIndex] || "");

  const textareaVfu = document.getElementById("textarea-vfu-resposta");
  textareaVfu.value = respostaDemo;
  document.getElementById("btn-responder-vfu").disabled = false;

  blocoVfu.scrollIntoView({ behavior: "smooth" });
}

function adicionarHistoricoVFU(num, pergunta, resposta) {
  const bloco = document.getElementById("bloco-historico-vfus");
  bloco.classList.remove("hidden");

  const lista = document.getElementById("historico-vfus-lista");
  const item = document.createElement("div");
  item.className = "historico-item";
  item.innerHTML = `
    <div class="historico-item-header">VFU ${num}</div>
    <div class="historico-item-pergunta">❓ ${pergunta}</div>
    <div class="historico-item-resposta">💬 ${resposta || "—"}</div>
  `;
  lista.appendChild(item);
}

async function responderVFU() {
  const textareaVfu = document.getElementById("textarea-vfu-resposta");
  const resposta = textareaVfu.value.trim();

  if (!resposta) {
    alert("A resposta não pode estar vazia.");
    return;
  }

  if (!state.sessaoId) {
    alert("Sessão não encontrada. Reinicie a avaliação.");
    return;
  }

  const perguntaAtual = document.getElementById("vfu-pergunta").textContent;
  const numAtual = state.vfuIndex + 1;

  document.getElementById("btn-responder-vfu").disabled = true;
  document.getElementById("bloco-vfu").classList.add("hidden");
  document.getElementById("bloco-loading").classList.remove("hidden");

  adicionarHistoricoVFU(numAtual, perguntaAtual, resposta);
  state.vfuIndex++;

  try {
    const resultado = await apiResponderVFU(state.sessaoId, resposta);
    document.getElementById("bloco-loading").classList.add("hidden");
    processarResultado(resultado);
  } catch (e) {
    document.getElementById("bloco-loading").classList.add("hidden");
    alert("Erro ao enviar resposta VFU: " + e.message);
    document.getElementById("btn-responder-vfu").disabled = false;
  }
}

function mostrarResultado(resultado) {
  atualizarEstagio(4);

  const cor = getCorClassificacao(resultado.classificacao);
  const icone = getIconeClassificacao(resultado.classificacao);
  const label = getLabelClassificacao(resultado.classificacao);

  const card = document.getElementById("resultado-card");
  card.innerHTML = `
    <div class="resultado-classificacao ${cor}">
      <span class="resultado-icon">${icone}</span>
      <div>
        <div class="resultado-label ${cor}">${label}</div>
        <div class="resultado-recomendacao">📌 ${resultado.recomendacao} — ${resultado.recomendacao_descricao}</div>
      </div>
    </div>
    <div class="resultado-detalhe">
      <div class="detalhe-item">
        <div class="detalhe-label">Lacuna Principal</div>
        <div class="detalhe-valor">${resultado.lacuna_principal || "Nenhuma — base evidencial completa."}</div>
      </div>
      <div class="detalhe-item">
        <div class="detalhe-label">Nível de Confiança</div>
        <div class="detalhe-valor">${resultado.nivel_confianca?.toUpperCase() || "—"}</div>
      </div>
      <div class="detalhe-item" style="grid-column: 1 / -1">
        <div class="detalhe-label">Perfil de Deficiência</div>
        <div class="detalhe-valor">${resultado.perfil_deficiencia || "—"}</div>
      </div>
    </div>
    <div class="resultado-racional">
      <strong>📖 Racional:</strong><br>${resultado.racional || "—"}
    </div>
    <div class="resultado-vfus-badge">
      🔎 VFUs realizados: <span class="badge badge-vfu">${resultado.vfus_realizados} de 2</span>
    </div>
  `;

  document.getElementById("bloco-resultado").classList.remove("hidden");
  document.getElementById("bloco-resetar").classList.remove("hidden");
  document.getElementById("bloco-resultado").scrollIntoView({ behavior: "smooth" });
}

function resetarCaso() {
  if (state.casoAtual) {
    state.vfuIndex = 0;
    state.sessaoId = null;
    document.getElementById("historico-vfus-lista").innerHTML = "";
    mostrarPainelAvaliacao(state.casoAtual);
  }
}