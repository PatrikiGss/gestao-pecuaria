from django.db import migrations, models
from django.db.models.functions import Lower
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Etapa 1 de 3 da promocao de 'gleba' a entidade.

    Cria o modelo Gleba e acrescenta uma chave estrangeira temporaria e
    opcional na AnaliseSolo. Os campos antigos continuam intactos aqui: a
    remocao so acontece na etapa 3, depois que a 0004 tiver transferido os
    dados. Dividir em tres migracoes e o que evita perder o conteudo da
    coluna de texto.
    """

    dependencies = [
        ('core', '0002_alter_analisesolo_al_alter_analisesolo_areia_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gleba',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                )),
                ('nome', models.CharField(max_length=255)),
                ('propriedade', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='glebas',
                    to='core.propriedade',
                )),
            ],
            options={
                'verbose_name': 'Gleba',
                'verbose_name_plural': 'Glebas',
                'ordering': ['nome'],
            },
        ),
        migrations.AddConstraint(
            model_name='gleba',
            constraint=models.UniqueConstraint(
                Lower('nome'), 'propriedade', name='gleba_unica_por_propriedade'
            ),
        ),
        migrations.AddField(
            model_name='analisesolo',
            name='gleba_ref',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='analises',
                to='core.gleba',
            ),
        ),
    ]
