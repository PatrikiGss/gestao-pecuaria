<template>
  <div class="container-fluid">
    <h1></h1>
    <h1 v-if="!showForm"><br>Lista de Recomendações </h1>
    <h1 v-if="!showForm"><br></h1>
    <div v-if="showForm" class="form-container">
      <h1>{{ editingRec ? 'Editar Recomendação' : 'Cadastro de Recomendação' }}</h1>
      <form @submit.prevent="submitForm" class="recomendação-form">
        <!-- Seleção em cascata: propriedade filtra as análises.
             Antes esta tela carregava TODAS as análises do usuário só para
             preencher a lista, o que fica insustentável conforme o histórico
             cresce. Agora só busca as da propriedade escolhida. -->
        <div class="mb-3">
          <label for="propriedade" class="form-label">Propriedade</label>
          <select id="propriedade" v-model="propriedadeSelecionada" class="form-control" required>
            <option disabled value="">Selecione uma propriedade</option>
            <option v-for="propriedade in propriedades" :key="propriedade.id" :value="propriedade.id">
              {{ propriedade.nome }}
            </option>
          </select>
        </div>
        <div class="mb-3">
          <label for="analisesolo" class="form-label">Análise de Solo</label>
          <select id="analisesolo" v-model="formData.analise_solo" class="form-control" required
            :disabled="!propriedadeSelecionada">
            <option disabled value="">
              {{ propriedadeSelecionada ? 'Selecione uma análise' : 'Escolha a propriedade primeiro' }}
            </option>
            <option v-for="analise in analise_solo" :key="analise.id" :value="analise.id">
              {{ analise.data }} — {{ analise.gleba_nome }} — {{ analise.laudo }}
            </option>
          </select>
          <small v-if="propriedadeSelecionada && !analise_solo.length" class="text-muted">
            Nenhuma análise cadastrada nesta propriedade.
          </small>
        </div>

        <!-- Campos para os dados da recomendação -->
        <div class="mb-3">
          <label for="camada_correcao" class="form-label">Camada de Correção</label>
          <input type="text" class="form-control" id="camada_correcao" v-model="formData.camada_correcao"
            placeholder="Informe a camada de correção" required >
        </div>

        <div class="mb-3">
          <label for="calcario_calcitico" class="form-label">Calcário Calcítico</label>
          <input type="number" step="0.01" min="0" class="form-control" id="calcario_calcitico" v-model="formData.calcario_calcitico"
            placeholder="Informe a quantidade de calcário calcítico" required >
        </div>

        <div class="mb-3">
          <label for="calcario_dolomitico" class="form-label">Calcário Dolomítico</label>
          <input type="number" step="0.01" min="0" class="form-control" id="calcario_dolomitico" v-model="formData.calcario_dolomitico"
            placeholder="Informe a quantidade de calcário dolomítico" required >
        </div>

        <div class="mb-3">
          <label for="calcario_magnesiano" class="form-label">Calcário Magnesiano</label>
          <input type="number" step="0.01" min="0" class="form-control" id="calcario_magnesiano" v-model="formData.calcario_magnesiano"
            placeholder="Informe a quantidade de calcário magnesiano" required >
        </div>

        <div class="mb-3">
          <label for="gesso" class="form-label">Gesso</label>
          <input type="number" step="0.01" min="0" class="form-control" id="gesso" v-model="formData.gesso"
            placeholder="Informe a quantidade de gesso" required >
        </div>

        <div class="mb-3">
          <label for="kcl" class="form-label">KCl</label>
          <input type="number" step="0.01" min="0" class="form-control" id="kcl" v-model="formData.kcl"
            placeholder="Informe a quantidade de KCl" required >
        </div>

        <div class="mb-3">
          <label for="p2o5" class="form-label">P2O5</label>
          <input type="number" step="0.01" min="0" class="form-control" id="p2o5" v-model="formData.p2o5"
            placeholder="Informe a quantidade de P2O5" required >
        </div>

        <div class="mb-3">
          <label for="n" class="form-label">Nitrogênio (N)</label>
          <input type="number" step="0.01" min="0" class="form-control" id="n" v-model="formData.n"
            placeholder="Informe a quantidade de Nitrogênio (N)" required >
        </div>

        <div class="mb-3">
          <label for="s" class="form-label">Enxofre (S)</label>
          <input type="number" step="0.01" min="0" class="form-control" id="s" v-model="formData.s"
            placeholder="Informe a quantidade de Enxofre (S)" required >
        </div>

        <div class="button-group">
          <!-- Botão para voltar sem salvar alterações -->
          <button @click="toggleForm" class="btn-back">Voltar</button>
          <!-- Botão para enviar ou atualizar o formulário -->
          <button type="submit" class="btn-submit">{{ editingRec ? 'Atualizar' : 'Enviar' }}</button>
        </div>
      </form>
    </div>

    <!-- Lista de recomendações cadastradas -->
    <div v-else class="recomendacao-list-container">
      <!-- Botão para abrir o formulário de cadastro -->
      <div class="button-container">
        <button @click="toggleForm" class="btn-submit">Cadastrar Nova Recomendação</button>
      </div>

      <!-- Verifica se há recomendações para exibir -->
      <div v-if="recomendacoes.length">
        <div class="container-fluid">
          <!-- Cabeçalho da tabela de recomendações -->
          <div class="row font-weight-bold mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Análise de Solo <p>(laudo)</p></div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Camada de Correção</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Calcário Calcítico</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Calcario Dolomitico</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Calcario Magnesiano</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Gesso</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Cloreto de Potássio (kcl)</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Fosfato (P2O5)</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Nitrogênio (n)</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Enxofre (s)</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Ações</div>
          </div>
          <!-- Loop para exibir cada recomendação na tabela -->
          <div v-for="recomendacao in recomendacoes" :key="recomendacao.id" class="row recomendacao-info mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">
              {{ recomendacao.analise_data }} — {{ recomendacao.gleba_nome }}
              <p>{{ recomendacao.analise_laudo }}</p>
            </div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ recomendacao.camada_correcao }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ recomendacao.calcario_calcitico }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ recomendacao.calcario_dolomitico }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ recomendacao.calcario_magnesiano }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ recomendacao.gesso }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ recomendacao.kcl }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ recomendacao.p2o5 }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ recomendacao.n }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ recomendacao.s }}</div>
            <!-- Botões para editar e excluir recomendações -->
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">
              <button @click="editRec(recomendacao)" class="btn-edit">🖊️</button>
              <button @click="deleteRec(recomendacao.id)" class="btn-delete">🗑️</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <p>Nenhuma recomendação encontrada.</p>
      </div>
      <PaginacaoLista :pagina="pagina" :total-paginas="paginacao.totalPaginas"
        :total="paginacao.total" @mudar="irParaPagina" />

    </div>
  </div>
</template>

<script>
import api from '@/interceptadorAxios';
import { aviso, confirmar, erro, sucesso } from '@/notificacoes';
import PaginacaoLista from '@/components/PaginacaoLista.vue';
import listaPaginada from '@/mixins/listaPaginada';
import { mensagemDeErro } from '@/erros';
import { extrairLista, PARAMS_LISTA_COMPLETA, TAMANHO_LISTA_COMPLETA } from '@/lista';
export default {
  components: { PaginacaoLista },
  mixins: [listaPaginada],
  data() {
    return {
      showForm: false,
      formData: {
        analisesolo: null,
        camada_correcao: '',
        calcario_calcitico: '',
        calcario_dolomitico: '',
        calcario_magnesiano: '',
        gesso: '',
        kcl: '',
        p2o5: '',
        n: '',
        s: '',
      },
      analisesolo: [],
      analise_solo: [],
      propriedades: [],
      propriedadeSelecionada: '',
      recomendacoes: [], 
      editingRec: null,  
    };
  }
  ,
  watch: {
    propriedadeSelecionada(nova, antiga) {
      // Trocar de propriedade invalida a análise escolhida, que é de outra.
      if (antiga !== '' && nova !== antiga) this.formData.analise_solo = '';
      this.fetchAnaliseSolo();
    },
  },
  methods: {
    // Exigido pelo mixin listaPaginada: como recarregar após trocar de página.
    recarregar() {
      this.fetchRecomendação();
    },
    toggleForm() {
      this.showForm = !this.showForm; 
      this.clearForm(); 
    },




    async fetchPropriedades() {
      try {
        const response = await api.get('/propriedades/' + PARAMS_LISTA_COMPLETA);
        this.propriedades = extrairLista(response);
      } catch (error) {
        console.error('Erro ao buscar propriedades:', error);
      }
    },
    // Busca apenas as análises da propriedade escolhida, usando o filtro
    // '?propriedade=' da API. Sem isso a tela puxava o histórico inteiro.
    async fetchAnaliseSolo() {
      if (!this.propriedadeSelecionada) {
        this.analise_solo = [];
        return;
      }
      try {
        const response = await api.get(
          `/analisesolo/?propriedade=${this.propriedadeSelecionada}` +
          `&page_size=${TAMANHO_LISTA_COMPLETA}`
        );
        this.analise_solo = extrairLista(response);
      } catch (error) {
        console.error('Erro ao buscar análises de solo: ', error);
      }
    },

    async fetchRecomendação() {
      try {
        const response = await api.get(`/recomendacoes/?page=${this.pagina}`);
                this.recomendacoes = this.aplicarPaginacao(response)
      } catch (error) {
        console.error('erro ao buscae recomendações: ', error);
      }
    },
    async submitForm() {
      try {
        if (this.editingRec) {
          const response = await api.put(`/recomendacoes/${this.editingRec}/`, this.formData);
          if (response.status === 200) {
            sucesso('recomendação atualizada com sucesso!');
          } else {
            erro('erro ao atualizar a recomendação.')
          }
        } else {
          const response = await api.post('/recomendacoes/', this.formData);
          if (response.status === 201) {
            sucesso(' recomendação foi cadastrada com sucesso!');
          } else {
            aviso('recomendação nao pode ser cadastrada.');
          }
        }
        this.fetchRecomendação();
        this.showForm = false;
      } catch (error) {
        console.error('erro ao enviuar requisição:', error);
        erro('erro ao enviar requisauição. verifique o console')
      }
    },

    editRec(recomendacoes) {
      this.editingRec = recomendacoes.id
      this.formData = { ...recomendacoes }; 
      this.showForm = true;
    },
    clearForm() {
      this.formData = {
        analisesolo: null,
        camada_correcao: '',
        calcario_calcitico: '',
        calcario_dolomitico: '',
        calcario_magnesiano: '',
        gesso: '',
        kcl: '',
        p2o5: '',
        n: '',
        s: '',
      };
      this.editingRec = null;
    },
    async deleteRec(id) {
      if (await confirmar('tem certeza que deseja excluir esta recomendação?')) {
        try {
          const response = await api.delete(`/recomendacoes/${id}/`);
          if (response.status === 204) { 
            sucesso('Recomendação excluída com sucesso!');
            this.fetchRecomendação();
          } else {
            erro('Erro ao tentar excluir a recomendação.');
          }
        } catch (error) {
          console.error('Erro ao excluir a recomendação:', error);
          erro(mensagemDeErro(error));
        }
      }
    }
  },
  mounted() {
    this.fetchPropriedades();
    this.fetchRecomendação();
  }
};
</script>

<style scoped>
/* Estilos do container principal */
.container-fluid {
  width: 100%;
  padding: 0 15px;
}

/* Estilos dos botões */
.button-container {
  text-align: left;
  margin-bottom: 20px;
}

/* Estilo para o container do formulário e da lista de usuários */
.form-container,
.recomendacao-list-container {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  background-color: whitesmoke;
  border: 2px solid grey;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* Estilos para a exibição das informações dos usuários */
.recomendacao-info {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ddd;
  position: relative;
}

.recomendacao-info>div {
  position: relative;
  padding-right: 10px;
}

/* Linha vertical entre as colunas */
.recomendacao-info>div:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 1px;
  background-color: grey;
}

/* Estilos dos botões */
.btn-submit,
.btn-edit,
.btn-delete,
.btn-cancel,
.btn-back {
  padding: 8px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-right: 5px;
}

.btn-submit,
.btn-back,
.btn-edit {
  background-color: #237837;
  color: white;
}

.btn-submit:hover,
.btn-back:hover,
.btn-edit:hover {
  background-color: #218838;
}

.btn-delete {
  background-color: #dc3545;
  color: white;
}

.btn-delete:hover {
  background-color: #c82333;
}

/* Estilos do botão de cancelar */
.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

/* Estilos das labels do formulário */
.form-label {
  text-align: left;
  display: block;
  margin-bottom: 0.5rem;
}

/* Grupo de botões do formulário */
.button-group {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.button-group .btn-back {
  margin-right: 10px;
}
</style>
