# Changelog - ASBJJ

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.3.0] - 2025-09-30

### ✨ Novos Recursos

#### WhatsApp Integration
- Integração com WhatsApp para notificações de contato
- Link automático para responder mensagens via WhatsApp
- Campo `whatsapp_url` no modelo `ContactMessage`
- Configuração via `ADMIN_WHATSAPP` no `.env`

#### Email Templates Profissionais
- Template base responsivo para emails
- Email de notificação de contato com HTML
- Email de confirmação de pedido aprimorado
- Design moderno com cores da marca
- Suporte a dark mode

#### Compartilhamento Social
- Botões de compartilhamento em produtos
- Facebook, Twitter, WhatsApp, Pinterest, LinkedIn
- Compartilhamento via email
- Meta tags Open Graph otimizadas
- Schema.org para produtos

#### Performance & Monitoring
- Middleware de performance tracking
- Headers de tempo de resposta
- Logging de requisições lentas (>1s)
- Rate limiting configurável
- Cache Redis otimizado com compressão

### 🔒 Segurança

- Headers de segurança adicionais
- Content Security Policy (CSP)
- Rate limiting por IP
- Proteção contra brute force
- Cookies HTTPOnly e SameSite
- Validação de senhas (mínimo 12 caracteres)

### 📱 SEO & Mobile

- Meta tags completas (robots, geo, language)
- Open Graph e Twitter Cards
- Schema.org structured data
- Sitemap XML atualizado
- Robots.txt otimizado
- PWA manifest
- Service Worker para cache
- Viewport otimizado para mobile
- Touch-friendly buttons (44px)

### 🎨 UI/UX Improvements

- Design profissional com paleta de cores sóbria
- Templates de email responsivos
- Notificações toast aprimoradas
- Animações suaves
- Loading states em botões
- Feedback visual em ações

### 🛠️ Infraestrutura

- Sistema de backup automático
- Script shell para backup (daily/weekly/monthly)
- Comando Django para restauração
- Middleware customizado para performance
- Middleware de tratamento de erros
- Logging com rotação automática

### 📖 Documentação

- API_DOCUMENTATION.md completa
- WHATSAPP_CONFIG.md
- CHANGELOG.md
- Exemplos de código JavaScript
- Instruções de configuração

### 🧪 Testes

- 55 testes unitários passando
- Cobertura de código documentada
- Testes de segurança
- Testes de performance
- Testes de integração

### 🐛 Correções

- Removido código de debug (prints)
- Limpeza de imports não utilizados
- Corrigido erro de indentação em views
- Apps não utilizados removidos (classes, newsletter, schedule, testimonials)
- Rate limiting desabilitado em desenvolvimento
- Correção de compatibilidade SQLite/MySQL

### 🗑️ Removido

- Apps não utilizados: `classes/`, `newsletter/`, `schedule/`, `testimonials/`
- Tasks do Celery dependentes de apps removidos
- Código de debug (console.log, print)
- Imports não utilizados

## [1.2.0] - 2025-09-29

### ✨ Novos Recursos

#### E-commerce Completo
- Sistema de carrinho de compras
- Checkout com múltiplas formas de pagamento
- Integração com Mercado Pago
- Sistema de cupons de desconto
- Cálculo de frete
- Lista de desejos
- Histórico de pedidos

#### Programa de Fidelidade
- Sistema de pontos
- Níveis (Bronze, Prata, Ouro, Platina)
- Recompensas por compras
- Histórico de pontos
- Dashboard de fidelidade

#### Chat de Suporte
- Chat em tempo real
- Templates de respostas
- Anexos de arquivos
- Status de leitura
- Histórico de conversas

#### Sistema de Recomendações
- Produtos relacionados
- Frequentemente comprados juntos
- Recomendações baseadas em categoria
- Produtos populares
- Produtos sazonais

### 🔒 Segurança Inicial

- CSRF protection
- XSS protection
- SQL injection protection
- Rate limiting básico
- Sessões seguras

## [1.1.0] - 2025-09-28

### ✨ Novos Recursos

#### Loja Online
- Catálogo de produtos
- Categorias de produtos
- Filtros e ordenação
- Busca de produtos
- Detalhes do produto
- Galeria de imagens

#### Sistema de Avaliações
- Avaliações de produtos
- Rating com estrelas
- Comentários
- Moderação de avaliações

### 🎨 Design

- Layout responsivo com Bootstrap 5
- Paleta de cores customizada
- Animações e transições
- Grid de produtos moderno

## [1.0.0] - 2025-09-27

### ✨ Lançamento Inicial

#### Core Features
- Página inicial
- Sobre nós
- Serviços
- Contato
- Galeria
- Blog

#### Admin
- Django Admin customizado
- Gestão de configurações do site
- Gestão de instrutores
- Gestão de mensagens de contato

#### Infraestrutura
- Django 5.1.4
- PostgreSQL
- Redis
- Nginx
- Docker support
- WhiteNoise para arquivos estáticos

---

## Links Úteis

- [API Documentation](API_DOCUMENTATION.md)
- [WhatsApp Configuration](WHATSAPP_CONFIG.md)
- [README](README.md)
