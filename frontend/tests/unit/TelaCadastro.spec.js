import { expect } from 'chai'
import { shallowMount } from '@vue/test-utils'
import TelaCadastro from '@/views/TelaCadastro.vue'

// TelaCadastro usa axios diretamente, entao nao passa pelo interceptadorAxios.
// Telas que importam '@/interceptadorAxios' caem numa dependencia circular
// (interceptador -> router -> tela) e nao sao montaveis em teste hoje.
describe('TelaCadastro.vue', () => {
  it('renderiza o formulario de cadastro', () => {
    const wrapper = shallowMount(TelaCadastro)
    expect(wrapper.text()).to.include('Cadastro de Usuário')
    expect(wrapper.findAll('input')).to.have.lengthOf(6)
  })

  it('limpa o formulario ao chamar clearForm', async () => {
    const wrapper = shallowMount(TelaCadastro)
    await wrapper.setData({
      formData: {
        nome: 'Fulano',
        email: 'fulano@teste.com',
        telefone: '11988887777',
        cpf: '12345678900',
        password: 'senha12345',
        creditos: 10
      }
    })
    expect(wrapper.vm.formData.nome).to.equal('Fulano')

    wrapper.vm.clearForm()
    expect(wrapper.vm.formData.nome).to.equal('')
    expect(wrapper.vm.formData.email).to.equal('')
    expect(wrapper.vm.formData.creditos).to.equal('')
  })
})
