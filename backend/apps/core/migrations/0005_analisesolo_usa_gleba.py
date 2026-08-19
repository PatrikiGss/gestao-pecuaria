from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Etapa 3 de 3: descarta os campos antigos e promove a chave estrangeira.

    A coluna de texto 'gleba' sai, e 'propriedade' tambem: a propriedade da
    analise passa a ser obtida por gleba.propriedade. Manter as duas
    permitiria que se contradissessem.

    Roda depois da 0004, que ja preencheu 'gleba_ref' em todas as linhas -
    por isso o campo pode ficar obrigatorio aqui.
    """

    dependencies = [
        ('core', '0004_migrar_glebas'),
    ]

    operations = [
        migrations.RemoveField(model_name='analisesolo', name='gleba'),
        migrations.RemoveField(model_name='analisesolo', name='propriedade'),
        migrations.RenameField(
            model_name='analisesolo', old_name='gleba_ref', new_name='gleba'
        ),
        migrations.AlterField(
            model_name='analisesolo',
            name='gleba',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='analises',
                to='core.gleba',
            ),
        ),
    ]
