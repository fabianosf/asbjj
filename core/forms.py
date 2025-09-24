from django import forms
from django.core.validators import RegexValidator
from .models import ContactMessage


class TrialClassBookingForm(forms.Form):
    """Formulário público para agendamento de aula experimental."""

    first_name = forms.CharField(
        label='Nome',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome'})
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu sobrenome'})
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )
    phone = forms.CharField(
        label='Telefone',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'})
    )
    birth_date = forms.DateField(
        label='Data de nascimento', required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    class_id = forms.IntegerField(widget=forms.HiddenInput())
    preferred_date = forms.DateField(
        label='Data preferida',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    preferred_time = forms.TimeField(
        label='Horário preferido', required=False,
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    notes = forms.CharField(
        label='Observações', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Informações adicionais'})
    )


class ContactForm(forms.ModelForm):
    """Formulário de contato melhorado"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message', 'category']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Assunto da sua mensagem'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Digite sua mensagem aqui...',
                'rows': 5
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['message'].required = True
        self.fields['subject'].required = False
        self.fields['phone'].required = False
        self.fields['category'].required = False

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove caracteres não numéricos
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) < 10:
                raise forms.ValidationError('Telefone deve ter pelo menos 10 dígitos.')
        return phone

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError('Mensagem deve ter pelo menos 10 caracteres.')
        return message