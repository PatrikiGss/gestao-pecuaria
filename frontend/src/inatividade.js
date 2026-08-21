// Encerra a sessão depois de 1 hora sem interação do usuário.
//
// POR QUE ISTO PRECISA EXISTIR NO CLIENTE
//
// A sessão nunca expirava sozinha, e o motivo não era o access token: ele já
// durava 60 minutos. O problema era o refresh token, que valia 1 DIA. Quando o
// access expirava, o interceptador renovava em silêncio e a conta seguia
// aberta — inclusive para quem largou a máquina destravada e foi embora.
//
// Encurtar o refresh no servidor (feito: 2h) resolve o lado da segurança, mas
// não resolve o de comportamento: o servidor não faz ideia se houve interação.
// Uma aba parada e uma aba em uso ativo produzem exatamente o mesmo tráfego
// quando ninguém clica em nada. Só o navegador sabe a diferença, então a regra
// de inatividade mora aqui.
//
// O QUE CONTA COMO ATIVIDADE
//
// Interação deliberada: clique, tecla, rolagem, toque. De propósito NÃO conta
// 'mousemove' — esbarrar na mesa moveria o cursor e manteria a sessão viva
// para sempre, que é justamente o cenário contra o qual isto existe. Também
// não conta requisição à API: a renovação automática de token é tráfego da
// aplicação, não sinal de que há alguém na frente da tela.

const LIMITE_MS = 60 * 60 * 1000

// A verificação é barata (uma leitura e uma subtração), então rodar de meio em
// meio minuto é suficiente: o logout sai no máximo 30s depois da hora cheia.
const INTERVALO_VERIFICACAO_MS = 30 * 1000

// Gravar a cada evento castigaria o localStorage à toa numa rolagem longa.
// Como a folga é de uma hora, atrasar o registro em até 30s não muda nada.
const INTERVALO_GRAVACAO_MS = 30 * 1000

// No localStorage, e não em memória, por dois motivos: sobrevive ao F5, e é
// compartilhado entre as abas. Sem isso, uma aba aberta em segundo plano
// derrubaria a sessão de quem está trabalhando na aba ao lado.
const CHAVE = 'ultima_atividade'

const EVENTOS = ['mousedown', 'keydown', 'wheel', 'touchstart', 'click']

let temporizador = null
let ultimaGravacao = 0
let aoExpirar = null

function ler () {
  try {
    return Number(localStorage.getItem(CHAVE)) || 0
  } catch (e) {
    return 0
  }
}

function gravar (instante) {
  try {
    localStorage.setItem(CHAVE, String(instante))
  } catch (e) { /* modo privado: a vigilância degrada para a sessão atual */ }
}

// Quanto tempo faz que o usuário não interage, em milissegundos.
export function tempoParado () {
  const ultima = ler()
  if (!ultima) return 0
  return Date.now() - ultima
}

export function registrarAtividade (forcar = false) {
  const agora = Date.now()
  if (!forcar && agora - ultimaGravacao < INTERVALO_GRAVACAO_MS) return
  ultimaGravacao = agora
  gravar(agora)
}

export function limparAtividade () {
  ultimaGravacao = 0
  try {
    localStorage.removeItem(CHAVE)
  } catch (e) { /* nada a fazer */ }
}

function verificar () {
  if (tempoParado() < LIMITE_MS) return
  const callback = aoExpirar
  pararVigilancia()
  if (callback) callback()
}

// 'aoExpirar' é chamado uma única vez, quando o limite estoura. A vigilância se
// encerra antes de chamar, para um logout lento não disparar o aviso duas vezes.
export function iniciarVigilancia (callback) {
  pararVigilancia()
  aoExpirar = callback

  // Marca o início da contagem se ainda não houver registro — caso do login,
  // em que ninguém tocou em nada desde que a tela abriu.
  if (!ler()) registrarAtividade(true)

  EVENTOS.forEach((evento) => {
    window.addEventListener(evento, aoInteragir, { passive: true })
  })
  temporizador = setInterval(verificar, INTERVALO_VERIFICACAO_MS)

  // Verifica na hora: cobre o caso de reabrir a aba no dia seguinte, em que a
  // hora já passou muito antes de o primeiro intervalo disparar.
  verificar()
}

export function pararVigilancia () {
  EVENTOS.forEach((evento) => window.removeEventListener(evento, aoInteragir))
  if (temporizador) clearInterval(temporizador)
  temporizador = null
  aoExpirar = null
}

function aoInteragir () {
  registrarAtividade()
}

export const LIMITE_INATIVIDADE_MS = LIMITE_MS
