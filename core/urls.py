from django.urls import path
from .views import  HomeView, AboutView, ClassView, ContactView, ScheduleView, IndexView


urlpatterns = [    
    path('', IndexView.as_view(), name='index'),    
    path('home/', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('class/', ClassView.as_view(), name='class'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('schedule/', ScheduleView.as_view(), name='schedule'),
]