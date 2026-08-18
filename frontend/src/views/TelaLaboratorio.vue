<template>
  <div class="container-fluid">
    <h1></h1>
    <!-- Título da Lista de laboratórios -->
    <h1 v-if="!showForm" class="mt-4"> <br> Lista de Laboratórios</h1>
    <!-- Formulário de cadastro/edição de laboratórios -->
    <div v-if="showForm" class="form-container">
      <h1>{{ editingLab ? 'Editar Laboratório' : "Cadastrar Laboratório" }}</h1>
      <form @submit.prevent="submitForm" class="lab-form">
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
            placeholder="Ex: (49)123112233" required />
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
          <input type="text" class="form-control" id="estado" v-model="formData.estado" placeholder="EX: SC, SP, RS, PR"
            required />
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
      <div class="container-fluidd">
        <!-- Botão para abrir o formulário de cadastro -->
        <br>
        <div class="button-container">
          <button @click="toggleForm" class="btn-submit">Cadastrar novo laboratorio</button>
        </div>
        <!-- Verifica se há laboratórios cadastrados -->
        <div v-if="laboratorios.length">
          <div class="row font-weight-bold mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Usuário</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Endereço</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Nome</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Email</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Telefone</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Cidade</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Estado</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Ação</div>
          </div>
          <div v-for="laboratorio in laboratorios" :key="laboratorio.id" class="row user-info mb-2">
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
        endereco: '',
        nome: '',
        telefone: '',
        email: '',
        cidade: '',
        estado: '',
      },
      usuarios: [],
      laboratorios: [],
      showForm: false,
      editingLab: false
    };
  },
  methods: {
    // Alterna a exibição do formulário e reseta os dados
    toggleForm() {
      this.showForm = !this.showForm;
      this.editingLab = false;
      this.formData = {usuario:'', endereco: '', nome: '', telefone: '', email: '', cidade: '', estado: '' };
    },
      getUsuarioNome(usuarioId) {
      const usuario = this.usuarios.find(u => u.id === usuarioId);
      return usuario ? usuario.nome : 'Desconhecido';
    },
    async fetchUsuarios() {
    try {
      const response = await api.get('/usuarios/'); // Atualize a URL conforme sua API
      this.usuarios = response.data;
    } catch (error) {
      console.error('Erro ao buscar usuários:', error);
    }
  },
    // Busca todos os laboratórios
    async fetchlaboratorios() {
      try {
        const response = await api.get('/laboratorios/');
        this.laboratorios = response.data;
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
            alert('Laboratório atualizado com sucesso!');
            this.fetchlaboratorios();
            this.toggleForm();
          } else {
            alert('Erro ao atualizar laboratório.');
          }
        } else {
          // Cadastra um novo laboratório
          const response = await api.post('/laboratorios/', this.formData);
          if (response.status === 201) {
            alert('Laboratório cadastrado com sucesso!');
            this.laboratorios.push(response.data);
            this.toggleForm();
          } else {
            alert('Erro ao cadastrar laboratório. Tente novamente mais tarde.');
          }
        }
      } catch (error) {
        console.error('Erro ao enviar requisição:', error);
        alert('Erro ao enviar requisição. Verifique o console para mais detalhes.');
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
      if (!confirm('Tem certeza que deseja deletar este laboratório?')) {
        return;
      }
      try {
        const response = await api.delete(`/laboratorios/${laboratorioId}/`);
        if (response.status === 204) {
          alert('Laboratório deletado com sucesso!');
          this.laboratorios = this.laboratorios.filter(p => p.id !== laboratorioId);
        } else {
          alert('Erro ao deletar laboratório.');
        }
      } catch (error) {
        console.error('Erro ao deletar laboratórios:', error);
        alert('Erro ao deletar laboratórios. Verifique o console para mais detalhes.');
      }
    }
  },
  mounted() {
    this.fetchUsuarios();
    this.fetchlaboratorios();
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
.lab-form {
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
