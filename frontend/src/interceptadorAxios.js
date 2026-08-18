import axios from 'axios';
import router from '@/router'; // Certifique-se de que isso aponte para o seu arquivo de rotas

// Cria uma instância do Axios com a URL base do backend
const api = axios.create({
  baseURL: 'http://localhost:8000', // Substitua pela URL do seu backend
});

// Adiciona um interceptor de requisição para incluir o token JWT
api.interceptors.request.use(
  (config) => {
    // Obtém o token de acesso do localStorage
    const token = localStorage.getItem('access_token');    
    if (token) {
      // Define o cabeçalho Authorization com o token de acesso
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // Lida com erros na requisição
    return Promise.reject(error);
  }
);

// Variáveis para controlar o estado de refresh e requisições pendentes
let isRefreshing = false;
let refreshSubscribers = [];

// Função para notificar as requisições pendentes que o token foi atualizado
function onRefreshed(token) {
  refreshSubscribers.map(callback => callback(token));
}

// Função para adicionar uma nova requisição à lista de pendentes
function addRefreshSubscriber(callback) {
  refreshSubscribers.push(callback);
}

// Interceptor de resposta para lidar com erros de autenticação e renovação de token
api.interceptors.response.use(
  (response) => response, // Retorna a resposta diretamente se estiver tudo ok
  async (error) => {
    const originalRequest = error.config; // Captura a requisição original
    
    // Se o erro for 401 e a requisição ainda não foi tentada novamente
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Se já estiver renovando o token, coloca a requisição em espera
        return new Promise((resolve) => {
          addRefreshSubscriber((token) => {
            // Quando o token for renovado, a requisição original é enviada novamente
            originalRequest.headers['Authorization'] = `Bearer ${token}`;
            resolve(api(originalRequest));
          });
        });
      }

      // Marca a requisição como "retry" para evitar loops
      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        // Se não houver refresh token, redireciona para o login
        localStorage.clear();
        this.router.push('/');
        return Promise.reject(error);
      }

      try {
        // Tenta renovar o token de acesso usando o refresh token
        const response = await axios.post('http://localhost:8000/token/refresh/', {
          refresh: refreshToken,
        });

        // Atualiza o localStorage com o novo token
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);

        // Atualiza o cabeçalho das requisições futuras
        api.defaults.headers['Authorization'] = `Bearer ${response.data.access}`;
        originalRequest.headers['Authorization'] = `Bearer ${response.data.access}`;

        isRefreshing = false;
        onRefreshed(response.data.access); // Notifica as requisições pendentes que o token foi renovado

        return api(originalRequest); 
      } catch (err) {
        isRefreshing = false;
        localStorage.clear(); 
        alert('Sua sessão expirou. Por favor, faça login novamente.');
        router.push('/'); 
      }
    }

    return Promise.reject(error); // Propaga o erro para ser tratado pela chamada original
  }
);

export default api;
