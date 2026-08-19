import { expect } from 'chai'
import {
  salvarSessao,
  limparSessao,
  getAccessToken,
  getRefreshToken,
  estaAutenticado
} from '@/sessao'

// O ambiente de teste (mochapack + jsdom) nao expoe localStorage como global,
// entao usamos um substituto em memoria com a mesma interface.
function criarLocalStorageFalso () {
  const dados = new Map()
  return {
    getItem: (chave) => (dados.has(chave) ? dados.get(chave) : null),
    setItem: (chave, valor) => dados.set(chave, String(valor)),
    removeItem: (chave) => dados.delete(chave),
    clear: () => dados.clear()
  }
}

// O logout apagava 'access_token' e 'nome_usuario' mas esquecia
// 'refresh_token', que seguia valido por 1 dia no navegador.
describe('sessao.js', () => {
  beforeEach(() => {
    global.localStorage = criarLocalStorageFalso()
    limparSessao()
  })

  afterEach(() => {
    delete global.localStorage
  })

  it('salva e le os tres dados da sessao', () => {
    salvarSessao({ access: 'a1', refresh: 'r1', nome: 'Fulano' })
    expect(getAccessToken()).to.equal('a1')
    expect(getRefreshToken()).to.equal('r1')
    expect(estaAutenticado()).to.equal(true)
  })

  it('limpa TODOS os dados, inclusive o refresh_token', () => {
    salvarSessao({ access: 'a1', refresh: 'r1', nome: 'Fulano' })
    limparSessao()
    expect(getAccessToken()).to.equal(null)
    expect(getRefreshToken()).to.equal(null)
    expect(estaAutenticado()).to.equal(false)
  })
})
