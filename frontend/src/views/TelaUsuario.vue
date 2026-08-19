<template>
  <div class="container-fluid">
    <!-- Título da página -->
    <h1></h1>
    <!-- Exibe o título "Lista de Usuários" se o formulário não estiver sendo exibido -->
    <h1 v-if="!showForm"><br>Lista de Usuários</h1>
    <h1 v-if="!showForm"><br></h1>

    <!-- Formulário de cadastro de usuários -->
    <div v-if="showForm" class="form-container">
      <!-- Título do formulário, muda dinamicamente entre 'Editar Usuário' e 'Cadastro de Usuários' -->
      <h1>{{ editingUser ? 'Editar Usuário' : 'Cadastro de Usuários' }}</h1>
      <!-- Formulário de usuário -->
      <form @submit.prevent="submitForm" class="user-form">
        <!-- Campo para o nome -->
        <div class="mb-3">
          <label for="nome" class="form-label">Nome</label>
          <input type="text" class="form-control" id="nome" v-model="formData.nome" placeholder="Digite seu nome" required >
        </div>
        <!-- Campo para o email -->
        <div class="mb-3">
          <label for="email" class="form-label">E-mail</label>
          <input type="email" class="form-control" id="email" v-model="formData.email" placeholder="name@example.com" required >
        </div>
        <!-- Campo para a senha -->
        <div v-if="!editingUser" class="mb-3">
          <label for="password" class="form-label">Senha</label>
          <input type="password" class="form-control" id="password" v-model="formData.password"
            placeholder="Digite sua senha" required >
        </div>
        <!-- Campo para o telefone -->
        <div class="mb-3">
          <label for="telefone" class="form-label">Telefone</label>
          <input type="text" class="form-control" id="telefone" v-model="formData.telefone"
            placeholder="(00)00000-0000" maxlength="15" required >
        </div>
        <!-- Campo para o CPF -->
        <div class="mb-3">
          <label for="cpf" class="form-label">CPF</label>
          <input type="text" class="form-control" id="cpf" v-model="formData.cpf"
            placeholder="Apenas números, EX: 12345678900" maxlength="14" required >
        </div>
        <!-- Créditos é somente-leitura na API (valor fixo definido pelo
             servidor), por isso aparece apenas na listagem, não no formulário. -->

        <!-- Grupo de botões -->
        <div class="button-group">
          <!-- Botão para voltar sem salvar alterações -->
          <button @click="toggleForm" class="btn-back">Voltar</button>
          <!-- Botão para enviar ou atualizar o formulário -->
          <button type="submit" class="btn-submit">{{ editingUser ? 'Atualizar' : 'Enviar' }}</button>
        </div>
      </form>
    </div>

    <!-- Lista de usuários cadastrados -->
    <div v-else class="user-list-container">
      <!-- Botão para abrir o formulário de cadastro -->
      <!-- <div class="button-container">
        <button v-if="!isAuthenticated" @click="toggleForm" class="btn-submit">Cadastrar Novo Usuário</button>
      </div> -->
      <!-- Verifica se há usuários para exibir -->
      <div v-if="usuarios.length">
        <div class="container-fluid">
          <!-- Cabeçalho da tabela de usuários -->
          <div class="row font-weight-bold mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Nome</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">E-mail</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Telefone</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">CPF</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Créditos</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Ações</div>
          </div>
          <!-- Loop para exibir cada usuário na tabela -->
          <div v-for="usuario in usuarios" :key="usuario.id" class="row user-info mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ usuario.nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ usuario.email }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ usuario.telefone }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ usuario.cpf }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ usuario.creditos }}</div>
            <!-- Botões para editar e excluir usuários -->
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">
              <button @click="editUser(usuario)" class="btn-edit">🖊️</button>
              <button @click="deleteUser(usuario.id)" class="btn-delete">🗑️</button>
            </div>
          </div>
        </div>
      </div>
      <!-- Exibe mensagem se não houver usuários cadastrados -->
      <div v-else>
        <p>Nenhum usuário encontrado.</p>
      </div>
    </div>
  </div>
</template>


<script>
import api from '@/interceptadorAxios';
import { confirmar, erro, sucesso } from '@/notificacoes';
import { mensagemDeErro } from '@/erros';
import { extrairLista } from '@/lista'; // Importa o Axios configurado

export default {
  data() {
    return {
      showForm: false, // Define se o formulário de usuário deve ser exibido
      formData: { // Dados do formulário de usuário
        nome: '',
        email: '',
        telefone: '',
        cpf: '',
        password: '', // Este campo será omitido na atualização
      },
      usuarios: [], // Lista de usuários
      editingUser: null, // Mantém o ID do usuário que está sendo editado
    };
  },
  methods: {
    // Alterna a exibição do formulário de usuário
    toggleForm() {
      this.showForm = !this.showForm; // Inverte o estado do formulário
      this.clearForm(); // Limpa os dados do formulário
    },
    // Método para enviar o formulário
    // Monta o corpo da requisicao sem a senha quando ela esta vazia:
    // a API valida a forca da senha e rejeitaria uma string vazia.
    montarPayload() {
      const payload = { ...this.formData };
      if (!payload.password) {
        delete payload.password;
      }
      return payload;
    },
    async submitForm() {
      try {
        if (this.editingUser) {
          // Atualiza o usuário existente
          const response = await api.put(`/usuarios/${this.editingUser}/`, this.montarPayload());
          if (response.status === 200) {
            sucesso('Usuário atualizado com sucesso!');
          } else {
            erro('Erro ao atualizar usuário.');
          }
        } else {
          // Cadastra um novo usuário
          const response = await api.post('/usuarios/', this.montarPayload());
          if (response.status === 201) {
            sucesso('Cadastro realizado com sucesso!');
          } else {
            erro('Erro ao cadastrar usuário. Tente novamente mais tarde.');
          }
        }
        this.fetchUsuarios(); // Atualiza a lista de usuários
        this.showForm = false; // Oculta o formulário após o cadastro ou atualização
      } catch (error) {
        console.error('Erro ao enviar requisição:', error);
        erro(mensagemDeErro(error));
      }
    },
    // Busca todos os usuários
    async fetchUsuarios() {
      try {
        const response = await api.get('/usuarios/');
        this.usuarios = extrairLista(response) // Atribui a lista de usuários ao array
      } catch (error) {
        console.error('Erro ao buscar usuários:', error);
        // Opcional: Mostrar uma mensagem ao usuário
      }
    },
    // Método para editar um usuário
    editUser(usuario) {
      this.editingUser = usuario.id;
      // Copia apenas os campos editaveis. Antes era '{ ...usuario }' seguido
      // de 'formData.password = usuario.password', o que reenviava no PUT a
      // senha e todas as flags vindas da API (is_staff, is_superuser,
      // groups...). A senha nao trafega mais: a API nao a devolve no GET, e
      // a troca de senha tem tela propria (/tela-edicao).
      this.formData = {
        nome: usuario.nome,
        email: usuario.email,
        telefone: usuario.telefone,
        cpf: usuario.cpf,
        password: '',
      };
      this.showForm = true;
    },
    // Método para limpar o formulário
    clearForm() {
      this.formData = {
        nome: '',
        email: '',
        telefone: '',
        cpf: '',
        password: '',
      };
      this.editingUser = null; // Reseta o estado de edição
    },
    // Método para excluir um usuário
    async deleteUser(userId) {
      if (await confirmar('Tem certeza que deseja excluir este usuário?')) {
        try {
          const response = await api.delete(`/usuarios/${userId}/`);
          if (response.status === 204) {
            sucesso('Usuário excluído com sucesso!');
            this.fetchUsuarios(); // Atualiza a lista de usuários
          } else {
            erro('Erro ao excluir usuário.');
          }
        } catch (error) {
          console.error('Erro ao excluir usuário:', error);
          erro(mensagemDeErro(error));
        }
      }
    },
  },
  created() {
    this.fetchUsuarios(); // Busca a lista de usuários quando o componente é criado
  },
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
.user-list-container {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  background-color: whitesmoke;
  border: 2px solid grey;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* Estilos para a exibição das informações dos usuários */
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

/* Linha vertical entre as colunas */
.user-info>div:not(:last-child)::after {
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
