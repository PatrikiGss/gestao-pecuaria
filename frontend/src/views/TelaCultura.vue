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
            placeholder="Digite o nome da propriedade" required />
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
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">Usuário</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">Nome</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">Ação</div>
          </div>
          <div v-for="cultura in culturas" :key="cultura.id" class="row user-info mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">{{ getUsuarioNome(cultura.usuario) }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-4">{{ cultura.nome }}</div>
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
      </div>
    </div>
  </div>
</template>


<script>
import api from '@/interceptadorAxios';

export default {
  data() {
    return {
      formData: {
        nome: '',
      },
      usuarios: [],
      culturas: [],
      showForm: false,
      editingcultura: false
    };
  },
  methods: {
    // Alterna a exibição do formulário e reseta os dados
    toggleForm() {
      this.showForm = !this.showForm;
      this.editingcultura = false;
      this.formData = { usuario: '', nome: '' };
    },
    // Obtém o nome do usuário a partir do ID
    getUsuarioNome(usuarioId) {
      const usuario = this.usuarios.find(u => u.id === usuarioId);
      return usuario ? usuario.nome : 'Desconhecido';
    },
    // Busca todos os usuários
    async fetchUsuarios() {
      try {
        const response = await api.get('/usuarios/');
        this.usuarios = response.data;
      } catch (error) {
        console.error('Erro ao buscar usuários:', error);
      }
    },
    // Busca todos as culturas
    async fetchculturas() {
      try {
        const response = await api.get('/culturas/');
        this.culturas = response.data;
      } catch (error) {
        console.error('Erro ao buscar culturas:', error);
      }
    },
    // Submete o formulário para cadastro ou edição
    async submitForm() {
      try {
    const token = localStorage.getItem('token')|| sessionStorage.getItem('token');
    const config = {
      headers: {
        Authorization: `Bearer ${token}`  // Envia o token no cabeçalho de autorização
      }
    };
        if (this.editingcultura) {
          // Atualiza o laboratório existente
          const response = await api.put(`/culturas/${this.formData.id}/`, this.formData, this.formData, config);
          if (response.status === 200) {
            alert('cultura atualizado com sucesso!');
            this.fetchculturas();
            this.toggleForm();
          } else {
            alert('Erro ao atualizar cultura.');
          }
        } else {
          // Cadastra um novo laboratório
          const response = await api.post('/culturas/', this.formData, this.formData, config);
          if (response.status === 201) {
            alert('cultura cadastrada com sucesso!');
            this.culturas.push(response.data);
            this.toggleForm();
          } else {
            alert('Erro ao cadastrar cultura. Tente novamente mais tarde.');
          }
        }
      } catch (error) {
        console.error('Erro ao enviar requisição:', error);
        alert('Erro ao enviar requisição. Verifique o console para mais detalhes.');
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
      if (!confirm('Tem certeza que deseja deletar esta cultura?')) {
        return;
      }
      try {
        const response = await api.delete(`/culturas/${culturaId}/`);
        if (response.status === 204) {
          alert('cultura deletada com sucesso!');
          this.culturas = this.culturas.filter(p => p.id !== culturaId);
        } else {
          alert('Erro ao deletar cultura.');
        }
      } catch (error) {
        console.error('Erro ao deletar culturas:', error);
        alert('Erro ao deletar culturas. Verifique o console para mais detalhes.');
      }
    }
  },
  mounted() {
    this.fetchUsuarios();
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
