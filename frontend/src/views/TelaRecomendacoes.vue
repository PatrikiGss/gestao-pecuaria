<template>
  <div class="container-fluid">
    <h1 v-if="!showForm" class="titulo-tela">Lista de Recomendações</h1>
    <div v-if="showForm" class="form-container">
      <h1 class="titulo-tela">{{ editingRec ? 'Editar Recomendação' : 'Cadastro de Recomendação' }}</h1>
      <form @submit.prevent="submitForm" class="tela-form">
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

        <!-- Não há campo digitável aqui. Todas as doses são calculadas
             pelo backend (apps/core/agronomia.py) a partir do laudo e dos
             parâmetros cadastrados na cultura. Um campo editável que o
             servidor sobrescreve só enganaria quem preenche. -->
        <div v-if="previa && previa.aplicavel" class="previa">
          <h3>Recomendação calculada</h3>

          <div class="indices">
            <div class="indice destaque">
              <span class="rotulo">Calcário {{ rotuloCalcario(previa.tipo_calcario) }}</span>
              <span class="valor">{{ doseCalcario }} t/ha</span>
            </div>
            <div class="indice">
              <span class="rotulo">Gesso</span>
              <span class="valor">{{ previa.gesso }} kg/ha</span>
            </div>
            <div class="indice">
              <span class="rotulo">KCl</span>
              <span class="valor">{{ previa.kcl }} kg/ha</span>
            </div>
            <div class="indice">
              <span class="rotulo">P₂O₅</span>
              <span class="valor">{{ previa.p2o5 }} kg/ha</span>
            </div>
            <div class="indice">
              <span class="rotulo">Nitrogênio</span>
              <span class="valor">{{ previa.n === null ? '—' : previa.n }} kg/ha</span>
            </div>
            <div class="indice">
              <span class="rotulo">Enxofre</span>
              <span class="valor">{{ previa.s }} kg/ha</span>
            </div>
          </div>

          <p class="nota">
            Método da calagem: {{ previa.metodo_calagem }}<span v-if="previa.v2_utilizado">,
            com V₂ = {{ previa.v2_utilizado }}%</span><span v-if="previa.prnt_utilizado">
            e PRNT = {{ previa.prnt_utilizado }}%</span>. Camada de 0 a 20 cm.
          </p>

          <!-- O que falta cadastrar para o cálculo ficar completo. Campo sem
               parâmetro sai zerado, e aqui se explica por quê. -->
          <div v-if="previa.pendencias && previa.pendencias.length" class="pendencias-bloco">
            <strong>Falta cadastrar para completar o cálculo:</strong>
            <ul>
              <li v-for="(p, i) in previa.pendencias" :key="i">{{ p }}</li>
            </ul>
          </div>
        </div>

        <div v-else-if="previa && !previa.aplicavel" class="alert-danger">
          {{ previa.motivo }}
        </div>

        <p v-else-if="formData.analise_solo" class="text-muted">Calculando…</p>

        <div class="button-group">
          <!-- Botão para voltar sem salvar alterações -->
          <button @click="toggleForm" class="btn-back">Voltar</button>
          <!-- Botão para enviar ou atualizar o formulário -->
          <button type="submit" class="btn-submit">{{ editingRec ? 'Atualizar' : 'Enviar' }}</button>
        </div>
      </form>
    </div>

    <!-- Lista de recomendações cadastradas -->
    <div v-else class="lista-container">
      <!-- Botão para abrir o formulário de cadastro -->
      <div class="button-container">
        <button @click="toggleForm" class="btn-submit">Cadastrar Nova Recomendação</button>
      </div>

      <!-- Verifica se há recomendações para exibir -->
      <div v-if="recomendacoes.length">
        <div class="container-fluid">
          <!-- Cabeçalho da tabela de recomendações -->
          <div class="row lista-cabecalho mb-2">
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
          <div v-for="recomendacao in recomendacoes" :key="recomendacao.id" class="row lista-linha mb-2">
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
      // Só a análise é escolhida; as doses vêm calculadas do servidor.
      formData: {
        analise_solo: '',
      },
      previa: null,
      analisesolo: [],
      analise_solo: [],
      propriedades: [],
      propriedadeSelecionada: '',
      recomendacoes: [], 
      editingRec: null,  
    };
  }
  ,
  computed: {
    // A calagem sai num único campo, o do tipo indicado pela relação Ca:Mg.
    doseCalcario() {
      if (!this.previa) return 0;
      return this.previa.calcario_calcitico
        || this.previa.calcario_dolomitico
        || this.previa.calcario_magnesiano
        || 0;
    },
  },
  watch: {
    'formData.analise_solo'(id) {
      this.buscarPrevia(id);
    },
    propriedadeSelecionada(nova, antiga) {
      // Trocar de propriedade invalida a análise escolhida, que é de outra.
      if (antiga !== '' && nova !== antiga) this.formData.analise_solo = '';
      this.fetchAnaliseSolo();
    },
  },
  methods: {
    rotuloCalcario(tipo) {
      return { calcitico: 'Calcítico', magnesiano: 'Magnesiano',
               dolomitico: 'Dolomítico' }[tipo] || '';
    },
    // Mostra o que será gravado antes de salvar.
    async buscarPrevia(id) {
      this.previa = null;
      if (!id) return;
      try {
        const { data } = await api.get(`/analisesolo/${id}/`);
        this.previa = data.recomendacao_previa;
      } catch (error) {
        console.error('Erro ao calcular a prévia:', error);
        erro(mensagemDeErro(error, 'Não foi possível calcular a recomendação.'));
      }
    },
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
