import { createRouter, createWebHistory } from 'vue-router'
import { estaAutenticado } from '@/sessao'
import TelaLogin from '@/views/TelaLogin.vue'
import TelaCadastro from '@/views/TelaCadastro.vue'
import TelaEdicaoSenha from '@/views/TelaEdicaoSenha.vue'
import TelaUsuario from '@/views/TelaUsuario.vue'
import TelaProdutor from '@/views/TelaProdutor.vue'
import TelaPropriedade from '@/views/TelaPropriedade.vue'
import TelaGleba from '@/views/TelaGleba.vue'
import TelaLaboratorio from '@/views/TelaLaboratorio.vue'
import TelaCultura from '@/views/TelaCultura.vue'
import TelaCalcario from '@/views/TelaCalcario.vue'
import TelaAnaliseSolo from '@/views/TelaAnaliseSolo.vue'
import TelaRecomendacoes from '@/views/TelaRecomendacoes.vue'

// 'meta.titulo' e o texto exibido na navbar. Antes o App.vue mostrava o
// 'name' da rota direto, o que colocava 'analiseSolo' e 'recomendação'
// (com acento no identificador) na interface.
const routes = [
  {
    path: '/',
    name: 'home',
    component: TelaLogin,
    // 'fundoDestaque' deixa a imagem de fundo quase sem véu. Só aqui: o
    // cartão de login é escuro e a tela é esparsa. Ver base.css, bloco FUNDO.
    meta: { titulo: 'Login', publica: true, fundoDestaque: true }
  },
  {
    path: '/tela-usuario',
    name: 'usuario',
    component: TelaUsuario,
    meta: { titulo: 'Usuário' }
  },
  {
    path: '/tela-produtor',
    name: 'produtor',
    component: TelaProdutor,
    meta: { titulo: 'Produtor' }
  },
  {
    path: '/tela-propriedade',
    name: 'propriedade',
    component: TelaPropriedade,
    meta: { titulo: 'Propriedade' }
  },
  {
    path: '/tela-gleba',
    name: 'gleba',
    component: TelaGleba,
    meta: { titulo: 'Glebas' }
  },
  {
    path: '/tela-laboratorio',
    name: 'laboratorio',
    component: TelaLaboratorio,
    meta: { titulo: 'Laboratório' }
  },
  {
    path: '/tela-cultura',
    name: 'cultura',
    component: TelaCultura,
    meta: { titulo: 'Cultura' }
  },
  {
    path: '/tela-calcario',
    name: 'calcario',
    component: TelaCalcario,
    meta: { titulo: 'Calcários' }
  },
  {
    path: '/tela-analise-solo',
    name: 'analiseSolo',
    component: TelaAnaliseSolo,
    meta: { titulo: 'Análise de Solo' }
  },
  {
    path: '/tela-recomendacoes',
    name: 'recomendacoes',
    component: TelaRecomendacoes,
    meta: { titulo: 'Recomendações' }
  },
  {
    path: '/tela-cadastro',
    name: 'cadastro',
    component: TelaCadastro,
    meta: { titulo: 'Cadastro', publica: true }
  },
  {
    path: '/tela-edicao',
    name: 'edicaoSenha',
    component: TelaEdicaoSenha,
    meta: { titulo: 'Alterar Senha' }
  },
  {
    // Sem esta rota, um caminho inexistente renderizava uma tela em branco
    // sem nenhum aviso ao usuario.
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Guarda de navegação.
//
// Antes qualquer rota carregava sem token: digitar /tela-usuario na barra de
// endereços montava a tela, que só falhava depois na chamada à API — o usuário
// via uma tela vazia sem explicação. Não era brecha de dados (o backend sempre
// exigiu autenticação), mas era um beco sem saída na interface.
router.beforeEach((para) => {
  const autenticado = estaAutenticado()

  if (para.meta.publica) {
    // Já logado não precisa ver login nem cadastro.
    if (autenticado) return { name: 'usuario' }
    return true
  }

  if (!autenticado) {
    // 'redirect' guarda o destino pretendido para voltar a ele após o login.
    return { name: 'home', query: { redirect: para.fullPath } }
  }

  return true
})

export default router
