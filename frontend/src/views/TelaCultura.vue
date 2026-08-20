<template>
  <div class="container-fluid">
    <h1 v-if="!showForm" class="titulo-tela">Lista de Culturas</h1>
    <!-- Formulário de cadastro/edição de culturas -->
    <div v-if="showForm" class="form-container">
      <h1 class="titulo-tela">{{ editingcultura ? 'Editar Cultura' : 'Cadastrar Cultura' }}</h1>
      <form @submit.prevent="submitForm" class="tela-form">
        <!-- Campo para o Nome -->
        <div class="mb-3">
          <label for="nome" class="form-label">Nome</label>
          <input type="text" class="form-control" id="nome" v-model="formData.nome"
            placeholder="Ex: Soja, Milho, Café" required />
        </div>

        <!-- V₂: alvo de saturação por bases desta cultura. Entra na fórmula
             da calagem: NC = T × (V₂ − V₁) / 100 × (100 / PRNT). -->
        <div class="mb-3">
          <label for="saturacao_bases_desejada" class="form-label">
            Saturação por bases desejada (V₂)
          </label>
          <input type="number" step="0.01" min="0" max="100" class="form-control"
            id="saturacao_bases_desejada" v-model="formData.saturacao_bases_desejada"
            placeholder="Ex: 60" />
          <small class="text-muted">
            Em %. Opcional — sem este valor a cultura é cadastrada normalmente,
            mas a calagem não é calculada para ela. Consulte a fonte de
            referência que você adota (Boletim 100 do IAC, 5ª Aproximação de MG,
            Embrapa Cerrados).
          </small>
        </div>

        <!-- Parâmetros de adubação. São eles que permitem a Recomendação ser
             inteiramente calculada. Cada um vem da fonte de referência que
             você adotar — o sistema aplica, não arbitra. -->
        <div class="mb-3">
          <label for="saturacao_k_desejada" class="form-label">
            Saturação de K na CTC desejada
          </label>
          <input type="number" step="0.01" min="0" max="100" class="form-control"
            id="saturacao_k_desejada" v-model="formData.saturacao_k_desejada"
            placeholder="Ex: 4" />
          <small class="text-muted">
            Em %. Define a dose de potássio: o sistema calcula quanto falta
            para o K ocupar essa fração da CTC.
          </small>
        </div>

        <div class="mb-3">
          <label for="fosforo_desejado" class="form-label">Fósforo desejado</label>
          <input type="number" step="0.01" min="0" class="form-control"
            id="fosforo_desejado" v-model="formData.fosforo_desejado" placeholder="Ex: 20" />
          <small class="text-muted">Em mg/dm³. Teor de P que se quer atingir no solo.</small>
        </div>

        <div class="mb-3">
          <label for="fator_fixacao_fosforo" class="form-label">
            Fator de fixação de fósforo
          </label>
          <input type="number" step="0.01" min="0" class="form-control"
            id="fator_fixacao_fosforo" v-model="formData.fator_fixacao_fosforo"
            placeholder="Ex: 5" />
          <small class="text-muted">
            Quantos kg de P₂O₅ são necessários para elevar 1 mg/dm³ de P.
            Varia com a textura, porque solo argiloso fixa mais fósforo.
          </small>
        </div>

        <div class="mb-3">
          <label for="nitrogenio_recomendado" class="form-label">
            Nitrogênio recomendado
          </label>
          <input type="number" step="0.01" min="0" class="form-control"
            id="nitrogenio_recomendado" v-model="formData.nitrogenio_recomendado"
            placeholder="Ex: 30" />
          <small class="text-muted">
            Em kg/ha. O nitrogênio <strong>não é calculável a partir da análise
            de solo</strong> — depende da cultura e da produtividade esperada.
            Por isso entra aqui como dose da sua fonte.
          </small>
        </div>

        <div class="mb-3">
          <label for="enxofre_desejado" class="form-label">Enxofre desejado</label>
          <input type="number" step="0.01" min="0" class="form-control"
            id="enxofre_desejado" v-model="formData.enxofre_desejado" placeholder="Ex: 12" />
          <small class="text-muted">Em mg/dm³. Teor de S que se quer atingir no solo.</small>
        </div>

        <!-- Botões de ação para enviar e cancelar -->
        <div class="button-group">
          <button type="button" @click="toggleForm" class="btn-back">Voltar</button>
          <button type="submit" class="btn-submit">{{ editingcultura ? 'Atualizar Cultura' : 'Cadastrar Cultura'
            }}</button>
        </div>
      </form>
    </div>

    <!-- Lista de Culturas -->
    <div v-if="!showForm" class="lista-container mt-5">
      <div>
        <!-- Botão para abrir o formulário de cultura -->
        <div class="button-container">
          <button @click="toggleForm" class="btn-submit">Cadastrar nova Cultura</button>
        </div>
        <!-- Verifica se há culturas cadastradas -->
        <div v-if="culturas.length">
          <div class="row lista-cabecalho mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">Nome</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">V₂ desejado</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">Ação</div>
          </div>
          <div v-for="cultura in culturas" :key="cultura.id" class="row lista-linha mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">{{ cultura.nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">
              <span v-if="cultura.saturacao_bases_desejada">{{ cultura.saturacao_bases_desejada }}%</span>
              <span v-else class="text-muted">não definido</span>
            </div>
            <!-- Botões para editar e excluir culturas -->
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">
              <button @click="startEditing(cultura)" class="btn-edit">🖊️</button>
              <button @click="deleteCulturas(cultura.id)" class="btn-delete">🗑️</button>
            </div>
          </div>
        </div>
        <!-- Mensagem caso não existam culturas -->
        <div v-else>
          <p>Nenhuma cultura encontrada.</p>
        </div>
      <PaginacaoLista :pagina="pagina" :total-paginas="paginacao.totalPaginas"
        :total="paginacao.total" @mudar="irParaPagina" />

      </div>
    </div>
  </div>
</template>


<script>
import api from '@/interceptadorAxios';

// Parâmetros de adubação, opcionais, que alimentam o cálculo da recomendação.
const PARAMETROS = ['saturacao_k_desejada', 'fosforo_desejado', 'fator_fixacao_fosforo', 'nitrogenio_recomendado', 'enxofre_desejado'];
import { confirmar, erro, sucesso } from '@/notificacoes';
import PaginacaoLista from '@/components/PaginacaoLista.vue';
import listaPaginada from '@/mixins/listaPaginada';
import { mensagemDeErro } from '@/erros';

export default {
  components: { PaginacaoLista },
  mixins: [listaPaginada],
  data() {
    return {
      formData: {
        nome: '',
        saturacao_bases_desejada: '',
        saturacao_k_desejada: '',
        fosforo_desejado: '',
        fator_fixacao_fosforo: '',
        nitrogenio_recomendado: '',
        enxofre_desejado: '',
      },
      culturas: [],
      showForm: false,
      editingcultura: false
    };
  },
  methods: {
    // A API espera número ou ausência do campo; string vazia seria recusada.
    montarPayload() {
      const payload = { ...this.formData };
      ['saturacao_bases_desejada', ...PARAMETROS].forEach((campo) => {
        if (payload[campo] === '' || payload[campo] === null) delete payload[campo];
      });
      return payload;
    },
    // Exigido pelo mixin listaPaginada: como recarregar após trocar de página.
    recarregar() {
      this.fetchculturas();
    },
    // Alterna a exibição do formulário e reseta os dados
    toggleForm() {
      this.showForm = !this.showForm;
      this.editingcultura = false;
      this.formData = { nome: '', saturacao_bases_desejada: '', saturacao_k_desejada: '', fosforo_desejado: '', fator_fixacao_fosforo: '', nitrogenio_recomendado: '', enxofre_desejado: '', };
    },
    // Obtém o nome do usuário a partir do ID
    // Busca todos as culturas
    async fetchculturas() {
      try {
        const response = await api.get(`/culturas/?page=${this.pagina}`);
                this.culturas = this.aplicarPaginacao(response)
      } catch (error) {
        console.error('Erro ao buscar culturas:', error);
      }
    },
    // Submete o formulário para cadastro ou edição
    async submitForm() {
      try {
    // Removido o bloco 'config' com localStorage.getItem('token') (chave
    // inexistente) e o argumento duplicado: em 'api.put(url, dados, config)'
    // o terceiro parametro do axios e a configuracao, entao passar
    // 'this.formData' ali fazia o axios interpretar o corpo como config e
    // descartar silenciosamente o 4o argumento.
        if (this.editingcultura) {
          // Atualiza a cultura existente
          const response = await api.put(`/culturas/${this.formData.id}/`, this.montarPayload());
          if (response.status === 200) {
            sucesso('cultura atualizado com sucesso!');
            this.fetchculturas();
            this.toggleForm();
          } else {
            erro('Erro ao atualizar cultura.');
          }
        } else {
          // Cadastra uma nova cultura
          const response = await api.post('/culturas/', this.montarPayload());
          if (response.status === 201) {
            sucesso('cultura cadastrada com sucesso!');
            this.culturas.push(response.data);
            this.toggleForm();
          } else {
            erro('Erro ao cadastrar cultura. Tente novamente mais tarde.');
          }
        }
      } catch (error) {
        console.error('Erro ao enviar requisição:', error);
        erro(mensagemDeErro(error));
      }
    },
    // Inicia o modo de edição
    startEditing(cultura) {
      this.showForm = true;
      this.editingcultura = true;
      this.formData = { ...cultura };
    },
    // Deleta um laboratório
    async deleteCulturas(culturaId) {
      if (!await confirmar('Tem certeza que deseja deletar esta cultura?')) {
        return;
      }
      try {
        const response = await api.delete(`/culturas/${culturaId}/`);
        if (response.status === 204) {
          sucesso('cultura deletada com sucesso!');
          this.culturas = this.culturas.filter(p => p.id !== culturaId);
        } else {
          erro('Erro ao deletar cultura.');
        }
      } catch (error) {
        console.error('Erro ao deletar culturas:', error);
        erro(mensagemDeErro(error));
      }
    }
  },
  mounted() {
    this.fetchculturas();
  }
};
</script>
