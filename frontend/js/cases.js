const state = {
  casoAtual: null,
  sessaoId: null,
  vfuIndex: 0,
  casos: [],
};

function getBadgeClassificacao(classificacao) {
  const map = {
    completamente_correto:   "badge-green",
    parcialmente_correto:    "badge-yellow",
    completamente_incorreto: "badge-red",
  };
  return map[classificacao] || "badge-neutro";
}

function getLabelClassificacao(classificacao) {
  const map = {
    completamente_correto:   "✅ Completamente Correto",
    parcialmente_correto:    "🟡 Parcialmente Correto",
    completamente_incorreto: "❌ Completamente Incorreto",
  };
  return map[classificacao] || classificacao;
}

function getCorClassificacao(classificacao) {
  const map = {
    completamente_correto:   "green",
    parcialmente_correto:    "yellow",
    completamente_incorreto: "red",
  };
  return map[classificacao] || "neutro";
}

function getIconeClassificacao(classificacao) {
  const map = {
    completamente_correto:   "✅",
    parcialmente_correto:    "🟡",
    completamente_incorreto: "❌",
  };
  return map[classificacao] || "❓";
}

async function carregarCasos() {
  try {
    const data = await apiGetCasos();
    state.casos = data.casos;
    renderizarListaCasos(data.casos);
  } catch (e) {
    document.getElementById("lista-casos").innerHTML =
      `<div class="loading" style="color:#ef4444">Erro ao carregar casos.<br>Verifique se o backend está rodando.</div>`;
  }
}

function renderizarListaCasos(casos) {
  const lista = document.getElementById("lista-casos");
  lista.innerHTML = "";

  // Casos de demo
  casos.forEach((caso) => {
    lista.appendChild(criarCardCaso(caso));
  });

  // Separador
  const sep = document.createElement("div");
  sep.style.cssText = "border-top: 1px solid rgba(255,255,255,0.08); margin: 0.5rem 0; padding-top: 0.5rem;";
  sep.innerHTML = `<p style="font-size:0.7rem;color:#475569;padding:0 0.5rem;text-transform:uppercase;letter-spacing:0.05em;">Avaliação Livre</p>`;
  lista.appendChild(sep);

  // Card modo livre
  const casoLivre = {
    id: "LIVRE",
    nome: "Avaliação Livre",
    descricao: "Digite sua própria submissão",
    vfus_esperados: "?",
    classificacao_esperada: "livre",
    submissao: "",
    respostas_vfu: [],
  };
  lista.appendChild(criarCardCaso(casoLivre));
}

function criarCardCaso(caso) {
  const card = document.createElement("div");
  card.className = "caso-card";
  card.id = `caso-card-${caso.id}`;
  card.onclick = () => selecionarCaso(caso);

  const isLivre = caso.id === "LIVRE";

  const vfuLabel = isLivre ? "? VFUs"
    : caso.vfus_esperados === 0 ? "0 VFUs"
    : caso.vfus_esperados === 1 ? "1 VFU"
    : "2 VFUs";

  card.innerHTML = `
    <div class="caso-card-header">
      <span class="caso-nome">${caso.nome}</span>
      <span class="badge badge-neutro">${caso.id}</span>
    </div>
    <div class="caso-descricao">${caso.descricao}</div>
    <div class="caso-badges">
      <span class="badge badge-vfu">${vfuLabel}</span>
      ${!isLivre ? `<span class="badge ${getBadgeClassificacao(caso.classificacao_esperada)}">${getLabelClassificacao(caso.classificacao_esperada)}</span>` : `<span class="badge badge-neutro">✏️ Texto livre</span>`}
    </div>
  `;

  return card;
}

function selecionarCaso(caso) {
  document.querySelectorAll(".caso-card").forEach((c) => c.classList.remove("ativo"));
  document.getElementById(`caso-card-${caso.id}`)?.classList.add("ativo");

  state.casoAtual = caso;
  state.sessaoId = null;
  state.vfuIndex = 0;

  mostrarPainelAvaliacao(caso);
}