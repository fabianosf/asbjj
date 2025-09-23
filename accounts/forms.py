from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import TextInput, EmailInput, PasswordInput
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    """Formulário de registro de usuário"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Criar UserProfile associado apenas se não existir
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'is_active_student': False}
            )
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover help_texts padrão e aplicar classes Bootstrap
        field_placeholders = {
            'username': 'Nome de usuário',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'password1': 'Senha',
            'password2': 'Confirmar senha',
        }

        for name, field in self.fields.items():
            field.help_text = ''
            css_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{css_classes} form-control".strip()
            field.widget.attrs['placeholder'] = field_placeholders.get(name, field.label)

        # Garantir widgets corretos
        self.fields['username'].widget = TextInput(attrs=self.fields['username'].widget.attrs)
        self.fields['first_name'].widget = TextInput(attrs=self.fields['first_name'].widget.attrs)
        self.fields['last_name'].widget = TextInput(attrs=self.fields['last_name'].widget.attrs)
        self.fields['email'].widget = EmailInput(attrs=self.fields['email'].widget.attrs)
        self.fields['password1'].widget = PasswordInput(render_value=False, attrs=self.fields['password1'].widget.attrs)
        self.fields['password2'].widget = PasswordInput(render_value=False, attrs=self.fields['password2'].widget.attrs)


class UserLoginForm(forms.Form):
    """Formulário de login"""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuário ou E-mail',
        })
        self.fields['password'].widget = PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha',
        })
