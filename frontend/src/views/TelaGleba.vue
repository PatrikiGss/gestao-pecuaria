<template>
  <div class="container-fluid">
    <h1 v-if="!showForm" class="titulo-tela">Lista de Glebas</h1>

    <!-- Formulário de cadastro/edição -->
    <div v-if="showForm" class="form-container">
      <h1 class="titulo-tela">{{ editingGleba ? 'Editar Gleba' : 'Cadastro de Gleba' }}</h1>
      <form @submit.prevent="submitForm" class="tela-form">
        <div class="mb-3">
          <label for="propriedade" class="form-label">Propriedade</label>
          <select id="propriedade" v-model="formData.propriedade" class="form-control" required>
            <option disabled value="">Selecione uma propriedade</option>
            <option v-for="propriedade in propriedades" :key="propriedade.id" :value="propriedade.id">
              {{ propriedade.nome }}
            </option>
          </select>
        </div>
        <div class="mb-3">
          <label for="nome" class="form-label">Nome da gleba</label>
          <input type="text" class="form-control" id="nome" v-model="formData.nome"
            placeholder="Ex: Talhão 3" required>
          <small class="text-muted">
            O nome é único dentro da propriedade e não diferencia maiúsculas de minúsculas.
          </small>
        </div>
        <div v-if="erro" class="alert alert-danger">{{ erro }}</div>
        <div class="button-group">
          <button type="button" @click="toggleForm" class="btn-back">Voltar</button>
          <button type="submit" class="btn-submit">{{ editingGleba ? 'Atualizar' : 'Enviar' }}</button>
        </div>
      </form>
    </div>

    <!-- Listagem -->
    <div v-else class="lista-container">
      <div class="button-container">
        <button @click="toggleForm" class="btn-submit">Cadastrar Nova Gleba</button>
      </div>
      <div v-if="glebas.length">
        <div class="container-fluid">
          <div class="row lista-cabecalho mb-2">
            <div class="col-12 col-sm-6 col-md-4">Gleba</div>
            <div class="col-12 col-sm-6 col-md-4">Propriedade</div>
            <div class="col-12 col-sm-6 col-md-4">Ações</div>
          </div>
          <div v-for="gleba in glebas" :key="gleba.id" class="row lista-linha mb-2">
            <div class="col-12 col-sm-6 col-md-4">{{ gleba.nome }}</div>
            <div class="col-12 col-sm-6 col-md-4">{{ gleba.propriedade_nome }}</div>
            <div class="col-12 col-sm-6 col-md-4">
              <button @click="editGleba(gleba)" class="btn-edit">🖊️</button>
              <button @click="deleteGleba(gleba.id)" class="btn-delete">🗑️</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <p>Nenhuma gleba encontrada.</p>
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
import { mensagemDeErro } from '@/erros';
import { extrairLista, PARAMS_LISTA_COMPLETA } from '@/lista';

export default {
  components: { PaginacaoLista },
  mixins: [listaPaginada],
  data() {
    return {
      showForm: false,
      formData: { nome: '', propriedade: '' },
      glebas: [],
      propriedades: [],
      editingGleba: null,
      erro: '',
    };
  },
  methods: {
    // Exigido pelo mixin listaPaginada: como recarregar após trocar de página.
    recarregar() {
      this.fetchGlebas();
    },
    toggleForm() {
      this.showForm = !this.showForm;
      this.clearForm();
    },
    clearForm() {
      this.formData = { nome: '', propriedade: '' };
      this.editingGleba = null;
      this.erro = '';
    },
    async fetchGlebas() {
      try {
        const response = await api.get(`/glebas/?page=${this.pagina}`);
                this.glebas = this.aplicarPaginacao(response)
      } catch (error) {
        console.error('Erro ao buscar glebas:', error);
      }
    },
    async fetchPropriedades() {
      try {
        const response = await api.get('/propriedades/' + PARAMS_LISTA_COMPLETA);
        this.propriedades = extrairLista(response)
      } catch (error) {
        console.error('Erro ao buscar propriedades:', error);
      }
    },
    async submitForm() {
      this.erro = '';
      try {
        if (this.editingGleba) {
          await api.put(`/glebas/${this.editingGleba}/`, this.formData);
          sucesso('Gleba atualizada com sucesso!');
        } else {
          await api.post('/glebas/', this.formData);
          sucesso('Gleba cadastrada com sucesso!');
        }
        this.fetchGlebas();
        this.showForm = false;
        this.clearForm();
      } catch (error) {
        // A API recusa nome repetido na mesma propriedade; mostra a mensagem
        // dela em vez de um alerta genérico.
        const dados = error.response && error.response.data;
        this.erro = (dados && (dados.nome || dados.detail)) || 'Erro ao salvar a gleba.';
        if (Array.isArray(this.erro)) this.erro = this.erro[0];
        console.error('Erro ao enviar requisição:', error);
      }
    },
    editGleba(gleba) {
      this.editingGleba = gleba.id;
      this.formData = { nome: gleba.nome, propriedade: gleba.propriedade };
      this.erro = '';
      this.showForm = true;
    },
    async deleteGleba(glebaId) {
      if (!await confirmar('Tem certeza que deseja excluir esta gleba?')) return;
      try {
        await api.delete(`/glebas/${glebaId}/`);
        sucesso('Gleba excluída com sucesso!');
        this.fetchGlebas();
      } catch (error) {
        // O backend usa PROTECT e devolve 409 com a contagem do que está
        // vinculado. Antes, esta tela dizia "possui análises de solo
        // vinculadas" para QUALQUER status >= 400 — então uma sessão expirada
        // (401) aparecia como se fosse vínculo de dados.
        console.error('Erro ao excluir gleba:', error);
        erro(mensagemDeErro(error));
      }
    },
  },
  mounted() {
    this.fetchGlebas();
    this.fetchPropriedades();
  },
};
</script>
