from django.db import migrations
from django.db.models import F


def trocar_p_e_k(apps, schema_editor):
    """
    Corrige a inversao entre fosforo e potassio nas analises ja gravadas.

    O formulario da tela de analise tinha os dois rotulos trocados entre si:
    o campo rotulado "Potassio (K)" gravava na coluna 'p', e o rotulado
    "Fosforo (P)" gravava na coluna 'k'. Os valores de exemplo confirmavam a
    inversao, nao a desmentiam - 0,05 e ordem de grandeza de potassio em
    cmolc/dm3, e 5,0 de fosforo em mg/dm3.

    Como quem preenche le o rotulo, e nao o nome da coluna, os dados existentes
    estao invertidos: a coluna 'p' guarda potassio e a coluna 'k' guarda
    fosforo. Esta migracao devolve cada valor a sua coluna.

    O defeito passou despercebido porque nada lia esses numeros: eram apenas
    armazenados e reexibidos com o mesmo rotulo trocado, o que fechava o ciclo
    sem contradicao aparente. So apareceu ao preparar o calculo agronomico,
    onde 'SB = Ca + Mg + K + Na' somaria fosforo.
    """
    AnaliseSolo = apps.get_model('core', 'AnaliseSolo')
    # F() faz a troca em uma unica instrucao no banco, sem carregar as linhas
    # e sem precisar de coluna temporaria.
    AnaliseSolo.objects.update(p=F('k'), k=F('p'))


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_analisesolo_al_alter_analisesolo_area_and_more'),
    ]

    # A troca e a propria inversa: aplicar duas vezes volta ao estado original.
    operations = [
        migrations.RunPython(trocar_p_e_k, trocar_p_e_k),
    ]
