<template>
  <div class="container-fluid">
    <!-- Título da Lista de Propriedades -->
    <h1 v-if="!showForm" class="titulo-tela">Lista de Propriedades</h1>
    <!-- Formulário de cadastro/edição de propriedades -->
    <div v-if="showForm" class="form-container">
      <h1 class="titulo-tela">{{ editingPropriedade ? 'Editar Propriedade' : 'Cadastro de Propriedade' }}</h1>
      <form @submit.prevent="submitForm" class="tela-form">
        <!-- Campo para o Produtor -->
        <div class="mb-3">
          <label for="produtor" class="form-label">Produtor</label>
          <select id="produtor" v-model="formData.produtor" class="form-control" required>
            <option disabled value="">Selecione um produtor</option>
            <option v-for="produtor in produtores" :key="produtor.id" :value="produtor.id">
              {{ produtor.nome }}
            </option>
          </select>
        </div>
        <!-- Campo para o Nome -->
        <div class="mb-3">
          <label for="nome" class="form-label">Nome</label>
          <input type="text" class="form-control" id="nome" v-model="formData.nome"
            placeholder="Digite o nome da propriedade" required />
        </div>
        <!-- Campo para a Latitude -->
        <div class="mb-3">
          <label for="latitude" class="form-label">Latitude</label>
          <input type="number" step="0.000001" min="-90" max="90" class="form-control" id="latitude" v-model="formData.latitude" placeholder="ex: 12.3456789"
            required />
        </div>
        <!-- Campo para a Longitude -->
        <div class="mb-3">
          <label for="longitude" class="form-label">Longitude</label>
          <input type="number" step="0.000001" min="-180" max="180" class="form-control" id="longitude" v-model="formData.longitude"
            placeholder="ex: 98.7654321" required />
        </div>
        <!-- Campo para o Endereço -->
        <div class="mb-3">
          <label for="endereco" class="form-label">Endereço</label>
          <input type="text" class="form-control" id="endereco" v-model="formData.endereco"
            placeholder="Digite seu endereço" required />
        </div>
        <!-- Campo para a Cidade -->
        <div class="mb-3">
          <label for="cidade" class="form-label">Cidade</label>
          <input type="text" class="form-control" id="cidade" v-model="formData.cidade" placeholder="Digite sua cidade"
            required />
        </div>
        <!-- Campo para o Estado -->
        <div class="mb-3">
          <label for="estado" class="form-label">Estado</label>
          <select class="form-control" id="estado" v-model="formData.estado" required>
            <option disabled value="">Selecione o estado</option>
            <option v-for="uf in UFS" :key="uf" :value="uf">{{ uf }}</option>
          </select>
        </div>
        <!-- Botões de ação -->
        <div class="button-group">
          <button @click="toggleForm" class="btn-back">Voltar</button>
          <button type="submit" class="btn-submit">{{ editingPropriedade ? 'Salvar' : 'Cadastrar' }}</button>
        </div>
      </form>
    </div>
    <!-- Lista de propriedades -->
    <div v-if="!showForm" class="lista-container mt-5">
      <!-- Botão para abrir o formulário de cadastro, sempre visível -->
      <div>
        <div class="button-container">
          <button @click="toggleForm" class="btn-submit">Cadastrar nova Propriedade</button>
        </div>
        <div v-if="propriedades.length">
          <div class="row lista-cabecalho mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Produtor</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Nome</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Endereço</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Cidade</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Latitude</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Longitude</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Estado</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Ação</div>
          </div>
          <div v-for="propriedade in propriedades" :key="propriedade.id" class="row lista-linha mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ getProdutorNome(propriedade.produtor) }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ propriedade.nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ propriedade.endereco }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ propriedade.cidade }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ propriedade.latitude }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ propriedade.longitude }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ propriedade.estado }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">
              <button @click="startEditing(propriedade)" class="btn-edit">🖊️</button>
              <button @click="deletePropriedade(propriedade.id)" class="btn-delete">🗑️</button>
            </div>
          </div>
        </div>
        <div v-else>
          <p>Nenhuma propriedade encontrada.</p>
        </div>
      <PaginacaoLista :pagina="pagina" :total-paginas="paginacao.totalPaginas"
        :total="paginacao.total" @mudar="irParaPagina" />

      </div>
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
import { UFS } from '@/ufs';

export default {
  components: { PaginacaoLista },
  mixins: [listaPaginada],
  data() {
    return {
      UFS,
      formData: {
        produtor: '',
        nome: '',
        longitude: '',
        latitude: '',
        endereco: '',
        cidade: '',
        estado: '',
      },
      propriedades: [],
      produtores: [],
      showForm: false,
      editingPropriedade: false,
    };
  },
  methods: {
    // Exigido pelo mixin listaPaginada: como recarregar após trocar de página.
    recarregar() {
      this.fetchPropriedades();
    },
    toggleForm() {
      this.showForm = !this.showForm;
      this.editingPropriedade = false;
      this.formData = {
        produtor: '',
        nome: '',
        longitude: '',
        latitude: '',
        endereco: '',
        cidade: '',
        estado: '',
      };
    },
    getProdutorNome(produtorId) {
      const produtor = this.produtores.find(u => u.id === produtorId);
      return produtor ? produtor.nome : 'Desconhecido';
    },
    async fetchPropriedades() {
      try {
        const response = await api.get(`/propriedades/?page=${this.pagina}`);
                this.propriedades = this.aplicarPaginacao(response)
      } catch (error) {
        console.error('Erro ao buscar propriedades:', error);
      }
    },
    async fetchProdutores() {
      try {
        const response = await api.get('/produtores/' + PARAMS_LISTA_COMPLETA);
        this.produtores = extrairLista(response)
      } catch (error) {
        console.error('Erro ao buscar produtores:', error);
      }
    },
    async submitForm() {
      try {
        if (this.editingPropriedade) {
          const response = await api.put(`/propriedades/${this.formData.id}/`, this.formData);
          if (response.status === 200) {
            sucesso('Propriedade atualizada com sucesso!');
            this.fetchPropriedades();
            this.toggleForm();
          } else {
            erro('Erro ao atualizar propriedade.');
          }
        } else {
          const response = await api.post('/propriedades/', this.formData);
          if (response.status === 201) {
            sucesso('Propriedade cadastrada com sucesso!');
            this.propriedades.push(response.data);
            this.toggleForm();
          } else {
            erro('Erro ao cadastrar propriedade. Tente novamente mais tarde.');
          }
        }
      } catch (error) {
        console.error('Erro ao enviar requisição:', error);
        erro(mensagemDeErro(error));
      }
    },
    startEditing(propriedade) {
      this.formData = { ...propriedade };
      this.showForm = true;
      this.editingPropriedade = true;
    },
    async deletePropriedade(propriedadeId) {
      if (!await confirmar('Tem certeza que deseja deletar esta propriedade?')) return;
      try {
        const response = await api.delete(`/propriedades/${propriedadeId}/`);
        if (response.status === 204) {
          sucesso('Propriedade deletada com sucesso!');
          this.fetchPropriedades();
        } else {
          erro('Erro ao deletar propriedade.');
        }
      } catch (error) {
        console.error('Erro ao deletar propriedade:', error);
        erro(mensagemDeErro(error));
      }
    },
  },
  mounted() {
    this.fetchProdutores();
    this.fetchPropriedades();
  },
};
</script>
