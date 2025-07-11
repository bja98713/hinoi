# Generated by Django 5.2 on 2025-04-24 01:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comptabilite', '0008_alter_facturation_numero_facture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facturation',
            name='code_acte',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='facturations', to='comptabilite.code', verbose_name="Code de l'acte"),
        ),
    ]
