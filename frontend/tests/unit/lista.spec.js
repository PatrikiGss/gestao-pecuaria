import { expect } from 'chai'
import { extrairLista, extrairPaginacao } from '@/lista'

// A API passou a paginar todas as listagens. Se uma tela receber o objeto
// paginado e tratar como array, o v-for não renderiza nada E não gera erro —
// falha silenciosa. Estes testes fixam o contrato do helper que evita isso.
describe('lista.js', () => {
  it('lê a resposta paginada', () => {
    const resposta = { data: { count: 55, next: '...', previous: null, results: [{ id: 1 }, { id: 2 }] } }
    expect(extrairLista(resposta)).to.have.lengthOf(2)
  })

  it('aceita também resposta em array puro', () => {
    expect(extrairLista({ data: [{ id: 1 }] })).to.have.lengthOf(1)
  })

  it('devolve lista vazia em resposta inesperada', () => {
    expect(extrairLista({ data: null })).to.deep.equal([])
    expect(extrairLista(undefined)).to.deep.equal([])
  })

  it('calcula o total de páginas a partir de count', () => {
    const resposta = { data: { count: 55, next: '...', previous: null, results: [] } }
    const p = extrairPaginacao(resposta, 1, 20)
    expect(p.total).to.equal(55)
    expect(p.totalPaginas).to.equal(3)
    expect(p.temProxima).to.equal(true)
    expect(p.temAnterior).to.equal(false)
  })

  it('trata resposta nao paginada como pagina unica', () => {
    const p = extrairPaginacao({ data: [{ id: 1 }, { id: 2 }] })
    expect(p.totalPaginas).to.equal(1)
    expect(p.temProxima).to.equal(false)
  })
})
