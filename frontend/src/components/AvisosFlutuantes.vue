<template>
  <div class="avisos" role="status" aria-live="polite">
    <transition-group name="aviso">
      <div v-for="aviso in estado.avisos" :key="aviso.id" :class="['aviso', aviso.tipo]"
        @click="dispensar(aviso.id)">
        <span class="icone">{{ icones[aviso.tipo] || 'ℹ' }}</span>
        <!-- white-space: pre-line no CSS preserva as quebras: erros da API
             vêm com uma linha por campo recusado. -->
        <span class="texto">{{ aviso.texto }}</span>
        <button type="button" class="fechar" aria-label="Fechar">×</button>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { estado, dispensar } from '@/notificacoes';

export default {
  name: 'AvisosFlutuantes',
  data() {
    return {
      estado,
      icones: { sucesso: '✓', erro: '✕', aviso: '!' },
    };
  },
  methods: { dispensar },
};
</script>

<style scoped>
.avisos {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 1080;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: min(420px, calc(100vw - 32px));
}

.aviso {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 6px;
  border-left: 4px solid;
  background-color: #fff;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
  cursor: pointer;
  text-align: left;
}

.aviso.sucesso { border-left-color: #1e8449; }
.aviso.erro    { border-left-color: #b03a2e; }
.aviso.aviso   { border-left-color: #b9770e; }

.icone {
  font-weight: bold;
  line-height: 1.4;
}

.aviso.sucesso .icone { color: #1e8449; }
.aviso.erro .icone    { color: #b03a2e; }
.aviso.aviso .icone   { color: #b9770e; }

.texto {
  flex: 1;
  font-size: 0.92rem;
  color: #212f3d;
  white-space: pre-line;
}

.fechar {
  background: none;
  border: none;
  font-size: 1.1rem;
  line-height: 1;
  color: #888;
  cursor: pointer;
  padding: 0;
}

.aviso-enter-active,
.aviso-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.aviso-enter-from,
.aviso-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
