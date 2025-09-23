from django import forms
from django.core.validators import RegexValidator
from .models import ContactMessage


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