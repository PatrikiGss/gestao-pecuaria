// Leitura de respostas de listagem da API.
//
// A API passou a paginar todas as listagens, então o corpo mudou de
//     [ {...}, {...} ]
// para
//     { count: 137, next: "...?page=2", previous: null, results: [ {...} ] }
//
// 'extrairLista' aceita as duas formas. Isso evita que uma tela quebre
// silenciosamente — iterar com v-for sobre um objeto não renderiza nada e não
// gera erro, que é o pior tipo de falha para diagnosticar.

// Quantidade suficiente para uma lista suspensa de cadastro vir completa numa
// requisição. O teto do servidor é 200 (config/paginacao.py); pedir acima
// disso não traz mais itens.
export const TAMANHO_LISTA_COMPLETA = 200

export function extrairLista (resposta) {
  const dados = resposta && resposta.data !== undefined ? resposta.data : resposta
  if (Array.isArray(dados)) return dados
  if (dados && Array.isArray(dados.results)) return dados.results
  return []
}

// Metadados da paginação, para os controles de página das telas de listagem.
export function extrairPaginacao (resposta, pagina = 1, tamanho = 20) {
  const dados = resposta && resposta.data !== undefined ? resposta.data : resposta
  if (Array.isArray(dados) || !dados) {
    const total = Array.isArray(dados) ? dados.length : 0
    return { total, pagina: 1, totalPaginas: 1, temProxima: false, temAnterior: false }
  }
  const total = dados.count || 0
  return {
    total,
    pagina,
    totalPaginas: Math.max(1, Math.ceil(total / tamanho)),
    temProxima: !!dados.next,
    temAnterior: !!dados.previous,
  }
}

// Sufixo para pedir a lista inteira numa requisição (listas suspensas).
export const PARAMS_LISTA_COMPLETA = `?page_size=${TAMANHO_LISTA_COMPLETA}`
