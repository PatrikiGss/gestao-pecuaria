import { createRouter, createWebHistory } from 'vue-router'
import TelaLogin from '@/views/TelaLogin.vue'
import TelaCadastro from '@/views/TelaCadastro.vue'
import TelaEdicaoSenha from '@/views/TelaEdicaoSenha.vue'
import TelaUsuario from '@/views/TelaUsuario.vue'
import TelaProdutor from '@/views/TelaProdutor.vue'
import TelaPropriedade from '@/views/TelaPropriedade.vue'
import TelaLaboratorio from '@/views/TelaLaboratorio.vue'
import TelaCultura from '@/views/TelaCultura.vue'
import TelaAnaliseSolo from '@/views/TelaAnaliseSolo.vue'
import TelaRecomendacoes from '@/views/TelaRecomendacoes.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: TelaLogin
  },
  {
    path: '/tela-usuario',
    name: 'usuario',
    component: TelaUsuario
  },
  {
    path: '/tela-produtor',
    name: 'produtor',
    component: TelaProdutor
  },
  {
    path: '/tela-propriedade',
    name: 'propriedade',
    component: TelaPropriedade
  },
  {
    path: '/tela-laboratorio',
    name: 'laboratorio',
    component: TelaLaboratorio
  },
  {
    path: '/tela-cultura',
    name: 'cultura',
    component: TelaCultura
  },
  {
    path: '/tela-analise-solo',
    name: 'analiseSolo',
    component: TelaAnaliseSolo
  },
  {
    path: '/tela-recomendacoes',
    name: 'recomendação',
    component: TelaRecomendacoes
  },
  {
    path: '/tela-cadastro',
    name: 'cadastro',
    component: TelaCadastro
  },
  {
    path: '/tela-edicao',
    name: 'edicaoSenha',
    component: TelaEdicaoSenha
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
