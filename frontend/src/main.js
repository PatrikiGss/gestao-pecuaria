import { createApp } from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import 'bootstrap/dist/css/bootstrap.min.css';
// Estilo base das telas. Vem DEPOIS do Bootstrap para poder sobrescrevê-lo.
import '@/estilos/base.css';
import 'bootstrap';

// A store do Vuex saiu daqui. Ela estava registrada mas vazia — sem estado,
// getters, mutations nem actions — e nada no projeto chegou a usar $store.
// O estado compartilhado que existe de fato é o da sessão, e vive em
// src/sessao.js, num objeto reactive() simples.
//
// Se um dia surgir estado que justifique: no Vue 3, a alternativa natural é
// Pinia. Reintroduzir Vuex só faz sentido se houver motivo específico.
createApp(App).use(router).mount('#app')
