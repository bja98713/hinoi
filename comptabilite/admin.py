from django.contrib import admin
from .models import Code, Medecin

@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    # On récupère tous les champs concrets et éditables sauf
    # ceux créés automatiquement (notamment 'id')
    fields = sorted(
        f.name for f in Code._meta.get_fields()
        if f.concrete and f.editable and not f.auto_created
    )

    list_display = fields
    ordering     = fields
    search_fields = ('code_acte', 'code_acte_normal', 'code_reel')


@admin.register(Medecin)
class MedecinAdmin(admin.ModelAdmin):
    # On peut aussi classer par ordre alphabétique
    fields = ['code_m', 'nom_clinique', 'nom_medecin']
    list_display = fields
    ordering     = fields
    search_fields = ('nom_medecin', 'code_m', 'nom_clinique')
