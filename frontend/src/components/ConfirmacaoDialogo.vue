<template>
  <div v-if="estado.confirmacao" class="fundo" @click.self="responder(false)">
    <div class="caixa" role="dialog" aria-modal="true">
      <p class="pergunta">{{ estado.confirmacao.pergunta }}</p>
      <div class="botoes">
        <button type="button" class="btn-cancelar" @click="responder(false)">
          {{ estado.confirmacao.cancelarTexto }}
        </button>
        <button type="button" class="btn-confirmar" ref="botaoConfirmar" @click="responder(true)">
          {{ estado.confirmacao.confirmarTexto }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { estado } from '@/notificacoes';

// Substitui o confirm() nativo. A diferença que importa: este não trava a aba
// enquanto espera, então a chamada precisa usar 'await confirmar(...)'.
export default {
  name: 'ConfirmacaoDialogo',
  data() {
    return { estado };
  },
  watch: {
    'estado.confirmacao'(valor) {
      if (valor) {
        // Foco no botão de ação para permitir confirmar pelo teclado.
        this.$nextTick(() => this.$refs.botaoConfirmar && this.$refs.botaoConfirmar.focus());
      }
    },
  },
  mounted() {
    // Esc cancela, como no diálogo nativo.
    this._aoTeclar = (e) => {
      if (e.key === 'Escape' && estado.confirmacao) this.responder(false);
    };
    window.addEventListener('keydown', this._aoTeclar);
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this._aoTeclar);
  },
  methods: {
    responder(resposta) {
      if (estado.confirmacao) estado.confirmacao.responder(resposta);
    },
  },
};
</script>

<style scoped>
.fundo {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1090;
}

.caixa {
  background-color: #fff;
  border-radius: 8px;
  padding: 22px 24px;
  max-width: min(440px, calc(100vw - 32px));
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.pergunta {
  margin: 0 0 20px;
  font-size: 1rem;
  color: #212f3d;
  text-align: left;
}

.botoes {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-cancelar,
.btn-confirmar {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.95rem;
}

.btn-cancelar {
  border: 1px solid #bbb;
  background-color: #fff;
  color: #333;
}

.btn-cancelar:hover {
  background-color: #eee;
}

.btn-confirmar {
  border: none;
  background-color: #b03a2e;
  color: #fff;
}

.btn-confirmar:hover {
  background-color: #922e24;
}
</style>
