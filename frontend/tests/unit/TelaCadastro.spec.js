import { expect } from 'chai'
import { shallowMount } from '@vue/test-utils'
import TelaCadastro from '@/views/TelaCadastro.vue'

describe('TelaCadastro.vue', () => {
  // Cinco campos: nome, e-mail, senha, telefone e CPF. 'creditos' saiu do
  // formulario porque virou somente-leitura na API, com valor fixo definido
  // pelo servidor (CREDITOS_INICIAIS).
  it('renderiza o formulario de cadastro', () => {
    const wrapper = shallowMount(TelaCadastro)
    expect(wrapper.text()).to.include('Cadastro de Usuário')
    expect(wrapper.findAll('input')).to.have.lengthOf(5)
  })

  it('nao envia creditos no cadastro', () => {
    const wrapper = shallowMount(TelaCadastro)
    expect(wrapper.vm.formData).to.not.have.property('creditos')
  })

  it('limpa o formulario ao chamar clearForm', async () => {
    const wrapper = shallowMount(TelaCadastro)
    await wrapper.setData({
      formData: {
        nome: 'Fulano',
        email: 'fulano@teste.com',
        telefone: '11988887777',
        cpf: '12345678900',
        password: 'senha12345'
      }
    })
    expect(wrapper.vm.formData.nome).to.equal('Fulano')

    wrapper.vm.clearForm()
    expect(wrapper.vm.formData.nome).to.equal('')
    expect(wrapper.vm.formData.email).to.equal('')
    expect(wrapper.vm.formData.cpf).to.equal('')
  })
})
