from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('meus-agendamentos/', views.MyBookingsView.as_view(), name='my_bookings'),
    path('agendamento/<int:booking_id>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('cancelar/<int:booking_id>/', views.CancelBookingView.as_view(), name='cancel_booking'),
    path('presenca/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('pagamentos/', views.PaymentListView.as_view(), name='payment_list'),
]
