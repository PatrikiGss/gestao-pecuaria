import axios from 'axios'
import { getAccessToken, getRefreshToken, atualizarTokens, limparSessao } from '@/sessao'
import { aviso } from '@/notificacoes'

// A URL vinha fixa no codigo ('http://localhost:8000') enquanto os arquivos
// .env definiam VUE_APP_API_URL sem que ninguem lesse a variavel. Agora ela e
// a fonte da verdade, com o localhost apenas como ultimo recurso.
const BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000'

// Rota real do refresh. Antes o interceptador chamava '/token/refresh/', que
// nao existe: a rota esta sob o prefixo '/autenticacao/'. Como o refresh
// sempre devolvia 404, a sessao caia ao fim dos 60 minutos do access token.
const ROTA_REFRESH = '/autenticacao/token/refresh/'

const api = axios.create({ baseURL: BASE_URL })

// Instancia separada e sem interceptadores para renovar o token: usar a
// propria 'api' faria o 401 da renovacao entrar em recursao.
const apiSemInterceptador = axios.create({ baseURL: BASE_URL })

api.interceptors.request.use(
  (config) => {
    const token = getAccessToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Encerra a sessao e volta para o login.
//
// Nao importa o router de proposito: era isso que criava o ciclo
// tela -> interceptador -> router -> tela. Em vez disso dispara um evento que
// o App.vue escuta e transforma em navegacao.
//
// Antes aqui havia um alert() seguido de window.location.assign(), que
// recarregava a pagina inteira. O recarregamento apagaria o aviso antes de
// ser lido, alem de descartar todo o estado da aplicacao sem necessidade -
// a guarda de rota ja impede o acesso as telas protegidas sem token.
function encerrarSessao (mensagem) {
  limparSessao()
  if (mensagem) aviso(mensagem)
  window.dispatchEvent(new CustomEvent('sessao-encerrada'))
}

let renovando = false
let pendentes = []

function notificarPendentes (token) {
  pendentes.forEach((callback) => callback(token))
  pendentes = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const requisicaoOriginal = error.config

    if (!error.response || error.response.status !== 401 || requisicaoOriginal._retry) {
      return Promise.reject(error)
    }

    if (renovando) {
      // Segura a requisicao ate a renovacao em andamento terminar.
      return new Promise((resolve, reject) => {
        pendentes.push((token) => {
          if (!token) {
            reject(error)
            return
          }
          requisicaoOriginal.headers['Authorization'] = `Bearer ${token}`
          resolve(api(requisicaoOriginal))
        })
      })
    }

    requisicaoOriginal._retry = true
    renovando = true

    const refreshToken = getRefreshToken()
    if (!refreshToken) {
      renovando = false
      notificarPendentes(null)
      // Era aqui que estava 'this.router.push', que lancava TypeError porque
      // 'this' e undefined em arrow function no escopo do modulo.
      encerrarSessao()
      return Promise.reject(error)
    }

    try {
      const { data } = await apiSemInterceptador.post(ROTA_REFRESH, { refresh: refreshToken })
      atualizarTokens({ access: data.access, refresh: data.refresh })

      api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`
      requisicaoOriginal.headers['Authorization'] = `Bearer ${data.access}`

      renovando = false
      notificarPendentes(data.access)

      return api(requisicaoOriginal)
    } catch (err) {
      renovando = false
      notificarPendentes(null)
      encerrarSessao('Sua sessão expirou. Por favor, faça login novamente.')
      return Promise.reject(err)
    }
  }
)

export default api
