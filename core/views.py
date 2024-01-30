from django.views.generic import TemplateView

 

class IndexView(TemplateView):
    template_name = 'index.html'

class HomeView(TemplateView):
    template_name = 'home.html'


class AboutView(TemplateView):
    template_name = 'about.html'


class ClassView(TemplateView):
    template_name = 'class.html'

class ContactView(TemplateView):
    template_name = 'contact.html'

    
class ScheduleView(TemplateView):
    template_name = 'schedule.html'