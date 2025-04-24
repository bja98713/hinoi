from django import forms
from django.utils import timezone
from .models import Facturation, Paiement
from .widgets import IntegerNumberInput, CodeSelectWidget

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
            'total_acte': IntegerNumberInput(attrs={'class': 'form-control'}),
            'tiers_payant': IntegerNumberInput(attrs={'class': 'form-control'}),
            'total_paye': IntegerNumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # formats de date
        for f in ('date_naissance','date_acte','date_facture'):
            self.fields[f].input_formats = ['%Y-%m-%d','%d/%m/%Y']
        # champs facultatifs
        self.fields['tiers_payant'].required = False
        self.fields['total_paye'].required = False
        self.fields['numero_facture'].required = False
        self.fields['code_acte'].required = False
        self.fields['total_acte'].required = False
        # pré-remplissage Paiement
        if self.instance.pk:
            try:
                paiement = self.instance.paiement
                self.fields['modalite_paiement'].initial = paiement.modalite_paiement
                self.fields['banque'].initial = paiement.banque
                self.fields['porteur'].initial = paiement.porteur
            except Paiement.DoesNotExist:
                pass
        # réordonner
        order = list(self.fields.keys())
        for key in ('modalite_paiement','banque','porteur'):
            if key in order:
                order.remove(key)
        if 'total_paye' in order:
            idx = order.index('total_paye')
            order[idx+1:idx+1] = ['modalite_paiement','banque','porteur']
        self.order_fields(order)

    def clean(self):
        data = super().clean()
        if data.get('modalite_paiement') == 'Chèque':
            if not data.get('banque'):
                self.add_error('banque', "Ce champ est requis pour les chèques.")
            if not data.get('porteur'):
                self.add_error('porteur', "Ce champ est requis pour les chèques.")
        return data

    def save(self, commit=True):
        # Génération automatique du numéro de facture si pas parcours de soins
        fact = super().save(commit=False)
        code = fact.code_acte
        if code and not code.parcours_soin:
            now = timezone.localtime()
            fact.numero_facture = now.strftime("FQ/%Y/%m/%d/%H:%M")
        else:
            fact.numero_facture = ''
        # Sauvegarde de Facturation
        fact.save()
        # Paiement associé
        modalite = self.cleaned_data.get('modalite_paiement')
        if modalite:
            paiement, _ = Paiement.objects.get_or_create(facture=fact)
            paiement.modalite_paiement = modalite
            if modalite == 'Chèque':
                paiement.banque = self.cleaned_data.get('banque','')
                paiement.porteur = self.cleaned_data.get('porteur','')
            else:
                paiement.banque = ''
                paiement.porteur = ''
            paiement.save()
        return fact
