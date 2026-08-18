<template>
  <div class="login">
    <h1>Login</h1>
    <input class="input" v-model="email" type="text" placeholder="email">
    <br>
    <input class="input" v-model="password" :type="passwordType" placeholder="Password">
    <span class="toggle-password" @click="togglePasswordVisibility">
      <i :class="passwordType === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash'"></i>
    </span>
    <br>
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
    <div class="cadastro">
      <button class="btn-cadastro" @click="redirectToCadastro">cadastre-se</button>
    </div>
    <div class="envio">
      <button class="btn-envio" @click="loginUsuario">enviar</button>
    </div>
  </div>
</template>


<script>
import api from '@/interceptadorAxios'; 

export default {
  data() {
    return {
      email: '',
      password: '',
      passwordType: 'password', 
      errorMessage: '', 
    };
  },
  methods: {
    async loginUsuario() {
      this.errorMessage = ''; 
      try {
        const response = await api.post('/autenticacao/token/', {
          email: this.email,
          password: this.password,
        });

        if (response.status === 200 && response.data.access && response.data.refresh) {
          const accessToken = response.data.access;
          const refreshToken = response.data.refresh;
          alert("login realizado com sucesso!");

          // Armazena os tokens no localStorage
          localStorage.setItem('access_token', accessToken);
          localStorage.setItem('refresh_token', refreshToken);

          const nomeUsuario = await this.obterNomeUsuario();
          localStorage.setItem('nome_usuario', nomeUsuario);

          
          this.$router.push('/tela-usuario');
          window.location.href = '/tela-usuario';
        } else {
          this.errorMessage = 'Falha ao obter os tokens de autenticação.';
          window.location.href = '/';
        }
      } catch (error) {
        console.error('Erro ao realizar login:', error);
        this.errorMessage = 'Erro no login. Verifique suas credenciais.';
        window.location.href = '/';
      }
    },

    // Método para buscar o nome do usuário logado
    async obterNomeUsuario() {
      try {
        const response = await api.get('/autenticacao/meuperfil/');
        return response.data.nome || 'Usuário';
      } catch (error) {
        console.error('Erro ao obter dados do usuário:', error);
        return 'Usuário';
      }
    },

    // Método para redirecionar para a tela de cadastro
    redirectToCadastro() {
      this.$router.push('/tela-cadastro');
    },

    // Alterna a visibilidade da senha
    togglePasswordVisibility() {
      this.passwordType = this.passwordType === 'password' ? 'text' : 'password';
    }
  }
};
</script>

<style scoped>
.login {
  background-color: rgba(0, 0, 0, 0.9);  
  position: absolute; 
  top: 50%; 
  left: 50%;  
  transform: translate(-50%, -50%);  
  padding: 80px;  
  border-radius: 20px;  
  color: white;  
}
.input {
  padding: 15px;
  border: none;
  font-size: 15px;
  border-radius: 10px;
  width: 100%;
  margin-bottom: 20px;
  box-sizing: border-box;
}

.toggle-password {
  position: absolute;
  margin-left: -30px;
  cursor: pointer;
}

.login input[type="text"],
.login input[type="password"] {
  width: calc(100% - 40px);
  padding-right: 40px;
}
.envio {
  text-align: left;
  margin-bottom: 20px;
}
.btn-envio {
  background-color: #237837;
  border: none;
  padding: 15px;
  width: 100%;
  border-radius: 10px;
  font-size: 15px;
  cursor: pointer;
}
.cadastro {
  text-align: left;
  margin-bottom: 20px;
}
.btn-cadastro {
  background-color: transparent;
  color: white;
  border: none;
  width: 100%;
  font-size: 15px;
  cursor: pointer;
}
.btn-cadastro:hover {
  color: #ddd;
}
.btn-envio:hover {
  background-color: #218838;
}

.toggle-password {
  cursor: pointer;
  margin-left: 10px;
}

.error-message {
  color: red;
  margin-top: 10px;
  font-size: 14px;
}
</style>
