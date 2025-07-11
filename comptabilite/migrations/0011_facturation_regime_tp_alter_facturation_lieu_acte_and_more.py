# Generated by Django 5.2 on 2025-04-28 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comptabilite', '0010_alter_facturation_total_acte'),
    ]

    operations = [
        migrations.AddField(
            model_name='facturation',
            name='regime_tp',
            field=models.BooleanField(default=False, verbose_name='Tiers Payants : (oui/non)'),
        ),
        migrations.AlterField(
            model_name='facturation',
            name='lieu_acte',
            field=models.CharField(choices=[('Cabinet', 'Cabinet'), ('Clinique', 'Clinique')], max_length=50, verbose_name="Lieu de l'acte"),
        ),
        migrations.AlterField(
            model_name='facturation',
            name='regime',
            field=models.CharField(choices=[('Sécurité Sociale', 'Sécurité Sociale'), ('RNS', 'RNS'), ('Salarié', 'Salarié'), ('RST', 'RST')], max_length=20, verbose_name='Régime'),
        ),
        migrations.AlterField(
            model_name='facturation',
            name='statut_dossier',
            field=models.CharField(choices=[('RAS', 'RAS'), ('DNO', 'DNO'), ('DNOLM', 'DNOLM'), ('Impayé', 'Impayé'), ('Rejet', 'Rejet')], max_length=20, verbose_name='Statut du dossier'),
        ),
    ]
