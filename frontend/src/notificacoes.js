import { reactive } from 'vue'

// Substitui alert() e confirm() do navegador.
//
// Os nativos travam a aba inteira até o clique, não aceitam estilo nenhum,
// aparecem com o nome do domínio no título e não podem ser testados sem
// interceptar métodos globais. Aqui o estado é reativo e renderizado pelos
// componentes Notificacoes.vue e ConfirmacaoDialogo.vue, montados no App.vue.

let proximoId = 1

export const estado = reactive({
  avisos: [],
  // Confirmação pendente: guarda a pergunta e a função que devolve a resposta
  // à chamada que está aguardando.
  confirmacao: null,
})

const DURACAO = { sucesso: 3500, erro: 7000, aviso: 5000 }

export function notificar (texto, tipo = 'sucesso') {
  if (!texto) return
  const id = proximoId++
  estado.avisos.push({ id, texto: String(texto), tipo })

  // Erros ficam mais tempo na tela: costumam ter várias linhas (uma por campo
  // recusado pela API) e precisam ser lidos, não só percebidos.
  const ms = DURACAO[tipo] || DURACAO.aviso
  setTimeout(() => dispensar(id), ms)
  return id
}

export const sucesso = (texto) => notificar(texto, 'sucesso')
export const erro = (texto) => notificar(texto, 'erro')
export const aviso = (texto) => notificar(texto, 'aviso')

export function dispensar (id) {
  const i = estado.avisos.findIndex((a) => a.id === id)
  if (i !== -1) estado.avisos.splice(i, 1)
}

// Devolve uma Promise que resolve para true/false — mesma semântica do
// confirm() nativo, mas sem travar a interface. Quem chama usa 'await'.
export function confirmar (pergunta, { confirmarTexto = 'Confirmar', cancelarTexto = 'Cancelar' } = {}) {
  return new Promise((resolve) => {
    estado.confirmacao = {
      pergunta,
      confirmarTexto,
      cancelarTexto,
      responder (resposta) {
        estado.confirmacao = null
        resolve(resposta)
      },
    }
  })
}
