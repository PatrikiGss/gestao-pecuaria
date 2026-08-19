<template>
  <!-- Só aparece quando há mais de uma página: em listas curtas seria ruído. -->
  <div v-if="totalPaginas > 1" class="paginacao">
    <button type="button" class="btn-pagina" :disabled="pagina <= 1"
      @click="$emit('mudar', pagina - 1)">‹ Anterior</button>

    <span class="info">
      Página {{ pagina }} de {{ totalPaginas }}
      <small>({{ total }} registro{{ total === 1 ? '' : 's' }})</small>
    </span>

    <button type="button" class="btn-pagina" :disabled="pagina >= totalPaginas"
      @click="$emit('mudar', pagina + 1)">Próxima ›</button>
  </div>
</template>

<script>
// Controles de navegação entre páginas.
//
// Único componente reutilizável do projeto — as demais telas são componentes
// de rota e ficam em src/views/. Existe porque a API passou a paginar: sem
// estes controles, tudo além da primeira página ficaria inacessível.
export default {
  name: 'PaginacaoLista',
  props: {
    pagina: { type: Number, required: true },
    totalPaginas: { type: Number, default: 1 },
    total: { type: Number, default: 0 },
  },
  emits: ['mudar'],
};
</script>

<style scoped>
.paginacao {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin: 18px 0;
}

.btn-pagina {
  padding: 6px 14px;
  border: 1px solid #bbb;
  border-radius: 4px;
  background-color: #fff;
  cursor: pointer;
}

.btn-pagina:hover:not(:disabled) {
  background-color: #eee;
}

.btn-pagina:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.info {
  font-size: 0.9rem;
  color: #444;
}
</style>
