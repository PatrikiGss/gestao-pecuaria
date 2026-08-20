<template>
    <div class="container-fluid">
      <h1 class="titulo-tela">Cadastro de Usuário</h1>
      <div class="form-container">
        <form @submit.prevent="submitForm" class="tela-form">
          <!-- Campo para o nome -->
          <div class="mb-3">
            <label for="nome" class="form-label">Nome</label>
            <input type="text" class="form-control" id="nome" v-model="formData.nome" placeholder="Digite seu nome" required >
          </div>
          <!-- Campo para o email -->
          <div class="mb-3">
            <label for="email" class="form-label">E-mail</label>
            <input type="email" class="form-control" id="email" v-model="formData.email" placeholder="name@example.com" required >
          </div>
          <!-- Campo para a senha -->
          <div class="mb-3">
            <label for="password" class="form-label">Senha</label>
            <input type="password" class="form-control" id="password" v-model="formData.password" placeholder="Digite sua senha" required >
          </div>
          <!-- Campo para o telefone -->
          <div class="mb-3">
            <label for="telefone" class="form-label">Telefone</label>
            <input type="text" class="form-control" id="telefone" v-model="formData.telefone" placeholder="(00)00000-0000" maxlength="15" required >
          </div>
          <!-- Campo para o CPF -->
          <div class="mb-3">
            <label for="cpf" class="form-label">CPF</label>
            <input type="text" class="form-control" id="cpf" v-model="formData.cpf" placeholder="Apenas números, EX: 12345678900" maxlength="14" required >
          </div>
          <!-- Créditos não é preenchido no cadastro: o valor é fixo e
               definido pelo servidor (CREDITOS_INICIAIS no backend). -->

          <!-- Botões para enviar ou voltar -->
          <div class="button-group">
            <button type="button" class="btn-back" @click="goBack">Voltar</button>
            <button type="submit" class="btn-submit">Enviar</button> 
          </div>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  // Usa a instancia compartilhada em vez do axios cru: era a unica tela com
  // uma segunda URL fixa no codigo ('http://127.0.0.1:8000'), que precisava
  // ser editada a parte sempre que o endereco da API mudava.
  import api from '@/interceptadorAxios';
import { erro, sucesso } from '@/notificacoes';
import { mensagemDeErro } from '@/erros';

  export default {
    data() {
      return {
        formData: { 
          nome: '',
          email: '',
          telefone: '',
          cpf: '',
          password: '',
        },
      };
    },
    methods: {
      async submitForm() {
  try {
    const response = await api.post('/autenticacao/signup/', this.formData);
    if (response.status === 201 || response.status === 200) {
    sucesso('Cadastro realizado com sucesso!');
    this.$router.push('/'); 
} else {
    erro('Erro ao cadastrar usuário. Tente novamente mais tarde.');
}
  } catch (error) {
    console.error('Erro ao enviar requisição:', error);
    erro(mensagemDeErro(error));
  }
},
      goBack() {
        this.$router.push('/'); 
      },
      clearForm() {
        this.formData = {
          nome: '',
          email: '',
          telefone: '',
          cpf: '',
          password: '',
        };
      }
    }
  };
  </script>
