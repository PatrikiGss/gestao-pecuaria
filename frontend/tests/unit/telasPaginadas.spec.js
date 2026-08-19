import { expect } from 'chai'
import { shallowMount } from '@vue/test-utils'
import api from '@/interceptadorAxios'

import TelaGleba from '@/views/TelaGleba.vue'
import TelaCultura from '@/views/TelaCultura.vue'
import TelaProdutor from '@/views/TelaProdutor.vue'
import TelaPropriedade from '@/views/TelaPropriedade.vue'
import TelaLaboratorio from '@/views/TelaLaboratorio.vue'
import TelaRecomendacoes from '@/views/TelaRecomendacoes.vue'
import TelaAnaliseSolo from '@/views/TelaAnaliseSolo.vue'
import TelaCalcario from '@/views/TelaCalcario.vue'

// Estas telas dependem do mixin listaPaginada para ter 'pagina', 'paginacao',
// 'aplicarPaginacao()' e 'irParaPagina()'.
//
// Houve um caso real em que o estado foi removido do data() das telas mas o
// mixin não chegou a ser registrado: as listagens quebravam em execução com
// "aplicarPaginacao is not a function". Lint, build e os testes de então
// passaram — nenhum deles verifica método ausente na Options API.
//
// Este arquivo existe para fechar essa lacuna: monta cada tela e confere o
// contrato do mixin.
const TELAS = [
  ['TelaGleba', TelaGleba],
  ['TelaCultura', TelaCultura],
  ['TelaProdutor', TelaProdutor],
  ['TelaPropriedade', TelaPropriedade],
  ['TelaLaboratorio', TelaLaboratorio],
  ['TelaRecomendacoes', TelaRecomendacoes],
  ['TelaAnaliseSolo', TelaAnaliseSolo],
  ['TelaCalcario', TelaCalcario],
]

// As telas chamam a API ao montar; sem stub o mocha acusa promessa rejeitada.
const stubs = { PaginacaoLista: true, 'router-link': true, 'router-view': true }

describe('telas paginadas: contrato do mixin listaPaginada', () => {
  let adaptadorOriginal

  // As telas chamam a API no mounted(). Sem isto o jsdom tenta rede de verdade
  // e enche a saída de erro — o que atrapalha enxergar uma falha real.
  before(() => {
    adaptadorOriginal = api.defaults.adapter
    api.defaults.adapter = (config) => Promise.resolve({
      data: { count: 0, next: null, previous: null, results: [] },
      status: 200,
      statusText: 'OK',
      headers: {},
      config,
    })
  })

  after(() => {
    api.defaults.adapter = adaptadorOriginal
  })

  TELAS.forEach(([nome, componente]) => {
    it(`${nome} tem o estado e os métodos de paginação`, () => {
      const wrapper = shallowMount(componente, { global: { stubs } })

      expect(wrapper.vm.pagina, 'pagina').to.be.a('number')
      expect(wrapper.vm.paginacao, 'paginacao').to.be.an('object')
      expect(wrapper.vm.paginacao).to.have.property('totalPaginas')
      expect(wrapper.vm.aplicarPaginacao, 'aplicarPaginacao').to.be.a('function')
      expect(wrapper.vm.irParaPagina, 'irParaPagina').to.be.a('function')
      // O mixin exige que cada tela diga como recarregar a própria lista.
      expect(wrapper.vm.recarregar, 'recarregar').to.be.a('function')
    })
  })

  it('aplicarPaginacao lê a resposta paginada e preenche os metadados', () => {
    const wrapper = shallowMount(TelaGleba, { global: { stubs } })
    const itens = wrapper.vm.aplicarPaginacao({
      data: { count: 42, next: '...', previous: null, results: [{ id: 1 }, { id: 2 }] },
    })

    expect(itens).to.have.lengthOf(2)
    expect(wrapper.vm.paginacao.total).to.equal(42)
    expect(wrapper.vm.paginacao.totalPaginas).to.equal(3)
  })

  it('irParaPagina ignora página fora do intervalo', () => {
    const wrapper = shallowMount(TelaGleba, { global: { stubs } })
    wrapper.vm.paginacao = { total: 5, totalPaginas: 1 }

    wrapper.vm.irParaPagina(0)
    expect(wrapper.vm.pagina).to.equal(1)

    wrapper.vm.irParaPagina(99)
    expect(wrapper.vm.pagina).to.equal(1)
  })
})
