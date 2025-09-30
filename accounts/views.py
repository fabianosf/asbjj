# accounts/views.py
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
import os
from django.conf import settings


def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username", None)
        password = request.POST.get("password", None)

        # Verificar se username_or_email não é None
        if username_or_email is not None:
            # Verificar se o input é um email
            if "@" in username_or_email:
                try:
                    user = User.objects.get(email=username_or_email)
                    username = user.username  # Pega o username relacionado ao email
                except User.DoesNotExist:
                    username = None
            else:
                username = username_or_email

            # Autenticar com username
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login efetuado com sucesso!")
                return redirect("core:index")
            else:
                messages.error(request, "Credenciais inválidas")
                return render(
                    request, "accounts/login.html", {"error": "Credenciais inválidas"}
                )
        else:
            messages.error(request, "Nome de usuário ou e-mail não fornecido")
            return render(
                request,
                "accounts/login.html",
                {"error": "Nome de usuário ou e-mail não fornecido"},
            )

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logout efetuado com sucesso!")
    return redirect("accounts:login")


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro realizado com sucesso! Faça login para continuar.")
            return redirect("accounts:login")
    else:
        form = UserRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


# robots google
def robots(request):
    if not settings.DEBUG:
        path = os.path.join(settings.STATIC_ROOT, 'robots.txt') # producao
    else:
        path = os.path.join(settings.BASE_DIR, 'core/static/robots.txt') # desenvolvimento
        
    with open(path, 'r') as arquivo:
        return HttpResponse(arquivo, content_type="text/plain")
        
        #return HttpResponse(arq, content_type="text/plain")
    # return HttpResponse("teste")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Após redefinir, limpar o flag must_change_password do perfil."""
    def form_valid(self, form):
        response = super().form_valid(form)
        try:
            user = getattr(self, 'user', None)
            if user and hasattr(user, 'student_profile'):
                profile = user.student_profile
                if getattr(profile, 'must_change_password', False):
                    profile.must_change_password = False
                    profile.save(update_fields=['must_change_password'])
        except Exception:
            pass
        return response
