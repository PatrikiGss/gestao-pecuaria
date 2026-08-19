<template>
  <div class="container-fluid">
    <h1></h1>
    <h1 v-if="!showForm" class="mt-4"><br>Lista de culturas</h1>
    <!-- Formulário de cadastro/edição de culturas -->
    <div v-if="showForm" class="form-container">
      <h1>{{ editingcultura ? 'Editar Cultura' : 'Cadastrar Cultura' }}</h1>
      <form @submit.prevent="submitForm" class="cultura-form">
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

        <!-- Botões de ação para enviar e cancelar -->
        <div class="button-group">
          <button type="button" @click="toggleForm" class="btn-cancel">Voltar</button>
          <button type="submit" class="btn-submit">{{ editingcultura ? 'Atualizar Cultura' : 'Cadastrar Cultura'
            }}</button>
        </div>
      </form>
    </div>

    <!-- Lista de culturas -->
    <div v-if="!showForm" class="cultura-list mt-5">
      <div class="container-fluidd">
        <!-- Botão para abrir o formulário de cultura -->
        <br />
        <div class="button-container">
          <button @click="toggleForm" class="btn-submit">Cadastrar nova Cultura</button>
        </div>
        <!-- Verifica se há culturas cadastradas -->
        <div v-if="culturas.length">
          <div class="row font-weight-bold mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">Nome</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">V₂ desejado</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">Ação</div>
          </div>
          <div v-for="cultura in culturas" :key="cultura.id" class="row user-info mb-2">
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
      },
      culturas: [],
      showForm: false,
      editingcultura: false
    };
  },
  methods: {
    // Exigido pelo mixin listaPaginada: como recarregar após trocar de página.
    recarregar() {
      this.fetchculturas();
    },
    // Alterna a exibição do formulário e reseta os dados
    toggleForm() {
      this.showForm = !this.showForm;
      this.editingcultura = false;
      this.formData = { nome: '', saturacao_bases_desejada: '' };
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
          const response = await api.put(`/culturas/${this.formData.id}/`, this.formData);
          if (response.status === 200) {
            sucesso('cultura atualizado com sucesso!');
            this.fetchculturas();
            this.toggleForm();
          } else {
            erro('Erro ao atualizar cultura.');
          }
        } else {
          // Cadastra uma nova cultura
          const response = await api.post('/culturas/', this.formData);
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

<style scoped>
/* Container geral com fundo e borda */
.container-fluidd {
  width: 100%;
  padding: 0 15px;
  background-color: whitesmoke;
  border: 2px solid grey;
  border-radius: 10px;
}

/* Container do formulário com sombra e borda */
.form-container {
  width: 100%;
  padding: 20px;
  background-color: whitesmoke;
  border: 2px solid grey;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* Estilo do formulário de laboratório */
.cultura-form {
  display: flex;
  flex-direction: column;
}

/* Estilo das linhas do formulário */
.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

/* Grupo de campos do formulário, ajusta o tamanho das colunas */
.form-group {
  flex: 1 1 150px;
  min-width: 150px;
}

/* Grupo de botões, alinha os botões ao final */
.button-group {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Container de botões, alinha o texto à esquerda */
.button-container {
  text-align: left;
  margin-bottom: 20px;
}

/* Estilo das linhas da lista de usuários */
.user-info {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ddd;
  position: relative;
}

/* Linha dos usuários, separadores entre colunas */
.user-info>div {
  position: relative;
  padding-right: 10px;
}

.user-info>div:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 1px;
  background-color: grey;
}

/* Botões estilizados para ações de formulário e lista */
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

/* Estilo dos botões de submit, back e edit */
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

/* Estilo do botão de delete */
.btn-delete {
  background-color: #dc3545;
  color: white;
}

.btn-delete:hover {
  background-color: #c82333;
}

/* Estilo do botão de cancel */
.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

/* Estilo das labels dos campos do formulário */
.form-label {
  text-align: left;
  display: block;
  margin-bottom: 0.5rem;
}
</style>
