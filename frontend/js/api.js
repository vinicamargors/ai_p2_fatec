const API_URL = "https://aip2fatec-production.up.railway.app/";

async function apiGetCasos() {
  const res = await fetch(`${API_URL}/casos`);
  if (!res.ok) throw new Error("Erro ao buscar casos");
  return res.json();
}

async function apiAvaliar(nome, submissao) {
  const res = await fetch(`${API_URL}/avaliar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome, submissao }),
  });
  if (!res.ok) throw new Error("Erro ao avaliar submissão");
  return res.json();
}

async function apiResponderVFU(sessaoId, resposta) {
  const res = await fetch(`${API_URL}/responder-vfu`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessao_id: sessaoId, resposta }),
  });
  if (!res.ok) throw new Error("Erro ao responder VFU");
  return res.json();
}
