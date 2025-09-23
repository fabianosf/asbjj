from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('inscrever/', views.NewsletterSubscribeView.as_view(), name='subscribe'),
    path('confirmar/<str:token>/', views.NewsletterConfirmView.as_view(), name='confirm'),
    path('descadastrar/<str:token>/', views.NewsletterUnsubscribeView.as_view(), name='unsubscribe'),
    path('preferencias/<str:token>/', views.NewsletterPreferencesView.as_view(), name='preferences'),
]
