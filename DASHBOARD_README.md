# 🥋 ASBJJ - Sistema de Gestão de Academia

Sistema completo de gestão para academia de Jiu-Jitsu com dashboard administrativo, controle de alunos, pagamentos e relatórios.

## 🚀 Funcionalidades Implementadas

### 📊 Dashboard Administrativo
- **Estatísticas em tempo real**: Alunos ativos, receita mensal, pagamentos pendentes
- **Interface moderna**: Design responsivo similar ao AdminLTE
- **Ações rápidas**: Cadastro de alunos, registro de pagamentos, marcação de presença

### 👥 Gestão de Alunos
- **Cadastro completo**: Dados pessoais, documentos, endereço, informações médicas
- **Controle de faixas**: Branca, Azul, Roxa, Marrom, Preta
- **Status de matrícula**: Ativo/Inativo
- **Histórico completo**: Pagamentos, presenças, assinaturas

### 💳 Sistema de Pagamentos
- **Planos flexíveis**: Mensal, Trimestral, Semestral, Anual
- **Múltiplos métodos**: PIX, Cartão, Dinheiro, Transferência
- **PIX com QR Code**: Geração automática de QR codes
- **Controle de vencimentos**: Alertas de pagamentos pendentes
- **Relatórios financeiros**: Receita, inadimplência, estatísticas

### 📋 Controle de Presença
- **Registro de aulas**: Data, horário, instrutor
- **Status de presença**: Presente, Ausente, Atrasado, Justificado
- **Histórico de frequência**: Por aluno e período

### 📈 Relatórios e Analytics
- **Relatórios personalizados**: Por período, tipo de plano, status
- **Métricas importantes**: Taxa de pagamento, receita, inadimplência
- **Exportação de dados**: Para análise externa

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.1.4
- **Frontend**: HTML5, CSS3, JavaScript
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Pagamentos**: PIX, QR Code
- **Interface**: Django Admin personalizado

## 📦 Instalação e Configuração

### 1. Clone o repositório
```bash
git clone <repository-url>
cd asbjj
```

### 2. Configure o ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp env_example.txt .env
# Edite o arquivo .env com suas configurações
```

### 5. Execute as migrações
```bash
python manage.py migrate
```

### 6. Crie um superusuário
```bash
python manage.py createsuperuser
```

### 7. Crie dados de exemplo (opcional)
```bash
python manage.py create_sample_data
```

### 8. Execute o servidor
```bash
python manage.py runserver
```

## 🌐 Acesso ao Sistema

### Dashboard Administrativo
- **URL**: http://localhost:8000/dashboard/
- **Usuário**: admin (ou o usuário criado)
- **Senha**: (a senha definida no createsuperuser)

### Admin Django Padrão
- **URL**: http://localhost:8000/admin/
- **Usuário**: admin
- **Senha**: (a senha definida no createsuperuser)

## 📱 Como Usar

### 1. Cadastrar Alunos
1. Acesse o dashboard
2. Clique em "➕ Novo Aluno"
3. Preencha os dados pessoais
4. Salve o cadastro

### 2. Criar Planos de Pagamento
1. Vá em "Planos de Pagamento"
2. Clique em "Adicionar Plano"
3. Defina nome, preço e duração
4. Configure aulas ilimitadas ou limite mensal

### 3. Registrar Pagamentos
1. Acesse "Pagamentos"
2. Clique em "Adicionar Pagamento"
3. Selecione o aluno e plano
4. Escolha o método de pagamento
5. Para PIX, será gerado QR Code automaticamente

### 4. Marcar Presença
1. Vá em "Presenças"
2. Clique em "Adicionar Presença"
3. Selecione aluno, data e horário
4. Marque o status da presença

### 5. Gerar Relatórios
1. Acesse "Relatórios de Pagamento"
2. Clique em "Gerar Relatório"
3. Defina o período
4. Visualize as estatísticas

## 🔧 Configurações Avançadas

### PIX Configuration
Para configurar PIX em produção, adicione no `.env`:
```env
PIX_KEY=seu_email@exemplo.com
PIX_WEBHOOK_SECRET=sua_chave_secreta
```

### Email Configuration
Para envio de notificações por email:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_app
```

### Banco de Dados PostgreSQL
Para produção, configure PostgreSQL:
```env
DATABASE_URL=postgres://usuario:senha@localhost:5432/asbjj_db
```

## 📊 Estrutura do Banco de Dados

### Modelos Principais
- **Student**: Dados dos alunos
- **PaymentPlan**: Planos de pagamento
- **StudentSubscription**: Assinaturas dos alunos
- **Payment**: Pagamentos realizados
- **PIXPayment**: Pagamentos PIX com QR Code
- **Attendance**: Controle de presença
- **PaymentNotification**: Notificações de pagamento
- **PaymentReport**: Relatórios gerados

## 🚀 Deploy em Produção

### 1. Configure o ambiente de produção
```bash
# Instale dependências de produção
pip install gunicorn psycopg2-binary

# Configure variáveis de ambiente
DEBUG=False
ALLOWED_HOSTS=seu_dominio.com
DATABASE_URL=postgres://...
```

### 2. Execute migrações
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 3. Configure servidor web (Nginx + Gunicorn)
```bash
# Use o arquivo nginx.conf incluído
# Configure o arquivo docker-compose.yml
```

## 📞 Suporte

Para dúvidas ou problemas:
- **Email**: admin@asbjj.com.br
- **WhatsApp**: +55 11 99999-9999

## 📄 Licença

Este projeto é proprietário da ASBJJ - Alexandre Salgado Brazilian Jiu-Jitsu.

---

**Desenvolvido com ❤️ para a ASBJJ**
