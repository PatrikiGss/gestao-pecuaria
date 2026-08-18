<template>
    <div class="change-password-form">
      <h2>Alterar Senha</h2>
      <form @submit.prevent="submitPasswordChange">
        <div class="form-group">
          <label for="oldPassword"></label>
          <input class="input" type="password" id="oldPassword" v-model="oldPassword" required placeholder="Senha Atual" />
        </div>
        <div class="form-group">
          <label for="newPassword"></label>
          <input class="input" type="password" id="newPassword" v-model="newPassword" required placeholder="Nova Senha" />
        </div>
        <button type="submit" class="envio">Alterar Senha</button>
        <button type="button" class="cancelar" @click="cancel">Cancelar</button>
      </form>
      <p v-if="message" :class="{'text-success': messageType === 'success', 'text-danger': messageType === 'error'}">
        {{ message }}
      </p>
    </div>
  </template>
  
  <script>
  import api from '@/interceptadorAxios';
  
  export default {
    data() {
      return {
        oldPassword: "",
        newPassword: "",
        message: "",
        messageType: ""
      };
    },
    methods: {
      async submitPasswordChange() {
        try {
          await api.post("/autenticacao/alterar-senha/", {
            old_password: this.oldPassword,
            new_password: this.newPassword
          });
          alert("Senha alterada com sucesso!"
          +" Por favor realize o login novamente.");
          localStorage.removeItem('access_token');
          localStorage.removeItem('nome_usuario');
          this.isAuthenticated = false;
          this.$router.push('/');
          this.messageType = "success";
          this.oldPassword = "";
          this.newPassword = "";
        } catch (error) {
          if (error.response && error.response.status === 401) {
            this.message = "Sessão expirada. Faça login novamente.";
            this.$router.push('/');
            this.messageType = "error";
          } else {
            this.message = "Erro ao alterar a senha. Verifique os dados.";
            this.messageType = "error";
          }
        }
      },
      cancel() {
        this.$router.push('/tela-usuario');
      }
    }
  };
  </script>
  
  <style scoped>
  .change-password-form {
    background-color: rgba(0, 0, 0, 0.9);
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    padding: 80px; 
    border-radius: 20px;
    color: white;
  }
  
  .form-group {
    margin-bottom: 10px; 
  }
  
  .input {
    padding: 15px;
    border: none;
    font-size: 15px;
    border-radius: 10px;
    width: 100%;
    box-sizing: border-box;
  }
  
  .envio, .cancelar {
    background-color: #237837;
    border: none;
    padding: 15px; 
    width: 100%;
    border-radius: 10px;
    font-size: 15px;
    cursor: pointer;
    margin-top: 10px; 
  }
  
  .cancelar {
    background-color: red;
  }
  
  .envio:hover {
    background-color: #218838;
  }
  
  .cancelar:hover {
    background-color: rgb(144, 33, 33);
  }
  
  .text-success {
    color: green;
  }
  
  .text-danger {
    color: red;
  }
  </style>
  