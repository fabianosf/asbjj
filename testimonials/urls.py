from django.urls import path
from . import views

app_name = 'testimonials'

urlpatterns = [
    path('', views.TestimonialListView.as_view(), name='list'),
    path('novo/', views.TestimonialCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TestimonialDetailView.as_view(), name='detail'),
    path('avaliar/<int:class_id>/', views.ReviewCreateView.as_view(), name='create_review'),
    path('faq/', views.FAQView.as_view(), name='faq'),
]
