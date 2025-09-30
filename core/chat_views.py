"""
Views para sistema de chat de suporte
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
import json

from .chat_models import ChatRoom, ChatMessage, ChatTemplate


class ChatSupportView(TemplateView):
    """Página de suporte via chat"""
    template_name = 'core/chat_support.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Buscar chat existente por email
        email = self.request.GET.get('email', '')
        if email:
            try:
                chat_room = ChatRoom.objects.filter(
                    customer_email=email,
                    status__in=['open', 'waiting']
                ).order_by('-created_at').first()
                
                if chat_room:
                    context['chat_room'] = chat_room
                    context['messages'] = chat_room.messages.all()
            except ChatRoom.DoesNotExist:
                pass
        
        context['search_email'] = email
        return context


class AdminChatView(LoginRequiredMixin, ListView):
    """Painel de chat para administradores"""
    model = ChatRoom
    template_name = 'core/admin_chat.html'
    context_object_name = 'chat_rooms'
    paginate_by = 20

    def get_queryset(self):
        queryset = ChatRoom.objects.all()
        
        # Filtros
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(customer_name__icontains=search) |
                Q(customer_email__icontains=search) |
                Q(subject__icontains=search)
            )
        
        return queryset.select_related('assigned_to').prefetch_related('messages')


class ChatRoomView(LoginRequiredMixin, TemplateView):
    """Visualização de uma sala de chat específica"""
    template_name = 'core/chat_room.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = self.kwargs.get('room_id')
        
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        messages = chat_room.messages.all()
        templates = ChatTemplate.objects.filter(is_active=True)
        
        context.update({
            'chat_room': chat_room,
            'messages': messages,
            'templates': templates,
        })
        
        return context


@require_http_methods(["POST"])
def start_chat(request):
    """Inicia um novo chat"""
    try:
        data = json.loads(request.body)
        
        customer_name = data.get('customer_name', '').strip()
        customer_email = data.get('customer_email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        if not all([customer_name, customer_email, subject, message]):
            return JsonResponse({
                'success': False,
                'message': 'Todos os campos são obrigatórios'
            })
        
        # Verificar se já existe um chat aberto para este email
        existing_chat = ChatRoom.objects.filter(
            customer_email=customer_email,
            status__in=['open', 'waiting']
        ).first()
        
        if existing_chat:
            return JsonResponse({
                'success': False,
                'message': 'Você já possui um chat aberto',
                'chat_id': existing_chat.id
            })
        
        # Criar nova sala de chat
        chat_room = ChatRoom.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            subject=subject,
            status='waiting'
        )
        
        # Criar primeira mensagem
        ChatMessage.objects.create(
            room=chat_room,
            sender_type='customer',
            sender_name=customer_name,
            sender_email=customer_email,
            message=message
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Chat iniciado com sucesso',
            'chat_id': chat_room.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao iniciar chat'
        })


@require_http_methods(["POST"])
def send_message(request):
    """Envia mensagem no chat"""
    try:
        data = json.loads(request.body)
        
        chat_id = data.get('chat_id')
        sender_name = data.get('sender_name', '').strip()
        sender_email = data.get('sender_email', '').strip()
        message = data.get('message', '').strip()
        sender_type = data.get('sender_type', 'customer')
        
        if not all([chat_id, sender_name, message]):
            return JsonResponse({
                'success': False,
                'message': 'Dados incompletos'
            })
        
        chat_room = get_object_or_404(ChatRoom, id=chat_id)
        
        # Criar mensagem
        chat_message = ChatMessage.objects.create(
            room=chat_room,
            sender_type=sender_type,
            sender_name=sender_name,
            sender_email=sender_email,
            message=message
        )
        
        # Atualizar status da sala se necessário
        if chat_room.status == 'waiting' and sender_type == 'admin':
            chat_room.status = 'open'
            chat_room.assigned_to = request.user
            chat_room.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Mensagem enviada',
            'message_id': chat_message.id,
            'created_at': chat_message.created_at.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao enviar mensagem'
        })


@require_http_methods(["GET"])
def get_messages(request, chat_id):
    """Obtém mensagens de um chat"""
    try:
        chat_room = get_object_or_404(ChatRoom, id=chat_id)
        messages = chat_room.messages.all()
        
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': message.id,
                'sender_type': message.sender_type,
                'sender_name': message.sender_name,
                'message': message.message,
                'created_at': message.created_at.isoformat(),
                'is_read': message.is_read
            })
        
        return JsonResponse({
            'success': True,
            'messages': messages_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao buscar mensagens'
        })


@login_required
@require_http_methods(["POST"])
def assign_chat(request, chat_id):
    """Atribui chat a um administrador"""
    try:
        chat_room = get_object_or_404(ChatRoom, id=chat_id)
        chat_room.assigned_to = request.user
        chat_room.status = 'open'
        chat_room.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Chat atribuído com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao atribuir chat'
        })


@login_required
@require_http_methods(["POST"])
def close_chat(request, chat_id):
    """Fecha um chat"""
    try:
        chat_room = get_object_or_404(ChatRoom, id=chat_id)
        chat_room.close()
        
        return JsonResponse({
            'success': True,
            'message': 'Chat fechado com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao fechar chat'
        })


@login_required
@require_http_methods(["GET"])
def get_template(request, template_id):
    """Obtém template de resposta"""
    try:
        template = get_object_or_404(ChatTemplate, id=template_id)
        
        return JsonResponse({
            'success': True,
            'template': {
                'id': template.id,
                'name': template.name,
                'subject': template.subject,
                'content': template.content
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao buscar template'
        })


@require_http_methods(["GET"])
def chat_status(request, chat_id):
    """Verifica status do chat"""
    try:
        chat_room = get_object_or_404(ChatRoom, id=chat_id)
        
        return JsonResponse({
            'success': True,
            'status': chat_room.status,
            'is_open': chat_room.is_open,
            'assigned_to': chat_room.assigned_to.username if chat_room.assigned_to else None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erro ao verificar status'
        })
