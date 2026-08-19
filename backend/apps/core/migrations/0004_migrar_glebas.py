from django.db import migrations


def texto_para_gleba(apps, schema_editor):
    """
    Etapa 2 de 3: transfere o texto livre para registros de Gleba.

    Para cada analise, cria (ou reaproveita) a gleba correspondente dentro da
    propriedade que a analise ja apontava. Como a gleba nasce da propriedade
    da propria analise, nenhum vinculo se perde quando a coluna 'propriedade'
    for removida na etapa 3.

    A correspondencia e feita por nome normalizado - espacos colapsados e
    comparacao sem diferenciar maiusculas. Variantes como "Talhao 3" e
    "talhao 3" sao unificadas; abreviacoes como "T3" NAO sao, porque adivinhar
    que se referem ao mesmo pedaco de terra seria um palpite sobre os dados de
    quem usa o sistema. Essas ficam como glebas separadas, para conferencia
    manual.
    """
    AnaliseSolo = apps.get_model('core', 'AnaliseSolo')
    Gleba = apps.get_model('core', 'Gleba')

    cache = {}
    for analise in AnaliseSolo.objects.all().iterator():
        bruto = (analise.gleba or '').strip()
        nome = ' '.join(bruto.split()) if bruto else 'Sem gleba'
        chave = (analise.propriedade_id, nome.casefold())

        gleba_id = cache.get(chave)
        if gleba_id is None:
            existente = Gleba.objects.filter(
                propriedade_id=analise.propriedade_id, nome__iexact=nome
            ).first()
            if existente is None:
                existente = Gleba.objects.create(
                    propriedade_id=analise.propriedade_id, nome=nome
                )
            gleba_id = existente.pk
            cache[chave] = gleba_id

        analise.gleba_ref_id = gleba_id
        analise.save(update_fields=['gleba_ref'])


def gleba_para_texto(apps, schema_editor):
    """Volta o nome da gleba para a coluna de texto, se a migracao for revertida."""
    AnaliseSolo = apps.get_model('core', 'AnaliseSolo')
    for analise in AnaliseSolo.objects.select_related('gleba_ref').iterator():
        if analise.gleba_ref_id:
            analise.gleba = analise.gleba_ref.nome
            analise.propriedade_id = analise.gleba_ref.propriedade_id
            analise.save(update_fields=['gleba', 'propriedade'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_gleba'),
    ]

    operations = [
        migrations.RunPython(texto_para_gleba, gleba_para_texto),
    ]
