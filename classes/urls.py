from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.ClassListView.as_view(), name='list'),
    path('<slug:slug>/', views.ClassDetailView.as_view(), name='detail'),
    path('categoria/<slug:slug>/', views.ClassCategoryView.as_view(), name='category'),
    path('agendar/<int:class_id>/', views.TrialClassBookingView.as_view(), name='trial_booking'),
    path('agendamento/sucesso/', views.TrialBookingSuccessView.as_view(), name='trial_booking_success'),
]
