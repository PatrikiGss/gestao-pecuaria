import { expect } from 'chai'
import { estado, notificar, dispensar, confirmar, sucesso, erro } from '@/notificacoes'

// Substituem alert() e confirm() em 74 pontos de chamada. A diferença que mais
// importa é o confirmar(): o nativo trava a aba e devolve o valor na hora,
// este devolve uma Promise — quem chama precisa usar 'await'.
describe('notificacoes.js', () => {
  beforeEach(() => {
    estado.avisos.splice(0)
    estado.confirmacao = null
  })

  it('empilha avisos e os identifica por tipo', () => {
    sucesso('Salvo')
    erro('CPF inválido.')
    expect(estado.avisos).to.have.lengthOf(2)
    expect(estado.avisos[0].tipo).to.equal('sucesso')
    expect(estado.avisos[1].tipo).to.equal('erro')
  })

  it('ignora texto vazio', () => {
    notificar('')
    notificar(null)
    expect(estado.avisos).to.have.lengthOf(0)
  })

  it('dispensa um aviso pelo id', () => {
    const id = sucesso('Salvo')
    sucesso('Outro')
    dispensar(id)
    expect(estado.avisos).to.have.lengthOf(1)
    expect(estado.avisos[0].texto).to.equal('Outro')
  })

  it('confirmar resolve true quando confirmado', async () => {
    const promessa = confirmar('Excluir?')
    expect(estado.confirmacao).to.not.equal(null)
    estado.confirmacao.responder(true)
    expect(await promessa).to.equal(true)
    expect(estado.confirmacao).to.equal(null)
  })

  it('confirmar resolve false quando cancelado', async () => {
    const promessa = confirmar('Excluir?')
    estado.confirmacao.responder(false)
    expect(await promessa).to.equal(false)
  })
})
