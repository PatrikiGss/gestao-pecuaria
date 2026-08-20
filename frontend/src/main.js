import { createApp } from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
import 'bootstrap/dist/css/bootstrap.min.css';
// Estilo base das telas. Vem DEPOIS do Bootstrap para poder sobrescrevê-lo.
import '@/estilos/base.css';
import 'bootstrap';


createApp(App).use(store).use(router).mount('#app')
