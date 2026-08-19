import { expect } from 'chai'
import { shallowMount } from '@vue/test-utils'
import TelaLogin from '@/views/TelaLogin.vue'

// Esta tela importa '@/interceptadorAxios'. Enquanto o interceptador
// importava o router, existia o ciclo tela -> interceptador -> router -> tela
// e este arquivo nem chegava a carregar: quebrava com
// "Cannot access '__WEBPACK_DEFAULT_EXPORT__' before initialization".
// O teste existe para garantir que o ciclo nao volte.
describe('TelaLogin.vue', () => {
  it('monta sem esbarrar em dependencia circular', () => {
    const wrapper = shallowMount(TelaLogin)
    expect(wrapper.text()).to.include('Login')
    expect(wrapper.findAll('input')).to.have.lengthOf(2)
  })

  it('alterna a visibilidade da senha', async () => {
    const wrapper = shallowMount(TelaLogin)
    expect(wrapper.vm.passwordType).to.equal('password')

    await wrapper.find('.toggle-password').trigger('click')
    expect(wrapper.vm.passwordType).to.equal('text')

    await wrapper.find('.toggle-password').trigger('click')
    expect(wrapper.vm.passwordType).to.equal('password')
  })
})
