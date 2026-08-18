<template>
  <div class="container-fluid">
    <h1></h1>
    <!-- Título da Lista de Propriedades -->
    <h1 v-if="!showForm" class="mt-4"><br>Lista de Propriedades</h1>
    <!-- Formulário de cadastro/edição de propriedades -->
    <div v-if="showForm" class="form-container">
      <h1>{{ editingPropriedade ? 'Editar Propriedade' : 'Cadastro de Propriedade' }}</h1>
      <form @submit.prevent="submitForm" class="propriedade-form">
        <!-- Campo para o Produtor -->
        <div class="mb-3">
          <label for="produtor" class="form-label">Produtor</label>
          <select id="produtor" v-model="formData.produtor" class="form-control" required>
            <option disabled value="">Selecione um produtor</option>
            <option v-for="produtor in produtores" :key="produtor.id" :value="produtor.id">
              {{ produtor.nome }}
            </option>
          </select>
        </div>
        <!-- Campo para o Nome -->
        <div class="mb-3">
          <label for="nome" class="form-label">Nome</label>
          <input type="text" class="form-control" id="nome" v-model="formData.nome"
            placeholder="Digite o nome da propriedade" required />
        </div>
        <!-- Campo para a Latitude -->
        <div class="mb-3">
          <label for="latitude" class="form-label">Latitude</label>
          <input type="text" class="form-control" id="latitude" v-model="formData.latitude" placeholder="ex: 12.3456789"
            required />
        </div>
        <!-- Campo para a Longitude -->
        <div class="mb-3">
          <label for="longitude" class="form-label">Longitude</label>
          <input type="text" class="form-control" id="longitude" v-model="formData.longitude"
            placeholder="ex: 98.7654321" required />
        </div>
        <!-- Campo para o Endereço -->
        <div class="mb-3">
          <label for="endereco" class="form-label">Endereço</label>
          <input type="text" class="form-control" id="endereco" v-model="formData.endereco"
            placeholder="Digite seu endereço" required />
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
          <button type="submit" class="btn-submit">{{ editingPropriedade ? 'Salvar' : 'Cadastrar' }}</button>
        </div>
      </form>
    </div>
    <!-- Lista de propriedades -->
    <div v-if="!showForm" class="propriedade-list mt-5">
      <!-- Botão para abrir o formulário de cadastro, sempre visível -->
      <div class="container-fluidd">
        <br>
        <div class="button-container">
          <button @click="toggleForm" class="btn-submit">Cadastrar nova Propriedade</button>
        </div>
        <div v-if="propriedades.length">
          <div class="row font-weight-bold mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Produtor</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Nome</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Endereço</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Cidade</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Latitude</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Longitude</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Estado</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Ação</div>
          </div>
          <div v-for="propriedade in propriedades" :key="propriedade.id" class="row user-info mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ getProdutorNome(propriedade.produtor) }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ propriedade.nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ propriedade.endereco }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ propriedade.cidade }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ propriedade.latitude }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ propriedade.longitude }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ propriedade.estado }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">
              <button @click="startEditing(propriedade)" class="btn-edit">🖊️</button>
              <button @click="deletePropriedade(propriedade.id)" class="btn-delete">🗑️</button>
            </div>
          </div>
        </div>
        <div v-else>
          <p>Nenhuma propriedade encontrada.</p>
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
        produtor: '',
        nome: '',
        longitude: '',
        latitude: '',
        endereco: '',
        cidade: '',
        estado: '',
      },
      propriedades: [],
      produtores: [],
      showForm: false,
      editingPropriedade: false,
    };
  },
  methods: {
    toggleForm() {
      this.showForm = !this.showForm;
      this.editingPropriedade = false;
      this.formData = {
        produtor: '',
        nome: '',
        longitude: '',
        latitude: '',
        endereco: '',
        cidade: '',
        estado: '',
      };
    },
    getProdutorNome(produtorId) {
      const produtor = this.produtores.find(u => u.id === produtorId);
      return produtor ? produtor.nome : 'Desconhecido';
    },
    async fetchPropriedades() {
      try {
        const response = await api.get('/propriedades/');
        this.propriedades = response.data;
      } catch (error) {
        console.error('Erro ao buscar propriedades:', error);
      }
    },
    async fetchProdutores() {
      try {
        const response = await api.get('/produtores/');
        this.produtores = response.data;
      } catch (error) {
        console.error('Erro ao buscar produtores:', error);
      }
    },
    async submitForm() {
      try {
        if (this.editingPropriedade) {
          const response = await api.put(`/propriedades/${this.formData.id}/`, this.formData);
          if (response.status === 200) {
            alert('Propriedade atualizada com sucesso!');
            this.fetchPropriedades();
            this.toggleForm();
          } else {
            alert('Erro ao atualizar propriedade.');
          }
        } else {
          const response = await api.post('/propriedades/', this.formData);
          if (response.status === 201) {
            alert('Propriedade cadastrada com sucesso!');
            this.propriedades.push(response.data);
            this.toggleForm();
          } else {
            alert('Erro ao cadastrar propriedade. Tente novamente mais tarde.');
          }
        }
      } catch (error) {
        console.error('Erro ao enviar requisição:', error);
        alert('Erro ao enviar requisição. Verifique o console para mais detalhes.');
      }
    },
    startEditing(propriedade) {
      this.formData = { ...propriedade };
      this.showForm = true;
      this.editingPropriedade = true;
    },
    async deletePropriedade(propriedadeId) {
      if (!confirm('Tem certeza que deseja deletar esta propriedade?')) return;
      try {
        const response = await api.delete(`/propriedades/${propriedadeId}/`);
        if (response.status === 204) {
          alert('Propriedade deletada com sucesso!');
          this.fetchPropriedades();
        } else {
          alert('Erro ao deletar propriedade.');
        }
      } catch (error) {
        console.error('Erro ao deletar propriedade:', error);
        alert('Erro ao deletar propriedade. Verifique o console para mais detalhes.');
      }
    },
  },
  mounted() {
    this.fetchProdutores();
    this.fetchPropriedades();
  },
};
</script>


<style scoped>
.container-fluidd {
  width: 100%;
  padding: 0 15px;
  background-color: whitesmoke;
  border: 2px solid grey;
  border-radius: 10px;
}

.form-container {
  width: 100%;
  padding: 20px;
  background-color: whitesmoke;
  border: 2px solid grey;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.propriedade-form {
  display: flex;
  flex-direction: column;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.form-group {
  flex: 1 1 150px;
  min-width: 150px;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.button-container {
  text-align: left;
  margin-bottom: 20px;
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
</style>