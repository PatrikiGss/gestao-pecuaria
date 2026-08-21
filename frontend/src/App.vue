<template>
  <!-- Classe, e não id="app": o index.html já tem um <div id="app">, que é o
       container onde o Vue monta. Repetir o id aqui criava dois elementos com
       o mesmo id — HTML inválido — e fazia toda regra '#app' valer para os
       dois, o que pintava a camada de fundo duas vezes. -->
  <div class="app-raiz" :class="{ 'fundo-destaque': fundoEmDestaque }">
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
    <!-- O miolo cresce para empurrar o rodapé até o fim da janela em páginas
         curtas. Ver a seção 'rodapé' em src/estilos/base.css. -->
    <main class="conteudo">
      <router-view />
    </main>

    <!-- Aparece também nas telas públicas: a navbar some sem sessão, o
         rodapé não deve sumir junto. -->
    <footer class="rodape">
      <span>© {{ ano }} Projeto de pesquisa: AORUS. IFSC Câmpus Lages. Todos os direitos reservados.</span>
      <span>
        Desenvolvido por:
        <a :href="`mailto:${email}`">{{ email }}</a>
      </span>
    </footer>

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
import { aviso, confirmar, erro } from '@/notificacoes';
import { sessao, getRefreshToken, limparSessao } from '@/sessao';
import { iniciarVigilancia, pararVigilancia, limparAtividade } from '@/inatividade';

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
      // Ano em que o projeto foi desenvolvido. Fixo de propósito: o aviso de
      // direitos se refere à autoria da obra, não à data de hoje.
      ano: 2024,
      email: 'patrikigss321@gmail.com',
    };
  },
  computed: {
    isAuthenticated() {
      return this.sessao.autenticado;
    },
    nome() {
      return this.sessao.nome;
    },
    // Telas marcadas com 'fundoDestaque' mostram a imagem quase inteira, com
    // véu escuro. Só o login usa: é a única tela cujo conteúdo é um cartão
    // escuro com texto branco. Nas demais o título fica FORA da caixa, sobre
    // o fundo, e precisa do véu claro para continuar legível.
    fundoEmDestaque() {
      return !!this.$route.meta.fundoDestaque;
    },
  },
  watch: {
    // 'immediate' porque sem ele o título da navbar ficava vazio até a
    // primeira navegação: recarregar a página deixava a barra sem rótulo.
    $route: {
      immediate: true,
      handler(to) {
        // Usa o titulo declarado na rota; o 'name' era usado direto e aparecia
        // na navbar como 'analiseSolo' e 'recomendação'.
        this.currentName = to.meta.titulo || '';
      },
    },
    // A vigilância de inatividade só faz sentido com sessão aberta, e precisa
    // parar quando ela fecha — senão o temporizador continuaria rodando na
    // tela de login, sem nada para encerrar.
    isAuthenticated: {
      immediate: true,
      handler(autenticado) {
        if (autenticado) {
          iniciarVigilancia(() => this.encerrarPorInatividade());
        } else {
          pararVigilancia();
        }
      },
    },
  },
  mounted() {
    // O interceptadorAxios avisa por evento quando a sessão cai (refresh
    // recusado). Ele não importa o router para não recriar a dependência
    // circular, então a navegação acontece aqui.
    this._aoEncerrarSessao = () => {
      pararVigilancia();
      if (this.$route.name !== 'home') this.$router.push('/');
    };
    window.addEventListener('sessao-encerrada', this._aoEncerrarSessao);
  },
  beforeUnmount() {
    window.removeEventListener('sessao-encerrada', this._aoEncerrarSessao);
    pararVigilancia();
  },
  methods: {
    async confirmLogout() {
      if (await confirmar('Você deseja encerrar a sessão?', { confirmarTexto: 'Sair' })) {
        this.logoutUsuario();
      }
    },
    // Encerrada pelo relógio de inatividade (src/inatividade.js), não por
    // clique. Faz o mesmo caminho do logout manual — inclusive a blacklist no
    // servidor — mas explica o motivo, senão o usuário volta do café e encontra
    // a tela de login sem entender o que aconteceu.
    async encerrarPorInatividade() {
      await this.logoutUsuario({ silencioso: true });
      aviso('Sessão encerrada por 1 hora de inatividade. Entre novamente.');
    },
    async logoutUsuario({ silencioso = false } = {}) {
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
          // No logout por inatividade o token já venceu na maioria das vezes,
          // então esse aviso seria ruído sobre algo esperado.
          if (!silencioso) {
            erro('A sessão foi encerrada aqui, mas o servidor não confirmou.');
          }
        }
      }
      pararVigilancia();
      limparAtividade();
      limparSessao();
      // O default do axios guarda o token da última renovação; sem apagar,
      // as próximas requisições sairiam autenticadas depois do logout.
      delete api.defaults.headers.common['Authorization'];
      if (this.$route.name !== 'home') this.$router.push('/');
    },
    changepassword(){
      this.$router.push('/tela-edicao');
    }
  }
};
</script>

<style>
.app-raiz {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

/* Barra de navegação.
   Mesma cor do rodapé: as duas barras emolduram o conteúdo, então dividem o
   token --cor-barra. O cinza-marrom que estava aqui antes não vinha de token
   nenhum e era o único elemento fora da paleta. */
.nav-bar {
  background-color: var(--cor-barra);
  border-bottom: 3px solid var(--cor-primaria);
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

/* Botão de navegação (dropdown).
   Usa o verde primário, o mesmo dos botões de ação das telas, para o menu se
   ler como affordance em vez de mancha.

   O seletor precisa de '.nav-bar' na frente: sozinho, '.nav-button' empata em
   especificidade com o '.btn' do Bootstrap, que é injetado depois e vencia o
   desempate por ordem. O 'background-color: black' que estava aqui antes nunca
   chegou a valer por causa disso. */
.nav-bar .nav-button {
  background-color: var(--cor-primaria);
  color: #fff;
  border: none;
  margin-left: 20px;
}

.nav-bar .nav-button:hover {
  background-color: var(--cor-primaria-hover);
  color: #fff;
}

/* Container para o nome do usuário e botão de logout */
.lista-linha {
  display: flex;
  align-items: center;
}

/* Nome do usuário */
.user-name {
  margin-right: 10px;
  color: var(--cor-barra-texto);
  font-weight: bold;
}

/* Botão de logout.
   O 'color: black' que havia aqui pintava a setinha do dropdown de preto —
   invisível sobre a barra escura. Passa a acompanhar o texto da barra. */
.nav-bar .logout-button {
  background-color: transparent;
  color: var(--cor-barra-texto) !important;
  border: none;
  padding: 5px 10px;
  margin-right: 20px;
  border-radius: var(--raio-pequeno);
}

/* O vermelho de aviso agora sai da paleta (--cor-perigo), em vez de um
   #ff4d4d avulso que brigava com o verde da barra. Mesmo motivo do botão
   acima para o seletor levar '.nav-bar': sem ele, '.btn:hover' do Bootstrap
   empata e ganha por ordem. */
.nav-bar .logout-button:hover {
  background-color: var(--cor-perigo);
  color: #fff !important;
}

.nav-bar .logout-button:hover .user-name {
  color: #fff;
}

/* Nome da rota atual */
.current-name {
  margin-left: 10px;
  color: var(--cor-barra-texto);
  font-weight: bold;
}

/* Estilo do dropdown */
.dropdown-menu {
  text-align: left;
}
</style>
