<template>
  <div class="container-fluid">
    <!-- Título da Lista de Produtores -->
    <h1 v-if="!showForm" class="titulo-tela">Lista de Produtores</h1>
    <!-- Formulário de cadastro/edição de produtores -->
    <div v-if="showForm" class="form-container">
      <h1 class="titulo-tela">{{ editingProdutor ? 'Editar Produtor' : 'Cadastro de Produtor' }}</h1>
      <form @submit.prevent="submitForm" class="tela-form">
        <!-- O usuário é preenchido pelo servidor (perform_create): não faz
             sentido escolher, já que só existe o próprio. -->
        <!-- Campo para o CPF -->
        <div class="mb-3">
          <label for="cpf" class="form-label">CPF</label>
          <input type="text" class="form-control" id="cpf" v-model="formData.cpf" placeholder="Digite apenas os números"
            required maxlength="14" />
        </div>
        <!-- Campo para o nome -->
        <div class="mb-3">
          <label for="nome" class="form-label">Nome</label>
          <input type="text" class="form-control" id="nome" v-model="formData.nome"
            placeholder="Digite seu nome completo" required />
        </div>
        <!-- Campo para o telefone -->
        <div class="mb-3">
          <label for="telefone" class="form-label">Telefone</label>
          <input type="text" class="form-control" id="telefone" v-model="formData.telefone"
            placeholder="Ex: (49)123112233" required maxlength="15" />
        </div>
        <!-- Campo para o email -->
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input type="email" class="form-control" id="email" v-model="formData.email" placeholder="Ex: email@gmail.com"
            required />
        </div>
        <!-- Botões de ação -->
        <div class="button-group">
          <button @click="toggleForm" class="btn-back">Voltar</button>
          <button type="submit" class="btn-submit">{{ editingProdutor ? 'Salvar' : 'Cadastrar' }}</button>
        </div>
      </form>
    </div>

    <!-- Lista de produtores -->
    <div v-if="!showForm" class="lista-container mt-5">
      <!-- Botão para abrir o formulário de cadastro -->
      <div v-if="!showForm" class="button-container">
        <button @click="toggleForm" class="btn-submit">Cadastrar Novo Produtor</button>
      </div>
      <div v-if="produtores.length">
        <div class="container-fluid">
          <div class="row lista-cabecalho mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Usuário</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">CPF</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Nome</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Telefone</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Email</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Ações</div>
          </div>
          <div v-for="produtor in produtores" :key="produtor.id" class="row lista-linha mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ getUsuarioNome(produtor.usuario) }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ produtor.cpf }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ produtor.nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ produtor.telefone }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ produtor.email }}</div>
            <!-- Botões para editar e excluir produtores -->
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">
              <button @click="startEditing(produtor)" class="btn-edit">🖊️</button>
              <button @click="deleteProdutor(produtor.id)" class="btn-delete">🗑️</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <p>Nenhum produtor encontrado.</p>
      </div>
      <PaginacaoLista :pagina="pagina" :total-paginas="paginacao.totalPaginas"
        :total="paginacao.total" @mudar="irParaPagina" />

    </div>
  </div>
</template>

<script>
import api from '@/interceptadorAxios';
import { confirmar, erro, sucesso } from '@/notificacoes';
import PaginacaoLista from '@/components/PaginacaoLista.vue';
import listaPaginada from '@/mixins/listaPaginada';
import { getNomeUsuario } from '@/sessao';
import { mensagemDeErro } from '@/erros';

export default {
  components: { PaginacaoLista },
  mixins: [listaPaginada],
  data() {
    return {
      showForm: false,
      formData: {
        // usuario: '',
        cpf: '',
        nome: '',
        telefone: '',
        email: ''
      },
      produtores: [],
      editingProdutor: false,
    };
  },
  methods: {
    // Exigido pelo mixin listaPaginada: como recarregar após trocar de página.
    recarregar() {
      this.fetchProdutores();
    },
    toggleForm() {
      this.showForm = !this.showForm;
      this.editingProdutor = false;
      this.formData = { usuario: '', cpf: '', nome: '', telefone: '', email: '' };
    },
    getUsuarioNome() {
      // Todo registro pertence ao usuário logado (o backend filtra por ele),
      // então o nome vem da sessão em vez de uma requisição a /usuarios/,
      // que devolvia uma lista de um item só.
      return getNomeUsuario();
    },
    async fetchProdutores() {
      try {
        const response = await api.get(`/produtores/?page=${this.pagina}`);
                this.produtores = this.aplicarPaginacao(response)
      } catch (error) {
        console.error('Erro ao buscar produtores:', error);
      }
    },
    async submitForm() {
  try {
    // O bloco 'config' que existia aqui lia localStorage.getItem('token'),
    // chave que nunca foi gravada (o login grava 'access_token'), e montava
    // 'Authorization: Bearer null'. O cabecalho correto ja e injetado pelo
    // interceptador em toda requisicao.
    if (this.editingProdutor) {
      const response = await api.put(`/produtores/${this.formData.id}/`, this.formData);
      if (response.status === 200) {
        sucesso('Produtor atualizado com sucesso!');
        this.fetchProdutores();
        this.toggleForm();
      } else {
        erro('Erro ao atualizar produtor.');
      }
    } else {
      // Cadastra um novo produtor
      const response = await api.post('/produtores/', this.formData);
      if (response.status === 201) {
        sucesso('Produtor cadastrado com sucesso!');
        this.produtores.push(response.data);
        this.toggleForm();
      } else {
        erro('Erro ao cadastrar produtor. Tente novamente mais tarde.');
      }
    }
  } catch (error) {
    console.error('Erro ao enviar requisição:', error);
    erro(mensagemDeErro(error));
  }
},
    // Inicia o modo de edição
    startEditing(produtor) {
      this.showForm = true;
      this.editingProdutor = true;
      this.formData = { ...produtor };
    },
    // Deleta um produtor
    async deleteProdutor(produtorId) {
      if (!await confirmar('Tem certeza que deseja deletar este produtor?')) {
        return;
      }
      try {
        const response = await api.delete(`/produtores/${produtorId}/`);
        if (response.status === 204) {
          sucesso('Produtor deletado com sucesso!');
          this.produtores = this.produtores.filter(p => p.id !== produtorId);
        } else {
          erro('Erro ao deletar produtor.');
        }
      } catch (error) {
        console.error('Erro ao deletar produtor:', error);
        erro(mensagemDeErro(error));
      }
    }
  },
  mounted() {
    this.fetchProdutores();
  }
};
</script>
