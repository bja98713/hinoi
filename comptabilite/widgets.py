from django.forms.widgets import Select, NumberInput

class IntegerNumberInput(NumberInput):
    def format_value(self, value):
        if value is None or value == '':
            return ''
        try:
            # Convertir en float, arrondir et convertir en entier
            return str(int(round(float(value))))
        except (ValueError, TypeError):
            return super().format_value(value)

class CodeSelectWidget(Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        # On appelle d'abord la méthode parente pour créer l'option
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value:
            # Certaines instances de ModelChoiceIteratorValue disposent d'un attribut "value"
            pk = value.value if hasattr(value, 'value') else value
            # Importer le modèle Code ici pour éviter les problèmes d'import cyclique
            try:
                from .models import Code
                code_obj = Code.objects.get(pk=pk)
                # Mettre à jour les attributs data avec des montants formatés en entier (aucune décimale)
                option['attrs'].update({
                    'data-total_acte': str(int(round(code_obj.total_acte))),
                    'data-tiers_payant': str(int(round(code_obj.tiers_payant))),
                    'data-total_paye': str(int(round(code_obj.total_paye))),
                })
            except Code.DoesNotExist:
                pass
        return option
