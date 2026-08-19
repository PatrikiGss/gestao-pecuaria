import { reactive } from 'vue'

// Centraliza as chaves da sessão no localStorage e expõe um estado reativo.
//
// Antes o App.vue rodava um setInterval de 3 segundos só para perguntar se o
// token ainda existia — 1.200 verificações por hora para detectar um evento
// que o próprio código provoca. Agora quem altera a sessão atualiza o estado,
// e a interface reage na hora, sem espera de até 3 segundos.
//
// Este módulo importa apenas o Vue de propósito: é ele que permite ao
// interceptadorAxios limpar a sessão sem importar o router, que era a origem
// da dependência circular (tela → interceptador → router → tela).

const CHAVE_ACCESS = 'access_token'
const CHAVE_REFRESH = 'refresh_token'
const CHAVE_NOME = 'nome_usuario'

// Acesso protegido ao localStorage.
//
// Ele não existe em todo ambiente (o runner de testes não o expõe) e pode
// lançar exceção mesmo no navegador — em modo privado ou com cookies
// bloqueados o acesso é negado. Sem esta proteção, o app inteiro deixa de
// carregar, porque este módulo é lido na inicialização.
function ler (chave) {
  try {
    return typeof localStorage !== 'undefined' ? localStorage.getItem(chave) : null
  } catch (e) {
    return null
  }
}

function gravar (chave, valor) {
  try {
    if (typeof localStorage !== 'undefined') localStorage.setItem(chave, valor)
  } catch (e) {
    console.warn('Não foi possível gravar a sessão no navegador.')
  }
}

function apagar (chave) {
  try {
    if (typeof localStorage !== 'undefined') localStorage.removeItem(chave)
  } catch (e) { /* nada a fazer */ }
}

export const sessao = reactive({
  autenticado: !!ler(CHAVE_ACCESS),
  nome: ler(CHAVE_NOME) || 'Usuário',
})

function sincronizar () {
  sessao.autenticado = !!ler(CHAVE_ACCESS)
  sessao.nome = ler(CHAVE_NOME) || 'Usuário'
}

// Mantém abas irmãs em dia: o evento 'storage' dispara nas OUTRAS abas quando
// esta grava. Sair numa aba passa a refletir nas demais — que era a única
// coisa útil que o setInterval fazia, agora sem custo enquanto nada acontece.
if (typeof window !== 'undefined' && window.addEventListener) {
  window.addEventListener('storage', (evento) => {
    if ([CHAVE_ACCESS, CHAVE_REFRESH, CHAVE_NOME].includes(evento.key)) sincronizar()
  })
}

export function getAccessToken () {
  return ler(CHAVE_ACCESS)
}

export function getRefreshToken () {
  return ler(CHAVE_REFRESH)
}

export function getNomeUsuario () {
  return ler(CHAVE_NOME) || 'Usuário'
}

export function estaAutenticado () {
  return !!getAccessToken()
}

export function salvarSessao ({ access, refresh, nome }) {
  if (access) gravar(CHAVE_ACCESS, access)
  if (refresh) gravar(CHAVE_REFRESH, refresh)
  if (nome) gravar(CHAVE_NOME, nome)
  sincronizar()
}

export function atualizarTokens ({ access, refresh }) {
  if (access) gravar(CHAVE_ACCESS, access)
  // A rotação do simplejwt devolve um refresh novo a cada renovação.
  if (refresh) gravar(CHAVE_REFRESH, refresh)
  sincronizar()
}

export function limparSessao () {
  apagar(CHAVE_ACCESS)
  apagar(CHAVE_REFRESH)
  apagar(CHAVE_NOME)
  sincronizar()
}
