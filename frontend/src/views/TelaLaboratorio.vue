<template>
  <div class="container-fluid">
    <!-- Título da Lista de laboratórios -->
    <h1 v-if="!showForm" class="titulo-tela">Lista de Laboratórios</h1>
    <!-- Formulário de cadastro/edição de laboratórios -->
    <div v-if="showForm" class="form-container">
      <h1 class="titulo-tela">{{ editingLab ? 'Editar Laboratório' : "Cadastrar Laboratório" }}</h1>
      <form @submit.prevent="submitForm" class="tela-form">
        <!-- Campo para o Endereço -->
        <div class="mb-3">
          <label for="endereco" class="form-label">Endereço</label>
          <input type="text" class="form-control" id="endereco" v-model="formData.endereco"
            placeholder="Digite seu endereço" required />
        </div>
        <!-- Campo para o Nome -->
        <div class="mb-3">
          <label for="nome" class="form-label">Nome</label>
          <input type="text" class="form-control" id="nome" v-model="formData.nome"
            placeholder="Digite o nome do laboratório" required />
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
          <button type="submit" class="btn-submit">{{ editingLab ? 'Salvar' : 'Cadastrar' }}</button>
        </div>
      </form>
    </div>
    <!-- Lista de laboratórios -->
    <div v-if="!showForm" class="lab-list mt-5">
      <div class="lista-container">
        <!-- Botão para abrir o formulário de cadastro -->
        <div class="button-container">
          <button @click="toggleForm" class="btn-submit">Cadastrar novo laboratorio</button>
        </div>
        <!-- Verifica se há laboratórios cadastrados -->
        <div v-if="laboratorios.length">
          <div class="row lista-cabecalho mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Usuário</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Endereço</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Nome</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Email</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Telefone</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Cidade</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Estado</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Ação</div>
          </div>
          <div v-for="laboratorio in laboratorios" :key="laboratorio.id" class="row lista-linha mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ getUsuarioNome(laboratorio.usuario) }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ laboratorio.endereco }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ laboratorio.nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ laboratorio.email }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ laboratorio.telefone }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ laboratorio.cidade }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ laboratorio.estado }}</div>
            <!-- Botões para editar e excluir laboratórios -->
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">
              <button @click="startEditing(laboratorio)" class="btn-edit">🖊️</button>
              <button @click="deleteLab(laboratorio.id)" class="btn-delete">🗑️</button>
            </div>
          </div>
        </div>
        <!-- Mensagem caso não existam laboratórios -->
        <div v-else>
          <p>Nenhum laboratório encontrado.</p>
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
import { getNomeUsuario } from '@/sessao';
import { mensagemDeErro } from '@/erros';
import { UFS } from '@/ufs';

export default {
  components: { PaginacaoLista },
  mixins: [listaPaginada],
  data() {
    return {
      UFS,
      formData: {
        endereco: '',
        nome: '',
        telefone: '',
        email: '',
        cidade: '',
        estado: '',
      },
      laboratorios: [],
      showForm: false,
      editingLab: false
    };
  },
  methods: {
    // Exigido pelo mixin listaPaginada: como recarregar após trocar de página.
    recarregar() {
      this.fetchlaboratorios();
    },
    // Alterna a exibição do formulário e reseta os dados
    toggleForm() {
      this.showForm = !this.showForm;
      this.editingLab = false;
      this.formData = {usuario:'', endereco: '', nome: '', telefone: '', email: '', cidade: '', estado: '' };
    },
      getUsuarioNome() {
      // Todo registro pertence ao usuário logado (o backend filtra por ele),
      // então o nome vem da sessão em vez de uma requisição a /usuarios/,
      // que devolvia uma lista de um item só.
      return getNomeUsuario();
    },
    // Busca todos os laboratórios
    async fetchlaboratorios() {
      try {
        const response = await api.get(`/laboratorios/?page=${this.pagina}`);
                this.laboratorios = this.aplicarPaginacao(response)
      } catch (error) {
        console.error('Erro ao buscar laboratórios:', error);
      }
    },
    // Submete o formulário para cadastro ou edição
    async submitForm() {
      try {
        if (this.editingLab) {
          // Atualiza o laboratório existente
          const response = await api.put(`/laboratorios/${this.formData.id}/`, this.formData);
          if (response.status === 200) {
            sucesso('Laboratório atualizado com sucesso!');
            this.fetchlaboratorios();
            this.toggleForm();
          } else {
            erro('Erro ao atualizar laboratório.');
          }
        } else {
          // Cadastra um novo laboratório
          const response = await api.post('/laboratorios/', this.formData);
          if (response.status === 201) {
            sucesso('Laboratório cadastrado com sucesso!');
            this.laboratorios.push(response.data);
            this.toggleForm();
          } else {
            erro('Erro ao cadastrar laboratório. Tente novamente mais tarde.');
          }
        }
      } catch (error) {
        console.error('Erro ao enviar requisição:', error);
        erro(mensagemDeErro(error));
      }
    },
    // Inicia o modo de edição
    startEditing(laboratorio) {
      this.showForm = true;
      this.editingLab = true;
      this.formData = { ...laboratorio };
    },
    // Deleta um laboratório
    async deleteLab(laboratorioId) {
      if (!await confirmar('Tem certeza que deseja deletar este laboratório?')) {
        return;
      }
      try {
        const response = await api.delete(`/laboratorios/${laboratorioId}/`);
        if (response.status === 204) {
          sucesso('Laboratório deletado com sucesso!');
          this.laboratorios = this.laboratorios.filter(p => p.id !== laboratorioId);
        } else {
          erro('Erro ao deletar laboratório.');
        }
      } catch (error) {
        console.error('Erro ao deletar laboratórios:', error);
        erro(mensagemDeErro(error));
      }
    }
  },
  mounted() {
    this.fetchlaboratorios();
  }
};
</script>
