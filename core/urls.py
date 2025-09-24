from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Páginas principais
    path('', views.HomeView.as_view(), name='index'),
    path('sobre/', views.AboutView.as_view(), name='about'),
    path('servicos/', views.ServicesView.as_view(), name='services'),
    path('contato/', views.ContactView.as_view(), name='contact'),
    path('galeria/', views.GalleryListView.as_view(), name='gallery'),
    # Blog removido
    path('inscricao/', views.EnrollmentApplicationView.as_view(), name='enrollment'),
    path('calendario/', views.CalendarView.as_view(), name='calendar'),
    path('loja/', views.ShopView.as_view(), name='shop'),
    path('healthz', views.healthz, name='healthz'),
    
    # URLs antigas para compatibilidade
    path('sobre/', views.sobre, name='sobre'),
    path('servicos/', views.servicos, name='servicos'),
    path('contato/', views.contato, name='contato'),
]


