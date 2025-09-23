from django.core.management.base import BaseCommand
from students.models import Student, PaymentPlan, StudentSubscription, Payment
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Cria dados de exemplo para o dashboard'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados de exemplo...')
        
        # Criar planos de pagamento
        plans = [
            {
                'name': 'Mensal',
                'description': 'Plano mensal com aulas ilimitadas',
                'price': Decimal('150.00'),
                'duration_days': 30,
                'allows_unlimited_classes': True,
            },
            {
                'name': 'Trimestral',
                'description': 'Plano trimestral com desconto',
                'price': Decimal('400.00'),
                'duration_days': 90,
                'allows_unlimited_classes': True,
            },
            {
                'name': 'Semestral',
                'description': 'Plano semestral com desconto especial',
                'price': Decimal('750.00'),
                'duration_days': 180,
                'allows_unlimited_classes': True,
            },
            {
                'name': 'Anual',
                'description': 'Plano anual com máximo desconto',
                'price': Decimal('1400.00'),
                'duration_days': 365,
                'allows_unlimited_classes': True,
            },
        ]
        
        created_plans = []
        for plan_data in plans:
            plan, created = PaymentPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            created_plans.append(plan)
            if created:
                self.stdout.write(f'Criado plano: {plan.name}')
        
        # Criar alunos de exemplo
        students_data = [
            {
                'first_name': 'João',
                'last_name': 'Silva',
                'email': 'joao.silva@email.com',
                'phone': '+5511999999999',
                'cpf': '123.456.789-00',
                'address': 'Rua das Flores, 123',
                'city': 'São Paulo',
                'state': 'SP',
                'zip_code': '01234-567',
                'belt_color': 'white',
                'birth_date': timezone.now().date().replace(year=1990),
                'emergency_contact_name': 'Maria Silva',
                'emergency_contact_phone': '+5511888888888',
            },
            {
                'first_name': 'Maria',
                'last_name': 'Santos',
                'email': 'maria.santos@email.com',
                'phone': '+5511999999998',
                'cpf': '123.456.789-01',
                'address': 'Av. Paulista, 456',
                'city': 'São Paulo',
                'state': 'SP',
                'zip_code': '01234-568',
                'belt_color': 'blue',
                'birth_date': timezone.now().date().replace(year=1985),
                'emergency_contact_name': 'José Santos',
                'emergency_contact_phone': '+5511888888887',
            },
            {
                'first_name': 'Pedro',
                'last_name': 'Oliveira',
                'email': 'pedro.oliveira@email.com',
                'phone': '+5511999999997',
                'cpf': '123.456.789-02',
                'address': 'Rua Augusta, 789',
                'city': 'São Paulo',
                'state': 'SP',
                'zip_code': '01234-569',
                'belt_color': 'purple',
                'birth_date': timezone.now().date().replace(year=1988),
                'emergency_contact_name': 'Ana Oliveira',
                'emergency_contact_phone': '+5511888888886',
            },
            {
                'first_name': 'Ana',
                'last_name': 'Costa',
                'email': 'ana.costa@email.com',
                'phone': '+5511999999996',
                'cpf': '123.456.789-03',
                'address': 'Rua Oscar Freire, 321',
                'city': 'São Paulo',
                'state': 'SP',
                'zip_code': '01234-570',
                'belt_color': 'brown',
                'birth_date': timezone.now().date().replace(year=1992),
                'emergency_contact_name': 'Carlos Costa',
                'emergency_contact_phone': '+5511888888885',
            },
            {
                'first_name': 'Carlos',
                'last_name': 'Ferreira',
                'email': 'carlos.ferreira@email.com',
                'phone': '+5511999999995',
                'cpf': '123.456.789-04',
                'address': 'Rua da Consolação, 654',
                'city': 'São Paulo',
                'state': 'SP',
                'zip_code': '01234-571',
                'belt_color': 'black',
                'birth_date': timezone.now().date().replace(year=1980),
                'emergency_contact_name': 'Lucia Ferreira',
                'emergency_contact_phone': '+5511888888884',
            },
        ]
        
        created_students = []
        for student_data in students_data:
            student, created = Student.objects.get_or_create(
                email=student_data['email'],
                defaults=student_data
            )
            created_students.append(student)
            if created:
                self.stdout.write(f'Criado aluno: {student.full_name}')
        
        # Criar assinaturas e pagamentos
        admin_user = User.objects.filter(is_superuser=True).first()
        
        for student in created_students:
            # Criar assinatura
            plan = random.choice(created_plans)
            start_date = timezone.now().date()
            end_date = start_date + timezone.timedelta(days=plan.duration_days)
            
            subscription, created = StudentSubscription.objects.get_or_create(
                student=student,
                payment_plan=plan,
                start_date=start_date,
                end_date=end_date,
                defaults={'status': 'active'}
            )
            
            if created:
                self.stdout.write(f'Criada assinatura para {student.full_name}')
            
            # Criar pagamentos
            payment_methods = ['pix', 'credit_card', 'cash', 'bank_transfer']
            payment_statuses = ['paid', 'pending', 'paid', 'paid']  # Mais pagos que pendentes
            
            for i in range(random.randint(1, 3)):  # 1 a 3 pagamentos por aluno
                payment_date = timezone.now().date() - timezone.timedelta(days=random.randint(0, 30))
                due_date = payment_date + timezone.timedelta(days=random.randint(-5, 5))
                
                payment, created = Payment.objects.get_or_create(
                    student=student,
                    subscription=subscription,
                    amount=plan.price,
                    payment_method=random.choice(payment_methods),
                    payment_status=random.choice(payment_statuses),
                    due_date=due_date,
                    defaults={
                        'paid_date': payment_date if random.choice(payment_statuses) == 'paid' else None,
                        'created_by': admin_user,
                    }
                )
                
                if created:
                    self.stdout.write(f'Criado pagamento para {student.full_name}: R$ {payment.final_amount}')
        
        self.stdout.write(
            self.style.SUCCESS('Dados de exemplo criados com sucesso!')
        )
