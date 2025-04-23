from django import forms
from .models import Facturation, Paiement
from .widgets import IntegerNumberInput  # Importez le widget personnalisé
from .widgets import CodeSelectWidget  # Si vous utilisez déjà un widget personnalisé pour le code_acte

class FacturationForm(forms.ModelForm):
    # Champ pour le paiement (modalité, etc.)
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
            'code_acte': CodeSelectWidget(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(
                format='%Y-%m-%d',  # Format ISO pour HTML5 input type="date"
                attrs={
                    'placeholder': 'JJ/MM/AAAA',
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'date_acte': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'placeholder': 'JJ/MM/AAAA',
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'date_facture': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'placeholder': 'JJ/MM/AAAA',
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            # Utilisation de notre widget pour formater les montants sans décimales
            'total_acte': IntegerNumberInput(attrs={'class': 'form-control'}),
            'tiers_payant': IntegerNumberInput(attrs={'class': 'form-control'}),
            'total_paye': IntegerNumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_naissance'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        self.fields['date_acte'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        self.fields['date_facture'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        # Si on édite une facture qui a déjà un paiement, pré-remplir les champs correspondants
        if self.instance and hasattr(self.instance, 'paiement') and self.instance.paiement:
            paiement = self.instance.paiement
            self.fields['modalite_paiement'].initial = paiement.modalite_paiement
            self.fields['banque'].initial = paiement.banque
            self.fields['porteur'].initial = paiement.porteur
        
        # Réorganiser l'ordre des champs pour que modalite_paiement, banque et porteur apparaissent après total_paye.
        field_order = list(self.fields.keys())
        for key in ['modalite_paiement', 'banque', 'porteur']:
            if key in field_order:
                field_order.remove(key)
        if 'total_paye' in field_order:
            index = field_order.index('total_paye')
            field_order.insert(index + 1, 'modalite_paiement')
            field_order.insert(index + 2, 'banque')
            field_order.insert(index + 3, 'porteur')
        self.order_fields(field_order)
    
    def clean(self):
        cleaned_data = super().clean()
        modalite = cleaned_data.get('modalite_paiement')
        banque = cleaned_data.get('banque')
        porteur = cleaned_data.get('porteur')
        # Si le mode de paiement est "Chèque", banque et porteur sont obligatoires.
        if modalite == 'Chèque':
            if not banque:
                self.add_error('banque', "Ce champ est requis pour les paiements par chèque.")
            if not porteur:
                self.add_error('porteur', "Ce champ est requis pour les paiements par chèque.")
        return cleaned_data
    
    def save(self, commit=True):
        facturation = super().save(commit=commit)
        modalite = self.cleaned_data.get('modalite_paiement')
        banque = self.cleaned_data.get('banque')
        porteur = self.cleaned_data.get('porteur')
        if modalite:
            paiement, created = Paiement.objects.get_or_create(facture=facturation)
            paiement.modalite_paiement = modalite
            if modalite == 'Chèque':
                paiement.banque = banque
                paiement.porteur = porteur
            else:
                paiement.banque = ""
                paiement.porteur = ""
            paiement.save()
        return facturation
