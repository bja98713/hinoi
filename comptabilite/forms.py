from django import forms
from django.utils import timezone
from .models import Facturation, Paiement, Code
from .widgets import IntegerNumberInput, CodeSelectWidget
import json

class FacturationForm(forms.ModelForm):
    # Champs de paiement
    modalite_paiement = forms.ChoiceField(
        choices=Paiement.MODALITE_CHOICES,
        required=False,
        label="Modalité de paiement",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    banque = forms.ChoiceField(
        choices=Paiement.BANQUE_CHOICES,
        required=False,
        label="Banque",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    porteur = forms.CharField(
        required=False,
        label="Porteur",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Facturation
        fields = '__all__'
        widgets = {
            # Widget personnalisé pour gérer le tri et l'affichage dynamique
            'code_acte': CodeSelectWidget(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'placeholder': 'JJ/MM/AAAA', 'class': 'form-control', 'type': 'date'}
            ),
            'date_acte': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'placeholder': 'JJ/MM/AAAA', 'class': 'form-control', 'type': 'date'}
            ),
            'date_facture': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'placeholder': 'JJ/MM/AAAA', 'class': 'form-control', 'type': 'date'}
            ),
            'numero_facture': forms.TextInput(attrs={'class': 'form-control'}),
            'total_acte': IntegerNumberInput(attrs={'class': 'form-control'}),
            'tiers_payant': IntegerNumberInput(attrs={'class': 'form-control'}),
            'total_paye': IntegerNumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Tri ascendant des codes d'acte pour la liste déroulante
        qs_codes = Code.objects.order_by('code_acte')
        self.fields['code_acte'].queryset = qs_codes

        # Préparation des données dynamiques pour le JS et le widget sans requêtes supplémentaires
        codes_data = {}
        widget_metadata = {}
        for code in qs_codes:
            key = str(code.pk)

            total_acte = str(int(code.total_acte or 0))
            tiers_payant = str(int(code.tiers_payant or 0))
            total_paye = str(int(code.total_paye or 0))

            codes_data[key] = {
                'total_acte': total_acte,
                'total_acte_1': str(int(code.total_acte_1 or 0)),
                'total_acte_2': str(int(code.total_acte_2 or 0)),
                'tiers_payant': tiers_payant,
                'total_paye': total_paye,
                'code_acte_normal': code.code_acte_normal or "",
                'code_acte_normal_2': code.code_acte_normal_2 or "",
            }
            widget_metadata[key] = {
                'total_acte': total_acte,
                'tiers_payant': tiers_payant,
                'total_paye': total_paye,
            }

        # Injection via attribut du widget (data-codes) et cache local pour éviter les requêtes N+1
        widget = self.fields['code_acte'].widget
        widget.attrs.update({'data-codes': json.dumps(codes_data)})
        widget.code_metadata = widget_metadata

        # Initialisation des dates si création
        if not self.instance.pk:
            today = timezone.localdate()
            self.fields['date_acte'].initial = today
            self.fields['date_facture'].initial = today

        # Formats d'entrée pour les dates
        for fname in ('date_naissance', 'date_acte', 'date_facture'):
            self.fields[fname].input_formats = ['%Y-%m-%d', '%d/%m/%Y']

        # Champs facultatifs
        optional_fields = [
            'tiers_payant', 'total_paye', 'numero_facture',
            'code_acte', 'total_acte', 'lieu_acte', 'regime_tp'
        ]
        for fname in optional_fields:
            if fname in self.fields:
                self.fields[fname].required = False

        # Valeurs imposées par le métier : toujours sécurité sociale / droits ouverts / RAS
        if 'regime' in self.fields:
            self.fields['regime'].initial = 'Sécurité Sociale'
            self.fields['regime'].disabled = True
        if 'droit_ouvert' in self.fields:
            self.fields['droit_ouvert'].initial = True
            self.fields['droit_ouvert'].disabled = True
        if 'statut_dossier' in self.fields:
            self.fields['statut_dossier'].initial = 'ras'
            self.fields['statut_dossier'].disabled = True

        # Réordonnancement : modalite_paiement, banque, porteur après total_paye
        order = list(self.fields.keys())
        for key in ('modalite_paiement', 'banque', 'porteur'):
            if key in order:
                order.remove(key)
        if 'total_paye' in order:
            idx = order.index('total_paye')
            order[idx+1:idx+1] = ['modalite_paiement', 'banque', 'porteur']
        self.order_fields(order)

    def clean(self):
        cleaned = super().clean()
        # Champs imposés : même si désactivés, on force la valeur pour éviter toute incohérence.
        cleaned['regime'] = 'Sécurité Sociale'
        cleaned['droit_ouvert'] = True
        cleaned['statut_dossier'] = 'ras'
        # Validation pour paiements par chèque
        if cleaned.get('modalite_paiement') == 'Chèque':
            if not cleaned.get('banque'):
                self.add_error('banque', "Ce champ est requis pour les paiements par chèque.")
            if not cleaned.get('porteur'):
                self.add_error('porteur', "Ce champ est requis pour les paiements par chèque.")
        # Validation pour régime longue maladie
        if cleaned.get('regime_lm') and not cleaned.get('numero_facture'):
            self.add_error('numero_facture',
                "Le numéro de facture est requis pour un régime longue maladie."
            )
        return cleaned

    def save(self, commit=True):
        fact = super().save(commit=False)
        user_num = self.cleaned_data.get('numero_facture')
        code = fact.code_acte
        if user_num:
            fact.numero_facture = user_num
        elif code and not code.parcours_soin:
            now = timezone.localtime()
            fact.numero_facture = now.strftime("FQ/%Y/%m/%d/%H:%M")
        else:
            fact.numero_facture = ''
        if commit:
            fact.save()
        # Gestion du modèle Paiement
        modalite = self.cleaned_data.get('modalite_paiement')
        if modalite:
            paiement, _ = Paiement.objects.get_or_create(facture=fact)
            paiement.modalite_paiement = modalite
            if modalite == 'Chèque':
                paiement.banque = self.cleaned_data.get('banque', '')
                paiement.porteur = self.cleaned_data.get('porteur', '')
            else:
                paiement.banque = ''
                paiement.porteur = ''
            paiement.save()
        return fact
