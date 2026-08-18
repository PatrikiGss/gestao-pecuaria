<template>
    <div class="container-fluid">
      <h1>Cadastro de Usuário</h1>
      <div class="form-container">
        <form @submit.prevent="submitForm" class="user-form">
          <!-- Campo para o nome -->
          <div class="mb-3">
            <label for="nome" class="form-label">Nome</label>
            <input type="text" class="form-control" id="nome" v-model="formData.nome" placeholder="Digite seu nome">
          </div>
          <!-- Campo para o email -->
          <div class="mb-3">
            <label for="email" class="form-label">E-mail</label>
            <input type="email" class="form-control" id="email" v-model="formData.email" placeholder="name@example.com">
          </div>
          <!-- Campo para a senha -->
          <div class="mb-3">
            <label for="password" class="form-label">Senha</label>
            <input type="password" class="form-control" id="password" v-model="formData.password" placeholder="Digite sua senha">
          </div>
          <!-- Campo para o telefone -->
          <div class="mb-3">
            <label for="telefone" class="form-label">Telefone</label>
            <input type="text" class="form-control" id="telefone" v-model="formData.telefone" placeholder="(00)00000-0000">
          </div>
          <!-- Campo para o CPF -->
          <div class="mb-3">
            <label for="cpf" class="form-label">CPF</label>
            <input type="text" class="form-control" id="cpf" v-model="formData.cpf" placeholder="Apenas números, EX: 12345678900">
          </div>
          <!-- Campo para os créditos -->
          <div class="mb-3">
            <label for="creditos" class="form-label">Créditos</label>
            <input type="number" class="form-control" id="creditos" v-model="formData.creditos" placeholder="Digite quantidade de crédito">
          </div>
          <!-- Botões para enviar ou voltar -->
          <div class="button-group">
            <button type="button" class="btn-submit" @click="goBack">Voltar</button>
            <span style="margin-right: 10px;"></span> 
            <button type="submit" class="btn-submit">Enviar</button> 
          </div>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'; 
  
  export default {
    data() {
      return {
        formData: { 
          nome: '',
          email: '',
          telefone: '',
          cpf: '',
          password: '',
          creditos: '',
        },
      };
    },
    methods: {
      async submitForm() {
  try {
    const response = await axios.post('http://127.0.0.1:8000/autenticacao/signup/', this.formData);
    if (response.status === 201 || response.status === 200) {
    alert('Cadastro realizado com sucesso!');
    this.$router.push('/'); 
} else {
    alert('Erro ao cadastrar usuário. Tente novamente mais tarde.');
}
  } catch (error) {
    console.error('Erro ao enviar requisição:', error);
    alert('Erro ao enviar requisição. Verifique o console para mais detalhes.');
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
          creditos: '',
        };
      }
    }
  };
  </script>
  
  <style scoped>
  .container-fluid {
    width: 100%;
    padding: 0 15px;
  }
  
  .form-container {
    width: 100%;
    margin: 0 auto;
    padding: 20px;
    background-color: whitesmoke;
    border: 2px solid grey;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .mb-3 {
    margin-bottom: 1rem;
  }
  
  .form-label {
    text-align: left;
    display: block;
    margin-bottom: 0.5rem;
  }
  
  .btn-submit {
    padding: 8px 10px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    background-color: #237837;
    color: white;
  }
  
  .btn-submit:hover {
    background-color: #218838;
  }
  
  .button-group {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
  </style>
  