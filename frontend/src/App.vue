<template>
  <div id="app">
    <nav v-if="isAuthenticated" class="nav-bar">
      <div class="nav-container">
        <div class="dropdown">
          <button class="btn dropdown-toggle nav-button" type="button" id="dropdownMenuButton" data-bs-toggle="dropdown" aria-expanded="false">
            ☰
          </button>
          <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton">
            <li><router-link class="dropdown-item" to="/">Home</router-link></li>
            <li><router-link class="dropdown-item" to="/tela-usuario">Usuário</router-link></li>
            <li><router-link class="dropdown-item" to="/tela-produtor">Produtor</router-link></li>
            <li><router-link class="dropdown-item" to="/tela-propriedade">Propriedade</router-link></li>
            <li><router-link class="dropdown-item" to="/tela-gleba">Glebas</router-link></li>
            <li><router-link class="dropdown-item" to="/tela-laboratorio">Laboratório</router-link></li>
            <li><router-link class="dropdown-item" to="/tela-cultura">Cultura</router-link></li>
            <li><router-link class="dropdown-item" to="/tela-calcario">Calcários</router-link></li>
            <li><router-link class="dropdown-item" to="/tela-analise-solo">Análise Solo</router-link></li>
            <li><router-link class="dropdown-item" to="/tela-recomendacoes">Recomendação</router-link></li>
          </ul>
        </div>
        <span class="current-name">{{ currentName }}</span>
      </div>
      <div class="lista-linha">
        <div class="dropdown">
          <button class="btn dropdown-toggle logout-button user-name" type="button" id="logoutDropdown" data-bs-toggle="dropdown" aria-expanded="false">
            <span class="user-name">{{ nome }}</span> 
          </button>
          <ul class="dropdown-menu" aria-labelledby="logoutDropdown">
            <li><button class="dropdown-item" @click="confirmLogout">Logout</button></li>
            <li><button class="dropdown-item" @click="changepassword">Alterar Senha</button></li>
          </ul>
        </div>
      </div>
    </nav>
    <router-view />

    <!-- Substituem alert() e confirm() do navegador, que travavam a aba
         inteira e não aceitavam estilo. -->
    <AvisosFlutuantes />
    <ConfirmacaoDialogo />
  </div>
</template>

<script>
import api from '@/interceptadorAxios';
import AvisosFlutuantes from '@/components/AvisosFlutuantes.vue';
import ConfirmacaoDialogo from '@/components/ConfirmacaoDialogo.vue';
import { confirmar, erro } from '@/notificacoes';
import { sessao, getRefreshToken, limparSessao } from '@/sessao';

export default {
  name: 'App',
  components: { AvisosFlutuantes, ConfirmacaoDialogo },
  data() {
    return {
      currentName: '',
      // Estado reativo compartilhado. Substitui o setInterval de 3 segundos
      // que perguntava a cada tique se o token ainda existia: agora quem
      // altera a sessão notifica, e a navbar reage na hora.
      sessao,
    };
  },
  computed: {
    isAuthenticated() {
      return this.sessao.autenticado;
    },
    nome() {
      return this.sessao.nome;
    },
  },
  watch: {
    $route(to) {
      // Usa o titulo declarado na rota; o 'name' era usado direto e aparecia
      // na navbar como 'analiseSolo' e 'recomendação'.
      this.currentName = to.meta.titulo || '';
    }
  },
  mounted() {
    // O interceptadorAxios avisa por evento quando a sessão cai (refresh
    // recusado). Ele não importa o router para não recriar a dependência
    // circular, então a navegação acontece aqui.
    this._aoEncerrarSessao = () => {
      if (this.$route.name !== 'home') this.$router.push('/');
    };
    window.addEventListener('sessao-encerrada', this._aoEncerrarSessao);
  },
  beforeUnmount() {
    window.removeEventListener('sessao-encerrada', this._aoEncerrarSessao);
  },
  methods: {
    async confirmLogout() {
      if (await confirmar('Você deseja encerrar a sessão?', { confirmarTexto: 'Sair' })) {
        this.logoutUsuario();
      }
    },
    async logoutUsuario() {
      // O logout apenas apagava o access_token do localStorage: o
      // refresh_token continuava salvo e valido por 1 dia, e o endpoint de
      // blacklist do backend nunca era chamado. Agora o token e invalidado
      // no servidor antes de limpar a sessao local.
      const refresh = getRefreshToken();
      if (refresh) {
        try {
          await api.post('/autenticacao/logout/', { refresh });
        } catch (falha) {
          // Token ja expirado ou API fora do ar: a sessao local e limpa
          // de qualquer forma, para o logout nunca falhar para o usuário.
          console.warn('Não foi possível invalidar o token no servidor:', falha);
          erro('A sessão foi encerrada aqui, mas o servidor não confirmou.');
        }
      }
      limparSessao();
      this.$router.push('/');
    },
    changepassword(){
      this.$router.push('/tela-edicao');
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

/* Barra de navegação */
.nav-bar {
  background-color: rgb(107, 99, 99); /* Cor escura para a barra */
  width: 100%;
  padding: 10px 0; /* Espaçamento na vertical */
  display: flex;
  justify-content: space-between; /* Coloca os itens nas extremidades */
  align-items: center; /* Centraliza verticalmente */
}

/* Container do dropdown e nome da rota */
.nav-container {
  display: flex;
  align-items: center;
}

/* Botão de navegação (dropdown) */
.nav-button {
  background-color: black;
  color: white;
  border: none;
  margin-left: 20px;
}

.nav-button:hover {
  background-color: #666;
}

/* Container para o nome do usuário e botão de logout */
.lista-linha {
  display: flex;
  align-items: center;
}

/* Nome do usuário */
.user-name {
  margin-right: 10px;
  color: white; /* Cor branca para o nome do usuário */
  font-weight: bold;
}

/* Botão de logout */
.logout-button {
  background-color: transparent;
  color: black !important; /* Força a cor preta no botão de logout */
  border: none;
  padding: 5px 10px;
  margin-right: 20px;
}

.logout-button:hover {
  background-color: #ff4d4d;
  color: rgb(32, 22, 22) !important; /* Muda a cor ao passar o mouse */
}

/* Nome da rota atual */
.current-name {
  margin-left: 10px;
  color: white;
  font-weight: bold;
}

/* Estilo do dropdown */
.dropdown-menu {
  text-align: left;
}
</style>
