# ASBJJ - Alexandre Salgado Brazilian Jiu-Jitsu

![Django](https://img.shields.io/badge/Django-5.1.4-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.2-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Sobre o Projeto

O ASBJJ é uma plataforma web moderna para uma academia de artes marciais especializada em Jiu-Jitsu, Defesa Pessoal e Yoga. O projeto foi completamente reescrito com tecnologias modernas e melhores práticas de desenvolvimento.

## ✨ Principais Melhorias Implementadas

### 🏗️ Arquitetura e Estrutura
- **Django 5.1.4** - Versão mais recente com recursos avançados
- **Arquitetura modular** - Apps organizados por funcionalidade
- **Variáveis de ambiente** - Configurações seguras com django-environ
- **Class-Based Views** - Views modernas e reutilizáveis
- **Sistema de apps** - Separação clara de responsabilidades

### 🎨 Interface e Design
- **Bootstrap 5.3.2** - Framework CSS moderno e responsivo
- **Design system** - Cores, tipografia e componentes consistentes
- **Responsividade completa** - Otimizado para todos os dispositivos
- **Acessibilidade** - Seguindo padrões WCAG
- **Animações suaves** - Transições e efeitos visuais

### 📊 Funcionalidades Avançadas
- **Sistema de agendamentos** - Aulas experimentais e regulares
- **Gestão de alunos** - Perfis completos e histórico
- **Sistema de avaliações** - Depoimentos e reviews
- **Newsletter** - Email marketing automatizado
- **Blog integrado** - Conteúdo dinâmico
- **Galeria de fotos** - Lightbox e categorias
- **FAQ dinâmico** - Perguntas frequentes organizadas

### 🔒 Segurança e Performance
- **Configurações de segurança** - Headers e proteções
- **Cache Redis** - Performance otimizada
- **WhiteNoise** - Servir arquivos estáticos
- **Logging configurado** - Monitoramento de erros
- **Validação robusta** - Formulários seguros

### 🚀 DevOps e Deploy
- **Docker ready** - Containerização preparada
- **Gunicorn** - Servidor WSGI para produção
- **Celery** - Tarefas assíncronas
- **Environment variables** - Configurações flexíveis
- **Debug toolbar** - Desenvolvimento otimizado

## 🛠️ Tecnologias Utilizadas

### Backend
- **Django 5.1.4** - Framework web Python
- **PostgreSQL/SQLite** - Banco de dados
- **Redis** - Cache e sessões
- **Celery** - Tarefas assíncronas
- **Django Allauth** - Autenticação avançada

### Frontend
- **Bootstrap 5.3.2** - Framework CSS
- **Font Awesome 6.4.0** - Ícones
- **Google Fonts** - Tipografia
- **Vanilla JavaScript** - Interatividade
- **CSS Grid/Flexbox** - Layout moderno

### Ferramentas de Desenvolvimento
- **django-extensions** - Utilitários de desenvolvimento
- **django-debug-toolbar** - Debug avançado
- **django-crispy-forms** - Formulários estilizados
- **Pillow** - Processamento de imagens

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- pip
- virtualenv (recomendado)

### Passos para instalação

1. **Clone o repositório**
```bash
git clone https://github.com/fabianosf/asbjj.git
cd asbjj
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
cp env_example.txt .env
# Edite o arquivo .env com suas configurações
```

5. **Execute as migrações**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

7. **Execute o servidor de desenvolvimento**
```bash
python manage.py runserver
```

## 🔧 Configuração

### Variáveis de Ambiente Principais

```env
# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados
DATABASE_URL=sqlite:///db.sqlite3

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Configurações de Produção

Para produção, certifique-se de:
- Definir `DEBUG=False`
- Configurar `ALLOWED_HOSTS` corretamente
- Usar banco de dados PostgreSQL
- Configurar Redis para cache
- Configurar servidor web (Nginx + Gunicorn)
- Configurar SSL/HTTPS

## 📁 Estrutura do Projeto

```
asbjj/
├── core/                   # App principal
│   ├── models.py          # Modelos principais
│   ├── views.py           # Views do site
│   ├── forms.py           # Formulários
│   └── templates/         # Templates principais
├── accounts/              # Sistema de usuários
│   ├── models.py          # Perfis de usuário
│   ├── views.py           # Autenticação
│   └── forms.py           # Formulários de usuário
├── classes/               # Sistema de aulas
│   ├── models.py          # Aulas e categorias
│   └── views.py           # Views das aulas
├── schedule/              # Sistema de agendamentos
│   ├── models.py          # Agendamentos e presença
│   └── views.py           # Views de agendamento
├── testimonials/          # Sistema de depoimentos
│   ├── models.py          # Depoimentos e FAQ
│   └── views.py           # Views de depoimentos
├── newsletter/            # Sistema de newsletter
│   ├── models.py          # Assinantes e campanhas
│   └── views.py           # Views de newsletter
├── templates/             # Templates base
├── static/                # Arquivos estáticos
├── media/                 # Arquivos de mídia
└── projeto/               # Configurações do Django
    ├── settings.py        # Configurações
    └── urls.py           # URLs principais
```

## 🎯 Funcionalidades Principais

### Para Visitantes
- ✅ Página inicial moderna e atrativa
- ✅ Catálogo completo de aulas
- ✅ Sistema de agendamento de aulas experimentais
- ✅ Galeria de fotos com lightbox
- ✅ Blog com posts dinâmicos
- ✅ FAQ organizado por categorias
- ✅ Formulário de contato inteligente
- ✅ Sistema de newsletter

### Para Alunos
- ✅ Perfil completo de usuário
- ✅ Agendamento de aulas
- ✅ Histórico de presença
- ✅ Controle de pagamentos
- ✅ Sistema de avaliações
- ✅ Notificações personalizadas

### Para Administradores
- ✅ Painel administrativo completo
- ✅ Gestão de alunos e instrutores
- ✅ Controle de agendamentos
- ✅ Sistema de relatórios
- ✅ Gerenciamento de conteúdo
- ✅ Configurações do site

## 🚀 Deploy em Produção

### Usando Docker (Recomendado)

1. **Build da imagem**
```bash
docker build -t asbjj .
```

2. **Execute o container**
```bash
docker run -d -p 8000:8000 --env-file .env asbjj
```

### Deploy Manual

1. **Configure o servidor**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv nginx redis-server
```

2. **Configure o Nginx**
```nginx
server {
    listen 80;
    server_name asbjj.com.br;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/asbjj/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/asbjj/media/;
    }
}
```

3. **Configure o Gunicorn**
```bash
gunicorn --bind 0.0.0.0:8000 projeto.wsgi:application
```

## 📈 Performance e SEO

- **Lazy loading** para imagens
- **Compressão** de arquivos estáticos
- **Cache** Redis configurado
- **Meta tags** otimizadas
- **Sitemap** automático
- **Robots.txt** configurado
- **Schema.org** markup
- **Open Graph** tags

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Desenvolvedor

**Fabiano Freitas**
- Website: [https://fabianosf.github.io/fabianosf_/](https://fabianosf.github.io/fabianosf_/)
- GitHub: [@fabianosf](https://github.com/fabianosf)
- LinkedIn: [Fabiano Freitas](https://linkedin.com/in/fabianosf)

## 📞 Contato

- **Site**: [https://asbjj.com.br](https://asbjj.com.br)
- **Email**: admin@asbjj.com.br
- **WhatsApp**: +55 11 99999-9999

---

⭐ **Se este projeto foi útil para você, considere dar uma estrela no repositório!**
