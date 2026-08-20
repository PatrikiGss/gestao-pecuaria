<template>
    <div class="container-fluid">
      <h1 class="titulo-tela">Alterar Senha</h1>
      <div class="form-container">
        <form @submit.prevent="submitPasswordChange" class="tela-form">
          <div class="mb-3">
            <label for="oldPassword" class="form-label">Senha atual</label>
            <input class="form-control" type="password" id="oldPassword"
              v-model="oldPassword" required placeholder="Digite sua senha atual" />
          </div>
          <div class="mb-3">
            <label for="newPassword" class="form-label">Nova senha</label>
            <input class="form-control" type="password" id="newPassword"
              v-model="newPassword" required placeholder="Digite a nova senha" />
            <small class="text-muted">
              A senha passa pelos validadores do servidor: mínimo de caracteres,
              não puramente numérica e não pode ser óbvia demais.
            </small>
          </div>
          <div class="button-group">
            <button type="button" class="btn-back" @click="cancel">Cancelar</button>
            <button type="submit" class="btn-submit">Alterar Senha</button>
          </div>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  import api from '@/interceptadorAxios';
import { erro, sucesso } from '@/notificacoes';
  import { mensagemDeErro } from '@/erros';
  import { limparSessao } from '@/sessao';

  export default {
    data() {
      return {
        oldPassword: "",
        newPassword: "",
};
    },
    methods: {
      async submitPasswordChange() {
        try {
          await api.post("/autenticacao/alterar-senha/", {
            old_password: this.oldPassword,
            new_password: this.newPassword
          });
          sucesso("Senha alterada com sucesso!"
          +" Por favor realize o login novamente.");
          // Antes so o access_token era removido: o refresh_token continuava
          // no localStorage. E 'this.isAuthenticated = false' nao fazia nada,
          // porque essa propriedade nunca existiu no data() desta tela (foi
          // copiada do App.vue).
          limparSessao();
          this.$router.push('/');
            this.oldPassword = "";
          this.newPassword = "";
        } catch (error) {
          if (error.response && error.response.status === 401) {
            erro("Sessão expirada. Faça login novamente.");
            this.$router.push('/');
          } else {
            // A API detalha o motivo por campo (senha atual incorreta, nova
            // senha fraca, nova igual à atual). Mostra isso em vez de um
            // texto genérico.
            erro(mensagemDeErro(error, "Erro ao alterar a senha."));
          }
        }
      },
      cancel() {
        this.$router.push('/tela-usuario');
      }
    }
  };
  </script>
