<template>
  <div class="container-fluid">
    <h1 v-if="!showForm" class="titulo-tela">Lista de Calcários</h1>

    <div v-if="showForm" class="form-container">
      <h1 class="titulo-tela">{{ editando ? 'Editar Calcário' : 'Cadastrar Calcário' }}</h1>
      <form @submit.prevent="submitForm" class="tela-form">
        <div class="mb-3">
          <label for="nome" class="form-label">Nome</label>
          <input type="text" class="form-control" id="nome" v-model="formData.nome"
            placeholder="Ex: Calcário dolomítico — Fornecedor X" required maxlength="255" />
        </div>

        <div class="mb-3">
          <label for="tipo" class="form-label">Tipo</label>
          <select id="tipo" class="form-control" v-model="formData.tipo" required>
            <option disabled value="">Selecione o tipo</option>
            <option v-for="t in TIPOS" :key="t.valor" :value="t.valor">{{ t.rotulo }}</option>
          </select>
        </div>

        <!-- PRNT é o que converte a necessidade teórica de calagem em dose
             real de produto. Sem ele a fórmula fica pela metade. -->
        <div class="mb-3">
          <label for="prnt" class="form-label">PRNT (%)</label>
          <input type="number" step="0.01" min="1" max="150" class="form-control"
            id="prnt" v-model="formData.prnt" placeholder="Ex: 85.5" required />
          <small class="text-muted">
            Poder Relativo de Neutralização Total, conforme a embalagem.
            É o que converte a necessidade de calagem em quantidade de produto.
          </small>
        </div>

        <div class="mb-3">
          <label for="teor_cao" class="form-label">Teor de CaO (%)</label>
          <input type="number" step="0.01" min="0" max="100" class="form-control"
            id="teor_cao" v-model="formData.teor_cao" placeholder="Ex: 30" />
        </div>

        <div class="mb-3">
          <label for="teor_mgo" class="form-label">Teor de MgO (%)</label>
          <input type="number" step="0.01" min="0" max="100" class="form-control"
            id="teor_mgo" v-model="formData.teor_mgo" placeholder="Ex: 18" />
          <small class="text-muted">
            Opcional. Se informado, o sistema confere se o tipo escolhido bate
            com o teor — a classificação brasileira separa os três tipos
            justamente por essa faixa.
          </small>
        </div>

        <div class="button-group">
          <button type="button" @click="toggleForm" class="btn-back">Voltar</button>
          <button type="submit" class="btn-submit">{{ editando ? 'Atualizar' : 'Cadastrar' }}</button>
        </div>
      </form>
    </div>

    <div v-else class="lista-container">
      <div class="button-container">
        <button @click="toggleForm" class="btn-submit">Cadastrar Novo Calcário</button>
      </div>
      <div v-if="calcarios.length">
        <div class="container-fluid">
          <div class="row lista-cabecalho mb-2">
            <div class="col-12 col-sm-6 col-md-3">Nome</div>
            <div class="col-12 col-sm-6 col-md-3">Tipo</div>
            <div class="col-12 col-sm-6 col-md-2">PRNT</div>
            <div class="col-12 col-sm-6 col-md-2">CaO / MgO</div>
            <div class="col-12 col-sm-6 col-md-2">Ações</div>
          </div>
          <div v-for="calcario in calcarios" :key="calcario.id" class="row lista-linha mb-2">
            <div class="col-12 col-sm-6 col-md-3">{{ calcario.nome }}</div>
            <div class="col-12 col-sm-6 col-md-3">{{ calcario.tipo_descricao }}</div>
            <div class="col-12 col-sm-6 col-md-2">{{ calcario.prnt }}%</div>
            <div class="col-12 col-sm-6 col-md-2">
              <span v-if="calcario.teor_cao || calcario.teor_mgo">
                {{ calcario.teor_cao || '—' }} / {{ calcario.teor_mgo || '—' }}
              </span>
              <span v-else class="text-muted">não informado</span>
            </div>
            <div class="col-12 col-sm-6 col-md-2">
              <button @click="editar(calcario)" class="btn-edit">🖊️</button>
              <button @click="excluir(calcario.id)" class="btn-delete">🗑️</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <p>Nenhum calcário cadastrado.</p>
      </div>
      <PaginacaoLista :pagina="pagina" :total-paginas="paginacao.totalPaginas"
        :total="paginacao.total" @mudar="irParaPagina" />
    </div>
  </div>
</template>

<script>
import api from '@/interceptadorAxios';
import { confirmar, erro, sucesso } from '@/notificacoes';
import { mensagemDeErro } from '@/erros';
import PaginacaoLista from '@/components/PaginacaoLista.vue';
import listaPaginada from '@/mixins/listaPaginada';

// Espelha as escolhas do model (apps/core/models.py). As faixas de MgO são a
// classificação usada no Brasil, e o backend recusa a combinação incoerente.
const TIPOS = [
  { valor: 'calcitico', rotulo: 'Calcítico (MgO abaixo de 5%)' },
  { valor: 'magnesiano', rotulo: 'Magnesiano (MgO entre 5% e 12%)' },
  { valor: 'dolomitico', rotulo: 'Dolomítico (MgO acima de 12%)' },
];

export default {
  name: 'TelaCalcario',
  components: { PaginacaoLista },
  mixins: [listaPaginada],
  data() {
    return {
      TIPOS,
      showForm: false,
      formData: this.formularioVazio(),
      calcarios: [],
      editando: null,
    };
  },
  methods: {
    formularioVazio() {
      return { nome: '', tipo: '', prnt: '', teor_cao: '', teor_mgo: '' };
    },
    // Exigido pelo mixin listaPaginada: como recarregar após trocar de página.
    recarregar() {
      this.fetchCalcarios();
    },
    toggleForm() {
      this.showForm = !this.showForm;
      this.formData = this.formularioVazio();
      this.editando = null;
    },
    async fetchCalcarios() {
      try {
        const response = await api.get(`/calcarios/?page=${this.pagina}`);
        this.calcarios = this.aplicarPaginacao(response);
      } catch (error) {
        console.error('Erro ao buscar calcários:', error);
        erro(mensagemDeErro(error, 'Não foi possível carregar os calcários.'));
      }
    },
    // Campos opcionais vazios não podem ir como string: a API espera número
    // ou ausência do campo.
    montarPayload() {
      const payload = { ...this.formData };
      ['teor_cao', 'teor_mgo'].forEach((campo) => {
        if (payload[campo] === '' || payload[campo] === null) delete payload[campo];
      });
      return payload;
    },
    async submitForm() {
      try {
        if (this.editando) {
          await api.put(`/calcarios/${this.editando}/`, this.montarPayload());
          sucesso('Calcário atualizado com sucesso!');
        } else {
          await api.post('/calcarios/', this.montarPayload());
          sucesso('Calcário cadastrado com sucesso!');
        }
        this.fetchCalcarios();
        this.showForm = false;
        this.formData = this.formularioVazio();
        this.editando = null;
      } catch (error) {
        console.error('Erro ao salvar calcário:', error);
        erro(mensagemDeErro(error));
      }
    },
    editar(calcario) {
      this.editando = calcario.id;
      this.formData = {
        nome: calcario.nome,
        tipo: calcario.tipo,
        prnt: calcario.prnt,
        teor_cao: calcario.teor_cao || '',
        teor_mgo: calcario.teor_mgo || '',
      };
      this.showForm = true;
    },
    async excluir(id) {
      if (!await confirmar('Tem certeza que deseja excluir este calcário?')) return;
      try {
        await api.delete(`/calcarios/${id}/`);
        sucesso('Calcário excluído com sucesso!');
        this.fetchCalcarios();
      } catch (error) {
        console.error('Erro ao excluir calcário:', error);
        erro(mensagemDeErro(error));
      }
    },
  },
  mounted() {
    this.fetchCalcarios();
  },
};
</script>
