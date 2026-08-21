<template>
  <div class="container-fluid">
    <h1 v-if="!showForm && !showDetail" class="titulo-tela">Lista de Análises de Solo</h1>
    <h1 v-if="showDetail" class="titulo-tela">Detalhes da Análise</h1>

    <!-- Cada seção na sua própria caixa. Antes um único .form-container
         envolvia a tela toda, e como ele limita a largura para leitura de
         formulário, a listagem saía espremida. -->
    <div>
      <div v-if="showForm" class="form-container">
        <h1 class="titulo-tela">{{ editingSolo ? 'Editar Análise de Solo' : 'Cadastro de Análise de Solo' }}</h1>
        <form @submit.prevent="submitForm" class="tela-form">
          <!-- Campo para o laboratorio -->
          <div class="mb-3">
            <label for="laboratorio" class="form-label">Laboratório</label>
            <select id="laboratorio" v-model="formData.laboratorio" class="form-control" required>
              <option disabled value="">Selecione um laboratório</option>
              <option v-for="laboratorio in laboratorios" :key="laboratorio.id" :value="laboratorio.id">
                {{ laboratorio.nome }}
              </option>
            </select>
          </div>
          <!-- Propriedade serve para filtrar as glebas; a análise guarda
               apenas a gleba, e a propriedade vem por ela. -->
          <div class="mb-3">
            <label for="propriedade" class="form-label">Propriedade</label>
            <select id="propriedade" v-model="propriedadeSelecionada" class="form-control" required>
              <option disabled value="">Selecione uma propriedade</option>
              <option v-for="propriedade in propriedades" :key="propriedade.id" :value="propriedade.id">
                {{ propriedade.nome }}
              </option>
            </select>
          </div>
          <!-- Gleba: lista em cascata, dependente da propriedade escolhida -->
          <div class="mb-3">
            <label for="gleba" class="form-label">Gleba</label>
            <select id="gleba" v-model="formData.gleba" class="form-control" required
              :disabled="!propriedadeSelecionada">
              <option disabled value="">
                {{ propriedadeSelecionada ? 'Selecione uma gleba' : 'Escolha a propriedade primeiro' }}
              </option>
              <option v-for="gleba in glebasDaPropriedade" :key="gleba.id" :value="gleba.id">
                {{ gleba.nome }}
              </option>
            </select>
            <small v-if="propriedadeSelecionada && !glebasDaPropriedade.length" class="text-muted">
              Nenhuma gleba cadastrada nesta propriedade. Cadastre em Glebas.
            </small>
          </div>
          <!-- Campo para o cultura -->
          <div class="mb-3">
            <label for="cultura" class="form-label">Cultura</label>
            <select id="cultura" v-model="formData.cultura" class="form-control" required>
              <option disabled value="">Selecione uma cultura</option>
              <option v-for="cultura in culturas" :key="cultura.id" :value="cultura.id">
                {{ cultura.nome }}
              </option>
            </select>
          </div>
          <!-- A calagem é calibrada para 0–20 cm. Sem saber a camada, uma
               análise de subsuperfície entraria na mesma conta e produziria
               uma dose errada sem aviso nenhum. -->
          <div class="mb-3">
            <label for="camada" class="form-label">Camada amostrada</label>
            <select id="camada" class="form-control" v-model="formData.camada" required>
              <option value="0-20">0 a 20 cm (superficial)</option>
              <option value="20-40">20 a 40 cm (subsuperficial)</option>
              <option value="40-60">40 a 60 cm</option>
              <option value="outra">Outra</option>
            </select>
            <small class="text-muted">
              A recomendação de calagem só é calculada para a camada de 0 a 20 cm.
            </small>
          </div>
          <!-- Campo para o data -->
          <div class="mb-3">
            <label for="data" class="form-label">Data</label>
            <input type="date" class="form-control" id="data" v-model="formData.data" required :max="hoje" />
          </div>
          <!-- Campo para o area -->
          <div class="mb-3">
            <label for="area" class="form-label">Área (ha)</label>
            <input type="number" step="0.1" id="area" v-model="formData.area" placeholder="Ex: 10.50" required min="0" />
          </div>
          <div class="mb-3">
            <label for="laudo" class="form-label">Laudo</label>
            <input type="text" id="laudo" v-model="formData.laudo" placeholder="Insira o laudo" required />
          </div>
          <!-- Campo para o ph_h2o -->
          <div class="mb-3">
            <label for="ph_h2o" class="form-label">pH em H₂O</label>
            <input type="number" step="0.01" id="ph_h2o" v-model="formData.ph_h2o" placeholder="Ex: 5.5" required min="0" max="14" />
          </div>
          <!-- Campo para o s -->
          <div class="mb-3">
            <label for="s" class="form-label">Enxofre (S)</label>
            <input type="number" step="0.01" id="s" v-model="formData.s" placeholder="Ex: 12.5" required min="0" />
          </div>
          <!-- ATENÇÃO: os rótulos destes dois campos estavam trocados entre si.
               "Potássio (K)" apontava para a coluna 'p' e "Fósforo (P)" para a
               coluna 'k', então tudo que era digitado ia para a coluna errada.
               Os exemplos confirmavam a troca: 0,05 é ordem de grandeza de K em
               cmolc/dm³ e 5,0 é de P em mg/dm³. A migração 0007 corrige os
               dados já gravados. -->
          <div class="mb-3">
            <label for="p" class="form-label">Fósforo (P) — mg/dm³</label>
            <input type="number" step="0.01" id="p" v-model="formData.p" placeholder="Ex: 5.0" required min="0" />
          </div>
          <div class="mb-3">
            <label for="k" class="form-label">Potássio (K) — cmolc/dm³</label>
            <input type="number" step="0.01" id="k" v-model="formData.k" placeholder="Ex: 0.05" required min="0" />
          </div>
          <!-- Campo para o ca -->
          <div class="mb-3">
            <label for="ca" class="form-label">Cálcio (Ca)</label>
            <input type="number" step="0.01" id="ca" v-model="formData.ca" placeholder="Ex: 3.0" required min="0" />
          </div>
          <!-- Campo para o mg -->
          <div class="mb-3">
            <label for="mg" class="form-label">Magnésio (Mg)</label>
            <input type="number" step="0.01" id="mg" v-model="formData.mg" placeholder="Ex: 1.5" required min="0" />
          </div>
          <!-- Campo para o na -->
          <div class="mb-3">
            <label for="na" class="form-label">Sódio (Na)</label>
            <input type="number" step="0.01" id="na" v-model="formData.na" placeholder="Ex: 0.5" required min="0" />
          </div>
          <!-- Campo para o al -->
          <div class="mb-3">
            <label for="al" class="form-label">Alumínio (Al)</label>
            <input type="number" step="0.01" id="al" v-model="formData.al" placeholder="Ex: 0.2" required min="0" />
          </div>
          <!-- Campo para o h -->
          <div class="mb-3">
            <label for="h" class="form-label">Hidrogênio (H)</label>
            <input type="number" step="0.01" id="h" v-model="formData.h" placeholder="Ex: 1.0" required min="0" />
          </div>
          <!-- Campo para o materia organica -->
          <div class="mb-3">
            <label for="materia_organica" class="form-label">Matéria Orgânica</label>
            <input type="number" step="0.01" id="materia_organica" v-model="formData.materia_organica"
              placeholder="Ex: 2.0" required min="0" />
          </div>
          <!-- Campo para o areia -->
          <div class="mb-3">
            <label for="areia" class="form-label">Areia</label>
            <input type="number" step="0.01" id="areia" v-model="formData.areia" placeholder="Ex: 45.0" required min="0" />
          </div>
          <!-- Campo para o silte -->
          <div class="mb-3">
            <label for="silte" class="form-label">Silte</label>
            <input type="number" step="0.01" id="silte" v-model="formData.silte" placeholder="Ex: 30.0" required min="0" />
          </div>
                    <!-- Campo para o argila -->
                   <div class="mb-3">
            <label for="argila" class="form-label">Argila</label>
            <input type="number" step="0.01" id="argila" v-model="formData.argila" placeholder="Ex: 25.0" required min="0" />
          </div>
          <!-- Campo para o mn -->
          <div class="mb-3">
            <label for="mn" class="form-label">Manganês (Mn)</label>
            <input type="number" step="0.01" id="mn" v-model="formData.mn" placeholder="Ex: 0.02" required min="0" />
          </div>
          <!-- Campo para o fe -->
          <div class="mb-3">
            <label for="fe" class="form-label">Ferro (Fe)</label>
            <input type="number" step="0.01" id="fe" v-model="formData.fe" placeholder="Ex: 0.10" required min="0" />
          </div>
          <!-- Campo para o cu -->
          <div class="mb-3">
            <label for="cu" class="form-label">Cobre (Cu)</label>
            <input type="number" step="0.01" id="cu" v-model="formData.cu" placeholder="Ex: 0.05" required min="0" />
          </div>
          <!-- Campo para o zn -->
          <div class="mb-3">
            <label for="zn" class="form-label">Zinco (Zn)</label>
            <input type="number" step="0.01" id="zn" v-model="formData.zn" placeholder="Ex: 0.10" required min="0" />
          </div>
          <!-- Campo para o b -->
          <div class="mb-3">
            <label for="b" class="form-label">Boro (B)</label>
            <input type="number" step="0.01" id="b" v-model="formData.b" placeholder="Ex: 0.02" required min="0" />
          </div>
          <!-- Botões de ação -->
          <div class="button-group">
            <button @click="toggleForm" class="btn-back">Voltar</button>
            <button type="submit" class="btn-submit">{{ editingSolo ? 'Salvar' : 'Cadastrar' }}</button>
          </div>
        </form>
      </div>
      <!-- Listagem -->
      <div v-if="!showForm && !showDetail" class="lista-container">
        <div class="button-container">
          <button @click="toggleForm" class="btn-submit">Cadastrar nova análise de solo</button>
        </div>

        <!-- Barra de filtros.
             A API já filtrava por propriedade, gleba, cultura e intervalo de
             datas (apps/core/filtros.py), mas nada disso tinha interface: com
             o histórico paginado, achar a análise de uma gleba específica
             exigia percorrer página por página. O filtro roda no SERVIDOR —
             filtrar no cliente só esconderia linhas da página atual. -->
        <div class="filtros">
          <div class="filtro">
            <label for="f-propriedade">Propriedade</label>
            <select id="f-propriedade" v-model="filtros.propriedade">
              <option value="">Todas</option>
              <option v-for="p in propriedades" :key="p.id" :value="p.id">{{ p.nome }}</option>
            </select>
          </div>
          <div class="filtro">
            <label for="f-gleba">Gleba</label>
            <select id="f-gleba" v-model="filtros.gleba" :disabled="!filtros.propriedade">
              <option value="">{{ filtros.propriedade ? 'Todas' : 'Escolha a propriedade' }}</option>
              <option v-for="g in glebasDoFiltro" :key="g.id" :value="g.id">{{ g.nome }}</option>
            </select>
          </div>
          <div class="filtro">
            <label for="f-cultura">Cultura</label>
            <select id="f-cultura" v-model="filtros.cultura">
              <option value="">Todas</option>
              <option v-for="c in culturas" :key="c.id" :value="c.id">{{ c.nome }}</option>
            </select>
          </div>
          <div class="filtro">
            <label for="f-de">De</label>
            <input id="f-de" type="date" v-model="filtros.data_apos" :max="hoje" />
          </div>
          <div class="filtro">
            <label for="f-ate">Até</label>
            <input id="f-ate" type="date" v-model="filtros.data_antes" :max="hoje" />
          </div>
          <div class="filtro filtro-acao">
            <button type="button" class="btn-back" :disabled="!temFiltro" @click="limparFiltros">
              Limpar
            </button>
          </div>
        </div>
        <p v-if="temFiltro" class="resumo-filtro">
          {{ paginacao.total }}
          {{ paginacao.total === 1 ? 'análise encontrada' : 'análises encontradas' }}
          com os filtros aplicados.
        </p>
        <div v-if="analisesSolo.length">
          <!-- Cabeçalho da tabela de analises -->
          <div class="row lista-cabecalho mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Laboratório</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Propriedade</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Cultura</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Data</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Gleba</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">Área</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Laudo</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">Ações</div>
          </div>
          <!-- Os nomes vêm prontos da API (laboratorio_nome, cultura_nome).
               Antes eram resolvidos no cliente, o que exigia carregar as listas
               inteiras de laboratórios e culturas só para traduzir ids — e
               mostrava "Desconhecido" enquanto elas não chegavam. -->
          <div v-for="analisesolo in analisesSolo" :key="analisesolo.id" class="row lista-linha mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ analisesolo.laboratorio_nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ analisesolo.propriedade_nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ analisesolo.cultura_nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ analisesolo.data }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ analisesolo.gleba_nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ analisesolo.area }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ analisesolo.laudo }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">
              <button @click="startEditing(analisesolo)" class="btn-edit">🖊️</button>
              <button @click="deleteSolo(analisesolo.id)" class="btn-delete">🗑️</button>
              <button @click="viewDetails(analisesolo)" class="btn-detalhe" title="Ver detalhes">🔎</button>
            </div>
          </div>
        </div>
        <div v-else>
          <!-- Distingue "não há nada cadastrado" de "o filtro não achou nada":
               sem isso, um filtro restritivo parece base vazia. -->
          <p v-if="temFiltro">
            Nenhuma análise corresponde aos filtros.
            <button type="button" class="link-limpar" @click="limparFiltros">Limpar filtros</button>
          </p>
          <p v-else>Nenhuma análise de solo encontrada.</p>
        </div>
        <PaginacaoLista :pagina="pagina" :total-paginas="paginacao.totalPaginas"
          :total="paginacao.total" @mudar="irParaPagina" />
      </div>

      <!-- Visualização dos detalhes da análise de solo -->
      <div v-if="showDetail" class="lista-container">
        <h2>Detalhes da Análise de Solo de laudo: {{ selectedSolo.laudo }}</h2>

        <!-- Índices derivados, calculados pelo backend a partir dos valores da
             própria análise (apps/core/agronomia.py). Não ficam gravados: são
             recalculados a cada leitura, para nunca divergirem da origem. -->
        <div v-if="selectedSolo.diagnostico" class="diagnostico">
          <h3>Diagnóstico do solo</h3>
          <div class="indices">
            <div class="indice destaque">
              <span class="rotulo">Saturação por bases (V%)</span>
              <span class="valor">
                {{ formatar(selectedSolo.diagnostico.saturacao_bases) }}%
                <small v-if="selectedSolo.diagnostico.classificacao_v" class="faixa">
                  {{ selectedSolo.diagnostico.classificacao_v }}
                </small>
              </span>
            </div>
            <div class="indice destaque">
              <span class="rotulo">Saturação por alumínio (m%)</span>
              <span class="valor">
                {{ formatar(selectedSolo.diagnostico.saturacao_aluminio) }}%
                <small v-if="selectedSolo.diagnostico.classificacao_m" class="faixa">
                  {{ selectedSolo.diagnostico.classificacao_m }}
                </small>
              </span>
            </div>
            <div class="indice">
              <span class="rotulo">Soma de bases (SB)</span>
              <span class="valor">{{ formatar(selectedSolo.diagnostico.soma_bases) }}</span>
            </div>
            <div class="indice">
              <span class="rotulo">CTC efetiva (t)</span>
              <span class="valor">{{ formatar(selectedSolo.diagnostico.ctc_efetiva) }}</span>
            </div>
            <div class="indice">
              <span class="rotulo">CTC a pH 7 (T)</span>
              <span class="valor">{{ formatar(selectedSolo.diagnostico.ctc_potencial) }}</span>
            </div>
            <div class="indice">
              <span class="rotulo">Classe textural</span>
              <span class="valor">{{ selectedSolo.diagnostico.classe_textural || '—' }}</span>
            </div>
            <div class="indice">
              <span class="rotulo">Relação Ca:Mg</span>
              <span class="valor">{{ formatar(selectedSolo.diagnostico.relacao_ca_mg) }}</span>
            </div>
            <div class="indice">
              <span class="rotulo">Participação de K na CTC</span>
              <span class="valor">{{ formatar(selectedSolo.diagnostico.participacao_k) }}%</span>
            </div>
          </div>
          <p class="nota">
            Bases em cmolc/dm³. Índices calculados a partir dos valores desta
            análise.
          </p>
        </div>

        <!-- Recomendação de calagem, calculada pelo backend em
             apps/core/agronomia.py. -->
        <div v-if="selectedSolo.calagem" class="calagem">
          <h3>Recomendação de calagem</h3>

          <div v-if="!selectedSolo.calagem.aplicavel" class="aviso-camada">
            {{ selectedSolo.calagem.motivo }}
          </div>

          <template v-else>
            <div class="indices">
              <div class="indice destaque">
                <span class="rotulo">Necessidade de calagem</span>
                <span class="valor">{{ formatar(selectedSolo.calagem.necessidade_t_ha) }} t/ha</span>
              </div>
              <div class="indice destaque">
                <span class="rotulo">
                  Dose do produto
                  <template v-if="selectedSolo.calagem.calcario_sugerido">
                    — {{ selectedSolo.calagem.calcario_sugerido }}
                  </template>
                </span>
                <span class="valor">{{ formatar(selectedSolo.calagem.dose_corretivo_t_ha) }} t/ha</span>
              </div>
              <div class="indice">
                <span class="rotulo">Tipo indicado</span>
                <span class="valor">{{ rotuloCalcario(selectedSolo.calagem.tipo_indicado) }}</span>
              </div>
              <div class="indice">
                <span class="rotulo">Método</span>
                <span class="valor metodo">{{ selectedSolo.calagem.metodo }}</span>
              </div>
            </div>

            <!-- O que falta cadastrar para o cálculo ficar completo. -->
            <ul v-if="selectedSolo.calagem.pendencias && selectedSolo.calagem.pendencias.length"
              class="pendencias">
              <li v-for="(p, i) in selectedSolo.calagem.pendencias" :key="i">{{ p }}</li>
            </ul>

            <p class="nota">
              Necessidade para incorporação em {{ selectedSolo.calagem.camada_cm }} cm.
              O tipo de calcário vem da relação Ca:Mg do solo. Doses de N, P e K
              não são calculadas — dependem de tabelas de calibração por região
              e cultura.
            </p>
          </template>
        </div>

        <div class="table-responsive">
  <table class="table">
    <thead>
      <tr>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">pH em H₂O</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Enxofre (S)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Fósforo (P)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Potássio (K)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Cálcio (Ca)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Magnésio (Mg)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Sódio (Na)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Alumínio (Al)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Hidrogênio (H)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Matéria orgânica</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Areia</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Silte</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Argila</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Manganês (Mn)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Ferro (Fe)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Cobre (Cu)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Zinco (Zn)</th>
        <th scope="col" class="col-12 col-sm-6 col-md-4 col-lg-2">Boro (B)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
      <td>{{ selectedSolo.ph_h2o }}</td>
      <td>{{ selectedSolo.s }}</td>
      <td>{{ selectedSolo.p }}</td>
      <td>{{ selectedSolo.k }}</td>
      <td>{{ selectedSolo.ca }}</td>
      <td>{{ selectedSolo.mg }}</td>
      <td>{{ selectedSolo.na }}</td>
      <td>{{ selectedSolo.al }}</td>
      <td>{{ selectedSolo.h }}</td>
      <td>{{ selectedSolo.materia_organica }}</td>
      <td>{{ selectedSolo.areia }}</td>
      <td>{{ selectedSolo.silte }}</td>
      <td>{{ selectedSolo.argila }}</td>
      <td>{{ selectedSolo.mn }}</td>
      <td>{{ selectedSolo.fe }}</td>
      <td>{{ selectedSolo.cu }}</td>
      <td>{{ selectedSolo.zn }}</td>
      <td>{{ selectedSolo.b }}</td>
     </tr>
    </tbody>
   </table>
  </div>
  <div class="button-container">
  <button @click="showDetail = false" class="btn-back">Voltar</button>
</div>
      </div>
    </div>
  </div>
</template>


<!---->


<script>
import api from '@/interceptadorAxios';
import { confirmar, erro, sucesso } from '@/notificacoes';
import PaginacaoLista from '@/components/PaginacaoLista.vue';
import listaPaginada from '@/mixins/listaPaginada';
import { mensagemDeErro } from '@/erros';
import { extrairLista, PARAMS_LISTA_COMPLETA, TAMANHO_LISTA_COMPLETA } from '@/lista';

export default {
  components: { PaginacaoLista },
  mixins: [listaPaginada],
  data() {
    return {
      formData: {
        laboratorio: null,
        cultura: null,
        camada: '0-20',
        data: '',
        gleba: '',
        area: '',
        laudo: '',
        ph_h2o: '',
        s: '',
        p: '',
        k: '',
        ca: '',
        mg: '',
        na: '',
        al: '',
        h: '',
        materia_organica: '',
        areia: '',
        silte: '',
        argila: '',
        mn: '',
        fe: '',
        cu: '',
        zn: '',
        b: '',
      },
      analisesSolo: [],
      laboratorios: [],
      propriedades: [],
      culturas: [],
      // Glebas da propriedade escolhida NO FORMULÁRIO, buscadas no servidor.
      glebasDaPropriedade: [],
      // Glebas da propriedade escolhida NO FILTRO. São listas separadas porque
      // filtrar a listagem e preencher o formulário são escolhas independentes.
      glebasDoFiltro: [],
      // Nao faz parte do formulario enviado: serve so para filtrar as glebas.
      propriedadeSelecionada: '',
      // Estado dos filtros da listagem. Enviados como query string para a API.
      filtros: {
        propriedade: '',
        gleba: '',
        cultura: '',
        data_apos: '',
        data_antes: '',
      },
      showForm: false,
      showDetail: false,
      editingSolo: false,
      selectedSolo: null,
    };
  },
  computed: {
    // Trava o seletor de data em hoje: o backend recusa data futura,
    // e assim o usuario nem consegue escolher uma.
    //
    // Montado a partir dos componentes LOCAIS da data, e não com
    // toISOString(), que converte para UTC. No Brasil (UTC-3), das 21h à
    // meia-noite o toISOString() já devolvia o dia seguinte — então o seletor
    // liberava amanhã e o servidor recusava na hora de salvar, com o usuário
    // vendo "A data não pode estar no futuro" para a data que o próprio campo
    // tinha oferecido.
    hoje() {
      const agora = new Date();
      const mes = String(agora.getMonth() + 1).padStart(2, '0');
      const dia = String(agora.getDate()).padStart(2, '0');
      return `${agora.getFullYear()}-${mes}-${dia}`;
    },
    temFiltro() {
      return Object.values(this.filtros).some(v => v !== '');
    },
  },
  watch: {
    propriedadeSelecionada(nova, antiga) {
      // Trocar de propriedade invalida a gleba escolhida, que pertence a outra.
      if (antiga !== '' && nova !== antiga) this.formData.gleba = '';
      this.fetchGlebasDaPropriedade();
    },
    // Um watcher só para o objeto inteiro: qualquer filtro que mude recarrega
    // a listagem a partir da primeira página. Sem voltar para a página 1, um
    // filtro aplicado na página 5 mostraria "nenhum resultado" só porque o
    // recorte novo tem menos páginas que isso.
    filtros: {
      deep: true,
      handler() {
        this.pagina = 1;
        this.fetchAnaliseSolo();
      },
    },
    'filtros.propriedade'(nova, antiga) {
      if (antiga !== '' && nova !== antiga) this.filtros.gleba = '';
      this.fetchGlebasDoFiltro();
    },
  },
  methods: {
    // Um índice pode vir nulo quando a análise não tem dados suficientes —
    // CTC igual a zero, por exemplo, impede calcular o V%. Exibe travessão
    // em vez de deixar "null" aparecer na tela.
    formatar(valor) {
      return valor === null || valor === undefined ? '—' : valor;
    },
    // A API devolve o valor cru do campo ('calcitico'); aqui vira texto.
    rotuloCalcario(tipo) {
      return {
        calcitico: 'Calcítico',
        magnesiano: 'Magnesiano',
        dolomitico: 'Dolomítico',
      }[tipo] || '—';
    },
    // Exigido pelo mixin listaPaginada: como recarregar após trocar de página.
    recarregar() {
      this.fetchAnaliseSolo();
    },
    viewDetails(analisesolo) {
      this.selectedSolo = analisesolo; 
      this.showDetail = true; // Exibe os detalhes
    },
    limparFiltros() {
      this.filtros = {
        propriedade: '', gleba: '', cultura: '', data_apos: '', data_antes: '',
      };
    },
    // Alterna a exibição do formulário e reseta os dados
    toggleForm() {
      this.showForm = !this.showForm;
      // Havia aqui um 'this.vermaiscampos = !this.vermaiscampos'. A propriedade
      // não existia no data(), e o bloco .extra-fields do template lia
      // 'analisesolo.vermaiscampos' — campo que a API nunca devolveu. O bloco
      // nunca renderizou; os dois foram removidos.
      this.editingSolo = false;
      this.propriedadeSelecionada = '';
      this.formData = {
        laboratorio: '',
        cultura: '',
        camada: '0-20',
        data: '',
        gleba: '',
        area: '',
        laudo: '',
        ph_h2o: '',
        s: '',
        p: '',
        k: '',
        ca: '',
        mg: '',
        na: '',
        al: '',
        h: '',
        materia_organica: '',
        areia: '',
        silte: '',
        argila: '',
        mn: '',
        fe: '',
        cu: '',
        zn: '',
        b: '',
      };
    },
    // Os três 'getXNome' que existiam aqui foram removidos: a API agora
    // devolve laboratorio_nome, cultura_nome e propriedade_nome prontos.
    // Busca os dados dos laboratórios
    async fetchLaboratorios() {
      try {
        const response = await api.get('/laboratorios/' + PARAMS_LISTA_COMPLETA);
        this.laboratorios = extrairLista(response)
      } catch (error) {
        console.error('Erro ao buscar laboratórios:', error);
      }
    },
    // Busca os dados das propriedades
    async fetchPropriedades() {
      try {
        const response = await api.get('/propriedades/' + PARAMS_LISTA_COMPLETA);
        this.propriedades = extrairLista(response)
      } catch (error) {
        console.error('Erro ao buscar propriedades:', error);
      }
    },
    // Busca as glebas de UMA propriedade, no servidor.
    //
    // Antes esta tela carregava TODAS as glebas do usuário (page_size=200) e
    // filtrava por propriedade em JavaScript. Passando de 200 glebas, a lista
    // vinha truncada sem nenhum aviso — e uma lista suspensa incompleta é o
    // pior modo de falha possível: o usuário não vê o que falta, então não
    // tem como desconfiar. A API já entende '?propriedade=', que é o que a
    // tela de Recomendações sempre usou.
    async buscarGlebas(propriedadeId) {
      if (!propriedadeId) return [];
      try {
        const response = await api.get(
          `/glebas/?propriedade=${propriedadeId}&page_size=${TAMANHO_LISTA_COMPLETA}`
        );
        return extrairLista(response);
      } catch (error) {
        console.error('Erro ao buscar glebas:', error);
        return [];
      }
    },
    async fetchGlebasDaPropriedade() {
      this.glebasDaPropriedade = await this.buscarGlebas(this.propriedadeSelecionada);
    },
    async fetchGlebasDoFiltro() {
      this.glebasDoFiltro = await this.buscarGlebas(this.filtros.propriedade);
    },
    // Busca os dados das culturas
    async fetchCulturas() {
      try {
        const response = await api.get('/culturas/' + PARAMS_LISTA_COMPLETA);
        this.culturas = extrairLista(response)
      } catch (error) {
        console.error('Erro ao buscar culturas:', error);
      }
    },
    // Busca as análises de solo, aplicando os filtros no SERVIDOR.
    //
    // Os parâmetros vazios são descartados: '?cultura=' sem valor faria o
    // django-filter recusar a requisição inteira em vez de ignorar o campo.
    async fetchAnaliseSolo() {
      const params = new URLSearchParams({ page: this.pagina });
      Object.entries(this.filtros).forEach(([campo, valor]) => {
        if (valor !== '' && valor !== null) params.append(campo, valor);
      });
      try {
        const response = await api.get(`/analisesolo/?${params.toString()}`);
        this.analisesSolo = this.aplicarPaginacao(response);
      } catch (error) {
        console.error('Erro ao buscar análises de solo:', error);
        erro(mensagemDeErro(error, 'Não foi possível carregar as análises.'));
      }
    },
    // Envia os dados do formulário
    async submitForm() {
      try {
        if (this.editingSolo) {
          const response = await api.put(`/analisesolo/${this.formData.id}/`, this.formData);
          if (response.status === 200) {
            sucesso('Análise de solo atualizada com sucesso!');
            this.fetchAnaliseSolo();
            this.toggleForm();
          } else {
            erro('Erro ao atualizar análise de solo.');
          }
        } else {
          const response = await api.post('/analisesolo/', this.formData);
          if (response.status === 201) {
            sucesso('Análise de solo cadastrada com sucesso!');
            // Recarrega em vez de dar push na lista local: a listagem é
            // ordenada por -data e paginada, então inserir no fim da página
            // atual punha a análise nova fora de ordem e deixava o 'count' da
            // paginação defasado. As outras telas já recarregavam.
            this.pagina = 1;
            this.fetchAnaliseSolo();
            this.toggleForm();
          } else {
            erro('Erro ao cadastrar análise de solo. Tente novamente mais tarde.');
          }
        }
      } catch (error) {
        console.error('Erro ao enviar requisição:', error);
        erro(mensagemDeErro(error));
      }
    },
    // Inicia o modo de edição
    startEditing(analisesolo) {
      this.formData = { ...analisesolo };
      // A analise nao guarda mais a propriedade; ela vem por leitura junto
      // da resposta e serve para reabrir o select em cascata no ponto certo.
      // O watcher de 'propriedadeSelecionada' dispara a busca das glebas — mas
      // só se o valor mudar, então guardamos a gleba antes: o watcher limpa
      // formData.gleba, e sem isto o campo abriria vazio ao editar.
      const glebaOriginal = analisesolo.gleba;
      this.propriedadeSelecionada = analisesolo.propriedade || '';
      this.formData.gleba = glebaOriginal;
      this.fetchGlebasDaPropriedade();
      this.showForm = true;
      this.editingSolo = true;
    },
    // Deleta uma análise de solo
    async deleteSolo(analisesoloId) {
      if (!await confirmar('Tem certeza que deseja deletar esta análise de solo?')) return;
      try {
        const response = await api.delete(`/analisesolo/${analisesoloId}/`);
        if (response.status === 204) {
          sucesso('Análise de solo deletada com sucesso!');
          this.fetchAnaliseSolo();
        } else {
          erro('Erro ao deletar análise de solo.');
        }
      } catch (error) {
        console.error('Erro ao deletar análise de solo:', error);
        erro(mensagemDeErro(error));
      }
    },
  },
  mounted() {
    // Laboratórios e culturas continuam sendo carregados: são as opções dos
    // selects do formulário. O que saiu foi a busca de TODAS as glebas —
    // agora elas vêm por propriedade, sob demanda.
    this.fetchLaboratorios();
    this.fetchPropriedades();
    this.fetchCulturas();
    this.fetchAnaliseSolo();
  }
};
</script>


<!-------------------------------------------------------------------------------------------------------------------->


<style scoped>
/* Apenas o que é específico desta tela.
   O padrão comum vive em src/estilos/base.css. */

/* ------------------------------------------------------------- filtros */

.filtros {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 12px;
  padding: 12px 14px;
  margin-bottom: 14px;
  background-color: #fff;
  border: 1px solid var(--cor-borda-suave);
  border-radius: var(--raio-pequeno);
}

.filtro {
  display: flex;
  flex-direction: column;
  flex: 1 1 160px;
  min-width: 140px;
  text-align: left;
}

.filtro label {
  font-size: 0.78rem;
  color: var(--cor-texto-suave);
  margin-bottom: 3px;
}

.filtro select,
.filtro input {
  padding: 6px 8px;
  font-size: 0.9rem;
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio-pequeno);
  background-color: #fff;
  color: var(--cor-texto);
}

.filtro select:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}

.filtro-acao {
  flex: 0 0 auto;
  min-width: 0;
}

.filtro-acao .btn-back:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.resumo-filtro {
  margin: 0 0 10px;
  font-size: 0.85rem;
  color: var(--cor-texto-suave);
  text-align: left;
}

.link-limpar {
  background: none;
  border: none;
  padding: 0 0 0 4px;
  color: var(--cor-primaria);
  text-decoration: underline;
  cursor: pointer;
  font-size: inherit;
}

.table {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #ddd;
}

.diagnostico {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 16px 20px;
  margin: 16px 0 24px;
  text-align: left;
}

.diagnostico h3 {
  margin: 0 0 14px;
  font-size: 1.1rem;
  color: #212f3d;
}

.indices {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.indice {
  display: flex;
  flex-direction: column;
  padding: 8px 12px;
  background-color: #fff;
  border-radius: 4px;
  border-left: 3px solid #ccc;
}

.indice.destaque {
  border-left-color: #1f618d;
}

.indice .rotulo {
  font-size: 0.78rem;
  color: #666;
}

.indice .valor {
  font-size: 1.15rem;
  font-weight: 600;
  color: #212f3d;
}

.diagnostico .nota {
  margin: 12px 0 0;
  font-size: 0.8rem;
  color: #6c757d;
}

.calagem {
  background-color: #f4f8f4;
  border: 1px solid #cfe0cf;
  border-radius: 8px;
  padding: 16px 20px;
  margin: 0 0 24px;
  text-align: left;
}

.calagem h3 {
  margin: 0 0 14px;
  font-size: 1.1rem;
  color: #1e5631;
}

.calagem .indice.destaque {
  border-left-color: #1e8449;
}

.calagem .metodo {
  font-size: 0.95rem;
  font-weight: 500;
}

.aviso-camada {
  background-color: #fff3cd;
  color: #664d03;
  padding: 10px 12px;
  border-radius: 4px;
  font-size: 0.9rem;
}

.pendencias {
  margin: 12px 0 0;
  padding-left: 20px;
  font-size: 0.85rem;
  color: #8a6d3b;
}

.faixa {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: #566573;
}
</style>