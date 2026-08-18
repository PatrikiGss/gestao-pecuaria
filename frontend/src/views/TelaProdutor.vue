<template>
  <div class="container-fluid">
    <h1></h1>
    <!-- Título da Lista de Produtores -->
    <h1 v-if="!showForm" class="mt-4"> <br> Lista de Produtores</h1>
    <!-- Formulário de cadastro/edição de produtores -->
    <div v-if="showForm" class="form-container">
      <h1>{{ editingProdutor ? 'Editar Produtor' : 'Cadastro de Produtores' }}</h1>
      <form @submit.prevent="submitForm" class="producer-form">
        <!-- Campo para o usuário -->
        <!-- <div class="mb-3">
          <label for="usuario" class="form-label">Usuário</label>
          <select id="usuario" v-model="formData.usuario" class="form-control" required>
            <option disabled value="">Selecione um usuário</option>
            <option v-for="usuario in usuarios" :key="usuario.id" :value="usuario.id">
              {{ usuario.nome }}
            </option>
          </select>
        </div> -->
        <!-- Campo para o CPF -->
        <div class="mb-3">
          <label for="cpf" class="form-label">CPF</label>
          <input type="text" class="form-control" id="cpf" v-model="formData.cpf" placeholder="Digite apenas os números"
            required />
        </div>
        <!-- Campo para o nome -->
        <div class="mb-3">
          <label for="nome" class="form-label">Nome</label>
          <input type="text" class="form-control" id="nome" v-model="formData.nome"
            placeholder="Digite seu nome completo" required />
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
        <!-- Botões de ação -->
        <div class="button-group">
          <button @click="toggleForm" class="btn-back">Voltar</button>
          <button type="submit" class="btn-submit">{{ editingProdutor ? 'Salvar' : 'Cadastrar' }}</button>
        </div>
      </form>
    </div>

    <!-- Lista de produtores -->
    <div v-if="!showForm" class="producer-list mt-5">
      <!-- Botão para abrir o formulário de cadastro -->
      <div v-if="!showForm" class="button-container">
        <button @click="toggleForm" class="btn-submit">Cadastrar Novo Produtor</button>
      </div>
      <div v-if="produtores.length">
        <div class="container-fluid">
          <div class="row font-weight-bold mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Usuário</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">CPF</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Nome</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Telefone</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Email</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Ações</div>
          </div>
          <div v-for="produtor in produtores" :key="produtor.id" class="row user-info mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ getUsuarioNome(produtor.usuario) }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ produtor.cpf }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ produtor.nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ produtor.telefone }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ produtor.email }}</div>
            <!-- Botões para editar e excluir produtores -->
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">
              <button @click="startEditing(produtor)" class="btn-edit">🖊️</button>
              <button @click="deleteProdutor(produtor.id)" class="btn-delete">🗑️</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <p>Nenhum produtor encontrado.</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/interceptadorAxios';

export default {
  data() {
    return {
      showForm: false,
      formData: {
        // usuario: '',
        cpf: '',
        nome: '',
        telefone: '',
        email: ''
      },
      usuarios: [],
      produtores: [],
      editingProdutor: false,
    };
  },
  methods: {
    toggleForm() {
      this.showForm = !this.showForm;
      this.editingProdutor = false;
      this.formData = { usuario: '', cpf: '', nome: '', telefone: '', email: '' };
    },
    getUsuarioNome(usuarioId) {
      const usuario = this.usuarios.find(u => u.id === usuarioId);
      return usuario ? usuario.nome : 'Desconhecido';
    },
    async fetchProdutores() {
      try {
        const response = await api.get('/produtores/');
        this.produtores = response.data;
      } catch (error) {
        console.error('Erro ao buscar produtores:', error);
      }
    },
    async fetchUsuarios() {
      try {
        const response = await api.get('/usuarios/');
        this.usuarios = response.data;
      } catch (error) {
        console.error('Erro ao buscar usuários:', error);
      }
    },
    async submitForm() {
  try {
    const token = localStorage.getItem('token')|| sessionStorage.getItem('token');
    const config = {
      headers: {
        Authorization: `Bearer ${token}`  // Envia o token no cabeçalho de autorização
      }
    };
    if (this.editingProdutor) {
      const response = await api.put(`/produtores/${this.formData.id}/`, this.formData, config);
      if (response.status === 200) {
        alert('Produtor atualizado com sucesso!');
        this.fetchProdutores();
        this.toggleForm();
      } else {
        alert('Erro ao atualizar produtor.');
      }
    } else {
      // Cadastra um novo produtor
      const response = await api.post('/produtores/', this.formData, config);
      if (response.status === 201) {
        alert('Produtor cadastrado com sucesso!');
        this.produtores.push(response.data);
        this.toggleForm();
      } else {
        alert('Erro ao cadastrar produtor. Tente novamente mais tarde.');
      }
    }
  } catch (error) {
    console.error('Erro ao enviar requisição:', error);
    alert('Erro ao enviar requisição. Verifique o console para mais detalhes.');
  }
},
    // Inicia o modo de edição
    startEditing(produtor) {
      this.showForm = true;
      this.editingProdutor = true;
      this.formData = { ...produtor };
    },
    // Deleta um produtor
    async deleteProdutor(produtorId) {
      if (!confirm('Tem certeza que deseja deletar este produtor?')) {
        return;
      }
      try {
        const response = await api.delete(`/produtores/${produtorId}/`);
        if (response.status === 204) {
          alert('Produtor deletado com sucesso!');
          this.produtores = this.produtores.filter(p => p.id !== produtorId);
        } else {
          alert('Erro ao deletar produtor.');
        }
      } catch (error) {
        console.error('Erro ao deletar produtor:', error);
        alert('Erro ao deletar produtor. Verifique o console para mais detalhes.');
      }
    }
  },
  mounted() {
    this.fetchUsuarios();
    this.fetchProdutores();
  }
};
</script>

<style scoped>
.container-fluid {
  width: 100%;
  padding: 0 15px;
}

.button-container {
  text-align: left;
  margin-bottom: 20px;
}

.form-container {
  width: 100%;
  padding: 20px;
  background-color: whitesmoke;
  border: 2px solid grey;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.producer-list {
  width: 100%;
  padding: 20px;
  background-color: whitesmoke;
  border: 2px solid grey;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ddd;
  position: relative;
}

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

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.form-label {
  text-align: left;
  display: block;
  margin-bottom: 0.5rem;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.button-group .btn-back {
  margin-right: 10px;
}
</style>
