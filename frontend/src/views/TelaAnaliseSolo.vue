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
            <label for="laboratorio" class="form-label">laboratorio</label>
            <select id="laboratorio" v-model="formData.laboratorio" class="form-control" required>
              <option disabled value="">Selecione um laboratorio</option>
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
            <label for="cultura" class="form-label">cultura</label>
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
            <label for="area" class="form-label">Area</label>
            <input type="number" step="0.1" id="area" v-model="formData.area" placeholder="Ex: 10.50" required min="0" />
          </div>
          <div class="mb-3">
            <label for="laudo" class="form-label">laudo</label>
            <input type="text" id="laudo" v-model="formData.laudo" placeholder="Insira o laudo" required />
          </div>
          <!-- Campo para o ph_h2o -->
          <div class="mb-3">
            <label for="ph_h2o" class="form-label">pH em H2O</label>
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
            <label for="h" class="form-label">Hidrogenio (H)</label>
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
        <div v-if="analisesSolo.length">
          <!-- Cabeçalho da tabela de analises -->
          <div class="row lista-cabecalho mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">laboratorio</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">propriedade</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">cultura</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">data</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">gleba</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">area</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">laudo</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">ação</div>
          </div>
          <!-- Loop para exibir cada analise de solo na tabela -->
          <div v-for="analisesolo in analisesSolo" :key="analisesolo.id" class="row lista-linha mb-2">
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ getlaboratorioNome(analisesolo.laboratorio) }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ analisesolo.propriedade_nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ getculturaNome(analisesolo.cultura) }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ analisesolo.data }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ analisesolo.gleba_nome }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ analisesolo.area }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">{{ analisesolo.laudo }}</div>
            <div class="col-12 col-sm-6 col-md-4 col-lg-2">
              <!-- Lista de Análises de Solo, oculta quando o formulário está ativo -->
              <button @click="startEditing(analisesolo)" class="btn-edit">🖊️</button>
              <button @click="deleteSolo(analisesolo.id)" class="btn-delete">🗑️</button>
              <button @click="viewDetails(analisesolo)" class="btn-detalhe" title="Ver detalhes">🔎</button>
            </div>
            <!-- Exibe campos adicionais se 'vermaiscampos' da análise estiver ativado -->
            <div v-if="analisesolo.vermaiscampos" class="extra-fields">
              <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ analisesolo.ph_h2o }}</div>
              <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ analisesolo.s }}</div>
              <div class="col-12 col-sm-6 col-md-4 col-lg-1">{{ analisesolo.p }}</div>
              <!-- Continue com os outros campos... -->
            </div>
          </div>
        </div>
        <div v-else>
          <p>Nenhuma análise de solo encontrada.</p>
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
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Ph em H20</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Enxofre (S)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Fosforo (P)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Potássio (K)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">calcio (ca)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Magnesio (mg)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Sodio (na)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Alumínio (al)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Hidrogenio (h)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Materia Organica</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Areia</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Silte</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Argila</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Meganes (mn)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Ferro (fr)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Cobre (cu)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Zinco (zn)</th>
        <th scope="col-12 col-sm-6 col-md-4 col-lg-2">Boro (b)</th>
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
import { extrairLista, PARAMS_LISTA_COMPLETA } from '@/lista';

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
      glebas: [],
      culturas: [],
      // Nao faz parte do formulario enviado: serve so para filtrar as glebas.
      propriedadeSelecionada: '',
      showForm: false,
      showDetail: false, 
      editingSolo: false,
      selectedSolo: null,
    };
  },
  computed: {
    // Trava o seletor de data em hoje: o backend recusa data futura,
    // e assim o usuario nem consegue escolher uma.
    hoje() {
      return new Date().toISOString().split('T')[0];
    },
    glebasDaPropriedade() {
      if (!this.propriedadeSelecionada) return [];
      return this.glebas.filter(g => g.propriedade === Number(this.propriedadeSelecionada));
    },
  },
  watch: {
    propriedadeSelecionada(nova, antiga) {
      // Trocar de propriedade invalida a gleba escolhida, que pertence a outra.
      if (antiga !== '' && nova !== antiga) this.formData.gleba = '';
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
    // Alterna a exibição do formulário e reseta os dados
    toggleForm() {
      this.showForm = !this.showForm;
      this.vermaiscampos = !this.vermaiscampos;
      this.editingSolo = false;
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
    // Obtém o nome do laboratório a partir do ID
    getlaboratorioNome(laboratorioId) {
      const laboratorio = this.laboratorios.find(u => u.id === laboratorioId);
      return laboratorio ? laboratorio.nome : 'Desconhecido';
    },
    // Obtém o nome da propriedade a partir do ID
    getpropriedadeNome(propriedadeId) {
      const propriedade = this.propriedades.find(u => u.id === propriedadeId);
      return propriedade ? propriedade.nome : 'Desconhecido';
    },
    // Obtém o nome da cultura a partir do ID
    getculturaNome(culturaId) {
      const cultura = this.culturas.find(u => u.id === culturaId);
      return cultura ? cultura.nome : 'Desconhecido';
    },
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
    // Busca as glebas de todas as propriedades do usuario
    async fetchGlebas() {
      try {
        const response = await api.get('/glebas/' + PARAMS_LISTA_COMPLETA);
        this.glebas = extrairLista(response)
      } catch (error) {
        console.error('Erro ao buscar glebas:', error);
      }
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
    // Busca as análises de solo
    async fetchAnaliseSolo() {
      try {
        const response = await api.get(`/analisesolo/?page=${this.pagina}`);
                this.analisesSolo = this.aplicarPaginacao(response)
      } catch (error) {
        console.error('Erro ao buscar análises de solo:', error);
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
            this.analisesSolo.push(response.data);
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
      this.propriedadeSelecionada = analisesolo.propriedade || '';
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
    this.fetchLaboratorios();
    this.fetchPropriedades();
    this.fetchGlebas();
    this.fetchCulturas();
    this.fetchAnaliseSolo();
  }
};
</script>


<!-------------------------------------------------------------------------------------------------------------------->


<style scoped>
/* Apenas o que é específico desta tela.
   O padrão comum vive em src/estilos/base.css. */
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