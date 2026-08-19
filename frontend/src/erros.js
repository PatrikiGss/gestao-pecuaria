// Traduz o corpo de erro da API numa mensagem legível para o usuário.
//
// As telas mostravam "Erro ao enviar requisição. Verifique o console" e
// jogavam fora a resposta da API — que já vem detalhada por campo, no formato
// { "cpf": ["CPF inválido."], "estado": ["..."] }. O usuário via um erro
// genérico e não tinha como saber o que corrigir.
//
// Concentrar a tradução aqui evita repetir a regra de validação no frontend:
// o backend continua sendo a fonte única da verdade, e a tela apenas exibe.

// Nome técnico do campo -> rótulo que o usuário reconhece.
const ROTULOS = {
  ph_h2o: 'pH em H₂O',
  materia_organica: 'Matéria orgânica',
  analise_solo: 'Análise de solo',
  camada_correcao: 'Camada de correção',
  calcario_calcitico: 'Calcário calcítico',
  calcario_dolomitico: 'Calcário dolomítico',
  calcario_magnesiano: 'Calcário magnesiano',
  p2o5: 'P₂O₅',
  kcl: 'KCl',
  cpf: 'CPF',
  email: 'E-mail',
  nome: 'Nome',
  telefone: 'Telefone',
  estado: 'Estado',
  cidade: 'Cidade',
  endereco: 'Endereço',
  latitude: 'Latitude',
  longitude: 'Longitude',
  propriedade: 'Propriedade',
  produtor: 'Produtor',
  laboratorio: 'Laboratório',
  cultura: 'Cultura',
  gleba: 'Gleba',
  laudo: 'Laudo',
  area: 'Área',
  data: 'Data',
  password: 'Senha',
  old_password: 'Senha atual',
  new_password: 'Nova senha',
}

function rotulo (campo) {
  if (ROTULOS[campo]) return ROTULOS[campo]
  // Fallback: 'materia_organica' -> 'Materia organica'
  const texto = campo.replace(/_/g, ' ')
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

function achatar (valor) {
  if (Array.isArray(valor)) return valor.map(achatar).join(' ')
  if (valor && typeof valor === 'object') return Object.values(valor).map(achatar).join(' ')
  return String(valor)
}

export function mensagemDeErro (error, padrao = 'Não foi possível concluir a operação.') {
  const resposta = error && error.response

  // Sem resposta = a requisição nem chegou ao servidor.
  if (!resposta) {
    return 'Não foi possível falar com o servidor. Verifique se a API está no ar.'
  }

  if (resposta.status === 403) return 'Você não tem permissão para esta ação.'
  if (resposta.status === 404) return 'Registro não encontrado.'
  if (resposta.status >= 500) return 'Erro interno do servidor. Tente novamente em instantes.'

  const dados = resposta.data
  if (!dados) return padrao
  if (typeof dados === 'string') return dados
  if (dados.detail) return achatar(dados.detail)

  const linhas = Object.entries(dados).map(([campo, valor]) => {
    const texto = achatar(valor)
    return campo === 'non_field_errors' ? texto : `${rotulo(campo)}: ${texto}`
  })

  return linhas.length ? linhas.join('\n') : padrao
}

export default mensagemDeErro
