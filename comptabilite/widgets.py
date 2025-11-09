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

# comptabilite/widgets.py

from django import forms
from django.forms.models import ModelChoiceIteratorValue

class CodeSelectWidget(forms.Select):
    """
    Un Select qui ajoute en data-attributes les montants liés au code d'acte
    pour pouvoir préremplir total_acte, tiers_payant et total_paye côté JS.
    Cette version gère la ModelChoiceIteratorValue pour en extraire la vraie PK.
    """
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected,
            index, subindex=subindex, attrs=attrs
        )

        # On récupère la vraie PK : si 'value' est un ModelChoiceIteratorValue, on prend value.value
        if isinstance(value, ModelChoiceIteratorValue):
            raw_pk = value.value
        else:
            raw_pk = value

        if not raw_pk:
            # pas de code sélectionné
            return option

        # Les métadonnées sont injectées par le formulaire pour éviter une requête par option.
        metadata = getattr(self, 'code_metadata', {})
        code_data = metadata.get(str(raw_pk))
        if not code_data:
            return option

        option['attrs'].update({
            'data-total_acte':   code_data.get('total_acte', '0'),
            'data-tiers_payant': code_data.get('tiers_payant', '0'),
            'data-total_paye':   code_data.get('total_paye', '0'),
        })
        return option


