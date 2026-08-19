import { extrairLista, extrairPaginacao } from '@/lista'

// Estado de paginação compartilhado pelas 7 telas de listagem.
//
// Antes cada tela repetia o mesmo bloco: 'pagina', 'paginacao', o cálculo do
// total de páginas e o método de troca. Sete cópias do mesmo código são sete
// lugares para corrigir quando algo muda.
//
// O mixin cobre apenas a parte idêntica. Formulários, campos e colunas
// continuam em cada tela, porque são genuinamente diferentes: unificá-los
// exigiria uma camada de configuração que custaria mais do que a duplicação
// que sobra.
//
// Uso na tela:
//   mixins: [listaPaginada],
//   methods: {
//     recarregar() { this.fetchProdutores(); },       // exigido pelo mixin
//     async fetchProdutores() {
//       const r = await api.get(`/produtores/?page=${this.pagina}`);
//       this.produtores = this.aplicarPaginacao(r);
//     },
//   }
export default {
  data () {
    return {
      pagina: 1,
      paginacao: { total: 0, totalPaginas: 1 },
    }
  },
  methods: {
    // Lê a resposta da API: atualiza os metadados e devolve os itens.
    aplicarPaginacao (resposta) {
      this.paginacao = extrairPaginacao(resposta, this.pagina)
      return extrairLista(resposta)
    },

    irParaPagina (numero) {
      if (numero < 1 || numero > this.paginacao.totalPaginas) return
      this.pagina = numero
      if (typeof this.recarregar === 'function') {
        this.recarregar()
      } else {
        console.warn('A tela usa listaPaginada mas não definiu recarregar().')
      }
    },
  },
}
