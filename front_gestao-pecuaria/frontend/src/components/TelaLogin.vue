<template>
  <div class="login">
    <h1>Login</h1>
    <!-- Campo de entrada para o nome de usuário -->
    <input class="input" v-model="email" type="text" placeholder="email">
    <br><h1></h1>
    <!-- Campo de entrada para a senha -->
    <input class="input" v-model="password" type="password" placeholder="Password">
    <br><h1></h1>
    <div class="cadastro">
      <!-- Botão para abrir o formulário de cadastro -->
      <button class="btn-cadastro" @click="redirectToCadastro">cadastre-se</button>
    </div>
    <div class="envio">
      <!-- Botão para enviar os dados de login -->
      <button class="btn-envio" @click="loginUsuario">enviar</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'; // Importa o axios para fazer requisições HTTP

export default {
  data() {
    return {
      email: '', // Armazena o email do usuário
      password: ''  // Armazena a senha
    };
  },
  methods: {
    // Método para fazer login do usuário
    async loginUsuario() {
      try {
        // Faz a requisição de login
        const response = await axios.post('http://127.0.0.1:8000/autenticacao/token/', {
          email: this.email,
          password: this.password
        });
        // Verifica se a resposta contém o token de acesso (JWT)
        const token = response.data.access;  // Pega o token JWT da resposta

        // Se o token estiver presente, salva-o no localStorage
        if (token) {
          localStorage.setItem('token', token);  // Salva o token no localStorage
          alert("Login realizado com sucesso!");  // Alerta de sucesso
          this.$router.push('/tela-usuario');  // Redireciona para o dashboard ou tela de usuário
        } else {
          alert("Falha ao obter o token de autenticação.");
        }
      } catch (error) {
        // Em caso de erro, exibe uma mensagem apropriada
        console.error("Erro no login:", error);
        alert("Erro no login. Verifique suas credenciais.");  // Alerta em caso de erro
      }
    },
    // Método para redirecionar para a tela de cadastro
    redirectToCadastro() {
      this.$router.push('/tela-cadastro');  // Redireciona para a tela de cadastro
    },
  }
};
</script>


<style scoped>
.login {
  background-color: rgba(0, 0, 0, 0.9);  /* Cor de fundo escura e semi-transparente */
  position: absolute;  /* Posiciona o login de forma absoluta */
  top: 50%;  /* Centraliza verticalmente */
  left: 50%;  /* Centraliza horizontalmente */
  transform: translate(-50%, -50%);  /* Ajusta o centro da caixa */
  padding: 80px;  /* Adiciona espaço interno */
  border-radius: 20px;  /* Bordas arredondadas */
  color: white;  /* Cor do texto */
}
.input {
  padding: 15px;  /* Espaço interno nos campos de entrada */
  border: none;  /* Remove a borda padrão */
  font-size: 15px;  /* Tamanho da fonte */
  border-radius: 10px;  /* Bordas arredondadas nos campos de entrada */
}
.envio {
  text-align: left;  /* Alinha texto à esquerda */
  margin-bottom: 20px;  /* Espaço inferior */
}
.btn-envio {
  background-color: #237837;  /* Cor de fundo do botão de envio */
  border: none;  /* Remove a borda do botão */
  padding: 15px;  /* Espaço interno do botão */
  width: 100%;  /* Largura total */
  border-radius: 10px;  /* Bordas arredondadas */
  font-size: 15px;  /* Tamanho da fonte */
  cursor: pointer;  /* Cursor como ponteiro */
}
.cadastro {
  text-align: left;  /* Alinha texto à esquerda */
  margin-bottom: 20px;  /* Espaço inferior */
}
.btn-cadastro {
  background-color: transparent;  /* Remove o fundo do botão */
  color: white;  /* Cor do texto */
  border: none;  /* Remove a borda do botão */
  width: 100%;  /* Largura total */
  font-size: 15px;  /* Tamanho da fonte */
  cursor: pointer;  /* Cursor como ponteiro */
}
.btn-cadastro:hover {
  color: #ddd;  /* Muda a cor do texto no hover */
}
.btn-envio:hover {
  background-color: #218838;  /* Muda a cor de fundo no hover */
}
</style>
