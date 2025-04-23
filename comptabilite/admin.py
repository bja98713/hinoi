from django.contrib import admin
from .models import Code, Medecin

@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    list_display = (
        'code_acte',
        'total_acte',
        'tiers_payant',
        'total_paye',
        'medecin',
        'parcours_soin',
        'longue_maladie',
        'code_reel',
        'variable_1',
        'code_acte_normal',
        'variable_2',
        'modificateur'
    )
    search_fields = ('code_acte', 'code_acte_normal', 'code_reel')

@admin.register(Medecin)
class MedecinAdmin(admin.ModelAdmin):
    list_display = ('nom_medecin', 'code_m', 'nom_clinique')
    search_fields = ('nom_medecin', 'code_m', 'nom_clinique')
