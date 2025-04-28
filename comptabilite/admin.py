from django.contrib import admin
from .models import Code, Medecin

@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    # Affichage en liste
    list_display = (
        'code_acte', 'total_acte', 'tiers_payant', 'total_paye',
        'medecin', 'parcours_soin', 'longue_maladie',
        'code_reel', 'variable_1', 'code_acte_normal',
        'variable_2', 'modificateur'
    )
    search_fields = ('code_acte', 'code_acte_normal', 'code_reel')

    # On récupère tous les champs non M2M ni O2M, triés alphabétiquement
    field_names = sorted(
        f.name for f in Code._meta.get_fields()
        if not (f.many_to_many or f.one_to_many)
    )

    fields = field_names
    list_display = field_names
    ordering = field_names


@admin.register(Medecin)
class MedecinAdmin(admin.ModelAdmin):
    list_display = ('nom_medecin', 'code_m', 'nom_clinique')
    search_fields = ('nom_medecin', 'code_m', 'nom_clinique')
