from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator que restringe acesso apenas para admin e fabianosf
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.username not in ['admin', 'fabianosf']:
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def student_required(view_func):
    """
    Decorator que restringe acesso apenas para alunos (não admin/fabianosf)
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.username in ['admin', 'fabianosf']:
            messages.info(request, 'Administradores devem usar o dashboard administrativo.')
            return redirect('dashboard')
        
        try:
            profile = request.user.student_profile
            if not profile.is_student or not profile.student_profile:
                messages.error(request, 'Acesso negado. Você não é um aluno.')
                return redirect('login')
        except:
            messages.error(request, 'Perfil de usuário não encontrado.')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def instructor_required(view_func):
    """
    Decorator que restringe acesso apenas para professores (não admin/fabianosf)
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.username in ['admin', 'fabianosf']:
            messages.info(request, 'Administradores devem usar o dashboard administrativo.')
            return redirect('dashboard')
        
        try:
            profile = request.user.student_profile
            if not profile.is_instructor:
                messages.error(request, 'Acesso negado. Você não é um professor.')
                return redirect('login')
        except:
            messages.error(request, 'Perfil de usuário não encontrado.')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view



