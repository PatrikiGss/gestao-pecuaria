"""
Popula a conta de um usuario com dados realistas para conferencia manual.

    python manage.py dados_exemplo --email patriki7771@gmail.com
    python manage.py dados_exemplo --email ... --limpar   (remove o que criou)

Os registros criados levam um marcador no nome (ver MARCADOR) para que a
limpeza remova exatamente o que este comando gerou, sem tocar no que voce
cadastrou a mao.

As analises cobrem situacoes de solo diferentes de proposito - muito acido,
acido, medio, bom e ja corrigido - para dar de ver o diagnostico e a calagem
variando. Uma das glebas tem serie historica de varios anos, que e o caso de
uso que motivou transformar a gleba em entidade.
"""
from datetime import date, timedelta
from decimal import Decimal as D

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from autenticacao.models import Usuario
from core.agronomia import recomendacao_completa
from core.models import (
    Produtor, Propriedade, Gleba, Laboratorio, Cultura, Calcario, AnaliseSolo, Recomendacao,
)
from core.serializers import calcario_para

MARCADOR = '[exemplo]'


def cpf_valido(base9):
    """Completa um CPF de 9 digitos com os dois verificadores corretos."""
    digitos = [int(c) for c in base9]
    for peso_inicial in (10, 11):
        soma = sum(d * (peso_inicial - i) for i, d in enumerate(digitos))
        dv = (soma * 10) % 11
        digitos.append(0 if dv == 10 else dv)
    return ''.join(map(str, digitos))


# Perfis de solo. Bases em cmolc/dm3, P e micros em mg/dm3.
PERFIS = {
    'muito acido': dict(ph_h2o='4.5', ca='0.80', mg='0.30', k='0.08', na='0.02',
                        al='1.20', h='5.50', p='4', s='6', materia_organica='18'),
    'acido':       dict(ph_h2o='5.0', ca='1.80', mg='0.70', k='0.12', na='0.03',
                        al='0.60', h='4.20', p='8', s='9', materia_organica='22'),
    'medio':       dict(ph_h2o='5.5', ca='3.00', mg='1.50', k='0.20', na='0.05',
                        al='0.20', h='3.05', p='12', s='12', materia_organica='25'),
    'bom':         dict(ph_h2o='6.2', ca='4.50', mg='2.00', k='0.35', na='0.05',
                        al='0.00', h='1.80', p='25', s='16', materia_organica='32'),
    'corrigido':   dict(ph_h2o='6.8', ca='6.00', mg='2.20', k='0.42', na='0.06',
                        al='0.00', h='1.20', p='38', s='20', materia_organica='35'),
    # Os dois perfis abaixo tem magnesio baixo em relacao ao calcio. Sao eles
    # que fazem o sistema indicar calcario magnesiano e dolomitico - sem isso
    # todas as analises cairiam em calcitico e os outros dois tipos nunca
    # apareceriam na conferencia.
    'mg baixo':    dict(ph_h2o='5.3', ca='3.50', mg='1.00', k='0.18', na='0.04',
                        al='0.40', h='3.60', p='10', s='11', materia_organica='24'),
    'mg escasso':  dict(ph_h2o='5.1', ca='4.00', mg='0.45', k='0.15', na='0.03',
                        al='0.50', h='4.00', p='9', s='10', materia_organica='21'),
}

TEXTURAS = {
    'arenosa':        ('80', '10', '10'),
    'media':          ('45', '30', '25'),
    'argilosa':       ('25', '25', '50'),
    'muito argilosa': ('15', '15', '70'),
}

MICROS = dict(mn='1.80', fe='45.00', cu='1.20', zn='2.40', b='0.35')


class Command(BaseCommand):
    help = 'Cria dados de exemplo na conta informada.'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='E-mail da conta que recebera os dados')
        parser.add_argument('--limpar', action='store_true',
                            help='Remove os dados de exemplo em vez de criar')

    def handle(self, *args, **opcoes):
        try:
            usuario = Usuario.objects.get(email=opcoes['email'])
        except Usuario.DoesNotExist:
            raise CommandError(f"Nenhuma conta com o e-mail {opcoes['email']}.")

        if opcoes['limpar']:
            self.limpar(usuario)
        else:
            self.criar(usuario)

    # ------------------------------------------------------------------ limpar
    def limpar(self, usuario):
        with transaction.atomic():
            analises = AnaliseSolo.objects.filter(
                gleba__propriedade__produtor__usuario=usuario,
                gleba__propriedade__produtor__nome__contains=MARCADOR,
            )
            Recomendacao.objects.filter(analise_solo__in=analises).delete()
            n_analises = analises.count()
            analises.delete()

            # AnaliseSolo protege a Gleba, entao as glebas so saem depois.
            n_glebas = Gleba.objects.filter(
                propriedade__produtor__usuario=usuario,
                propriedade__produtor__nome__contains=MARCADOR).delete()[0]
            n_prop = Propriedade.objects.filter(
                produtor__usuario=usuario, produtor__nome__contains=MARCADOR).delete()[0]
            n_prod = Produtor.objects.filter(
                usuario=usuario, nome__contains=MARCADOR).delete()[0]
            n_lab = Laboratorio.objects.filter(
                usuario=usuario, nome__contains=MARCADOR).delete()[0]
            n_cul = Cultura.objects.filter(
                usuario=usuario, nome__contains=MARCADOR).delete()[0]
            n_cal = Calcario.objects.filter(
                usuario=usuario, nome__contains=MARCADOR).delete()[0]

        self.stdout.write(self.style.SUCCESS(
            f'Removidos: {n_analises} analises, {n_glebas} glebas, {n_prop} propriedades, '
            f'{n_prod} produtores, {n_lab} laboratorios, {n_cul} culturas, {n_cal} calcarios.'
        ))

    def _cultura(self, usuario, nome, v2, sat_k, p, fator_p, n, s):
        """
        Cria a cultura ja com os parametros de adubacao.

        Sao ordens de grandeza comumente citadas, para o sistema poder ser
        conferido de ponta a ponta. Nao substituem a fonte de referencia que
        o projeto vier a adotar.
        """
        return Cultura.objects.create(
            usuario=usuario, nome=f'{nome} {MARCADOR}',
            saturacao_bases_desejada=D(v2), saturacao_k_desejada=D(sat_k),
            fosforo_desejado=D(p), fator_fixacao_fosforo=D(fator_p),
            nitrogenio_recomendado=D(n), enxofre_desejado=D(s))

    # ------------------------------------------------------------------- criar
    @transaction.atomic
    def criar(self, usuario):
        if Produtor.objects.filter(usuario=usuario, nome__contains=MARCADOR).exists():
            raise CommandError(
                'Ja existem dados de exemplo nesta conta. '
                'Rode com --limpar antes de criar de novo.'
            )

        # -------------------------------------------------------- laboratorios
        labs = [
            Laboratorio.objects.create(
                usuario=usuario, nome=f'Laboratório Solo Central {MARCADOR}',
                endereco='Av. Anhanguera, 1200', cidade='Goiânia', estado='GO',
                telefone='6232551100', email='central@labexemplo.local'),
            Laboratorio.objects.create(
                usuario=usuario, nome=f'AgroLab Análises {MARCADOR}',
                endereco='Rua das Palmeiras, 45', cidade='Rio Verde', estado='GO',
                telefone='6436218890', email='contato@agrolabexemplo.local'),
        ]

        # ------------------------------------------------------------ culturas
        # V2 sao valores de partida, comumente citados. Confira na fonte que
        # voce adotar antes de usar para valer.
        culturas = [
            self._cultura(usuario, 'Soja', v2='70', sat_k='4', p='20', fator_p='5', n='30', s='12'),
            self._cultura(usuario, 'Milho', v2='70', sat_k='4', p='20', fator_p='5', n='120', s='15'),
            self._cultura(usuario, 'Feijão', v2='60', sat_k='3', p='18', fator_p='4.5', n='60', s='10'),
            self._cultura(usuario, 'Café', v2='60', sat_k='5', p='25', fator_p='6', n='200', s='20'),
            self._cultura(usuario, 'Cana-de-açúcar', v2='60', sat_k='4', p='22', fator_p='5.5', n='90', s='18'),
            # Sem V2: serve para ver o sistema cair no metodo do aluminio.
            Cultura.objects.create(usuario=usuario, nome=f'Pastagem {MARCADOR}'),
        ]

        # ------------------------------------------------------------ calcarios
        Calcario.objects.create(usuario=usuario, nome=f'Calcítico Fornecedor A {MARCADOR}',
                                tipo='calcitico', prnt=D('85'), teor_cao=D('42'), teor_mgo=D('3'))
        Calcario.objects.create(usuario=usuario, nome=f'Magnesiano Fornecedor B {MARCADOR}',
                                tipo='magnesiano', prnt=D('78'), teor_cao=D('36'), teor_mgo=D('9'))
        Calcario.objects.create(usuario=usuario, nome=f'Dolomítico Fornecedor C {MARCADOR}',
                                tipo='dolomitico', prnt=D('92'), teor_cao=D('30'), teor_mgo=D('18'))

        # ----------------------------------------------------------- produtores
        dados_produtores = [
            ('João Batista Ferreira', '529982247', 'joao.ferreira', '6299881122'),
            ('Maria Aparecida Lima', '111444777', 'maria.lima', '6299773344'),
            ('Cooperativa Vale Verde', '390533447', 'contato.valeverde', '6432115566'),
        ]
        produtores = []
        for nome, base, email, tel in dados_produtores:
            produtores.append(Produtor.objects.create(
                usuario=usuario, nome=f'{nome} {MARCADOR}', cpf=cpf_valido(base),
                telefone=tel, email=f'{email}@exemplo.local'))

        # --------------------------------------------------------- propriedades
        dados_prop = [
            (0, 'Fazenda Boa Vista', '-16.686900', '-49.264800', 'Rod. GO-020, km 32', 'Goiânia', 'GO'),
            (0, 'Sítio Recanto',     '-16.320000', '-48.953000', 'Estrada Municipal, s/n', 'Anápolis', 'GO'),
            (1, 'Fazenda Santa Rita','-17.797000', '-50.919000', 'Rod. BR-060, km 405', 'Rio Verde', 'GO'),
            (2, 'Gleba Cooperativa', '-18.157000', '-47.939000', 'Zona Rural', 'Catalão', 'GO'),
        ]
        propriedades = []
        for idx, nome, lat, lon, end, cid, uf in dados_prop:
            propriedades.append(Propriedade.objects.create(
                produtor=produtores[idx], nome=f'{nome} {MARCADOR}',
                latitude=D(lat), longitude=D(lon), endereco=end, cidade=cid, estado=uf))

        # ---------------------------------------------------------------- glebas
        nomes_glebas = [
            (0, 'Talhão 1'), (0, 'Talhão 2'), (0, 'Talhão 3'),
            (1, 'Baixada'), (1, 'Morro Alto'),
            (2, 'Pivô Central'), (2, 'Sequeiro Norte'),
            (3, 'Área Experimental'),
        ]
        glebas = [Gleba.objects.create(propriedade=propriedades[i], nome=n)
                  for i, n in nomes_glebas]

        # -------------------------------------------------------------- analises
        hoje = date.today()
        # (gleba, cultura, perfil, textura, dias atras, area)
        receita = [
            # Talhao 1: serie historica de 4 anos, solo melhorando com o manejo.
            (0, 0, 'muito acido', 'argilosa', 4 * 365, 78.5),
            (0, 0, 'acido',       'argilosa', 3 * 365, 78.5),
            (0, 0, 'medio',       'argilosa', 2 * 365, 78.5),
            (0, 0, 'bom',         'argilosa', 365,     78.5),
            (0, 1, 'bom',         'argilosa', 30,      78.5),
            # Talhao 2
            (1, 0, 'medio',   'media', 400, 45.0),
            (1, 1, 'medio',   'media', 60,  45.0),
            (1, 2, 'mg baixo', 'media', 200, 45.0),
            # Talhao 3
            (2, 0, 'acido',       'arenosa', 300, 32.0),
            (2, 5, 'muito acido', 'arenosa', 120, 32.0),  # pastagem: sem V2
            (2, 1, 'medio',       'arenosa', 20,  32.0),
            # Baixada
            (3, 2, 'bom',       'muito argilosa', 250, 21.3),
            (3, 3, 'corrigido', 'muito argilosa', 80,  21.3),
            # Morro Alto
            (4, 3, 'acido',       'argilosa', 500, 15.7),
            (4, 3, 'mg escasso', 'argilosa', 150, 15.7),
            (4, 5, 'muito acido', 'argilosa', 45,  15.7),
            # Pivo Central
            (5, 0, 'bom',       'media', 380, 120.0),
            (5, 1, 'mg baixo', 'media', 190, 120.0),
            (5, 4, 'corrigido', 'media', 55,  120.0),
            # Sequeiro Norte
            (6, 0, 'acido',       'arenosa', 420, 64.8),
            (6, 5, 'muito acido', 'arenosa', 210, 64.8),
            (6, 2, 'mg escasso', 'arenosa', 35,  64.8),
            # Area Experimental: varias culturas, para comparar V2 diferentes
            (7, 0, 'medio', 'media', 340, 9.5),
            (7, 1, 'medio', 'media', 300, 9.5),
            (7, 2, 'medio', 'media', 260, 9.5),
            (7, 3, 'medio', 'media', 220, 9.5),
            (7, 4, 'mg escasso', 'media', 180, 9.5),
            (7, 5, 'medio', 'media', 140, 9.5),
            (7, 0, 'bom',   'media', 100, 9.5),
            (7, 1, 'mg baixo', 'media', 60,  9.5),
            (7, 2, 'bom',   'media', 25,  9.5),
            (7, 3, 'bom',   'media', 10,  9.5),
        ]

        analises = []
        for i, (ig, ic, perfil, textura, atras, area) in enumerate(receita, start=1):
            areia, silte, argila = TEXTURAS[textura]
            campos = {k: D(v) for k, v in PERFIS[perfil].items()}
            campos.update({k: D(v) for k, v in MICROS.items()})
            analises.append(AnaliseSolo.objects.create(
                laboratorio=labs[i % len(labs)],
                gleba=glebas[ig],
                cultura=culturas[ic],
                data=hoje - timedelta(days=atras),
                camada='0-20',
                area=D(str(area)),
                laudo=f'LAUDO-{(hoje - timedelta(days=atras)).year}-{i:03d}',
                areia=D(areia), silte=D(silte), argila=D(argila),
                **campos))

        # Uma analise de subsuperficie, para ver o aviso de camada.
        areia, silte, argila = TEXTURAS['argilosa']
        campos = {k: D(v) for k, v in PERFIS['acido'].items()}
        campos.update({k: D(v) for k, v in MICROS.items()})
        analises.append(AnaliseSolo.objects.create(
            laboratorio=labs[0], gleba=glebas[0], cultura=culturas[0],
            data=hoje - timedelta(days=365), camada='20-40', area=D('78.5'),
            laudo='LAUDO-SUBSUPERFICIE-001',
            areia=D(areia), silte=D(silte), argila=D(argila), **campos))

        # --------------------------------------------------------- recomendacoes
        # Calculadas, nao inventadas: as doses saem de agronomia.py a partir
        # do laudo e dos parametros da cultura. Escrever numeros fixos aqui
        # daria a impressao de resultado onde nao houve conta.
        for analise in analises[:6]:
            calculado = recomendacao_completa(analise, calcario=calcario_para(analise))
            Recomendacao.objects.create(
                analise_solo=analise,
                camada_correcao=calculado['camada_correcao'],
                calcario_calcitico=calculado['calcario_calcitico'] or 0,
                calcario_dolomitico=calculado['calcario_dolomitico'] or 0,
                calcario_magnesiano=calculado['calcario_magnesiano'] or 0,
                gesso=calculado['gesso'] or 0,
                kcl=calculado['kcl'] or 0,
                p2o5=calculado['p2o5'] or 0,
                n=calculado['n'] or 0,
                s=calculado['s'] or 0)

        self.stdout.write(self.style.SUCCESS('Dados de exemplo criados:'))
        for rotulo, quantidade in [
            ('produtores', len(produtores)), ('propriedades', len(propriedades)),
            ('glebas', len(glebas)), ('laboratórios', len(labs)),
            ('culturas', len(culturas)), ('calcários', 3),
            ('análises de solo', len(analises)), ('recomendações', 6),
        ]:
            self.stdout.write(f'  {quantidade:>3}  {rotulo}')
        self.stdout.write('')
        self.stdout.write('Para remover tudo isso depois:')
        self.stdout.write(f'  python manage.py dados_exemplo --email {usuario.email} --limpar')
