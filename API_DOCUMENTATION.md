# API Documentation - ASBJJ

## Visão Geral

Esta documentação descreve as APIs e endpoints disponíveis no sistema ASBJJ.

## Autenticação

### Headers Obrigatórios
```
Content-Type: application/json
X-CSRFToken: <token>
X-Requested-With: XMLHttpRequest
```

### CSRF Token
Para requisições POST, PUT, DELETE, é necessário incluir o token CSRF:
```javascript
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
```

## Endpoints

### 1. Carrinho de Compras

#### GET `/carrinho/total/`
Retorna o total atual do carrinho.

**Resposta:**
```json
{
    "success": true,
    "cart_total_items": 3,
    "cart_total_price": 150.00,
    "cart_total_price_formatted": "R$ 150,00"
}
```

#### POST `/carrinho/adicionar/<product_id>/`
Adiciona um produto ao carrinho.

**Parâmetros:**
- `quantity` (int): Quantidade do produto

**Resposta:**
```json
{
    "success": true,
    "message": "Produto adicionado ao carrinho",
    "cart_total_items": 3,
    "cart_total_price": 150.00,
    "cart_total_price_formatted": "R$ 150,00",
    "item_price": 50.00,
    "item_price_formatted": "R$ 50,00",
    "item_quantity": 1
}
```

#### POST `/carrinho/remover/<product_id>/`
Remove um produto do carrinho.

**Resposta:**
```json
{
    "success": true,
    "message": "Produto removido do carrinho"
}
```

#### POST `/carrinho/atualizar/<item_id>/`
Atualiza a quantidade de um item no carrinho.

**Parâmetros:**
- `quantity` (int): Nova quantidade

**Resposta:**
```json
{
    "success": true,
    "message": "Carrinho atualizado",
    "cart_total_items": 2,
    "cart_total_price": 100.00,
    "cart_total_price_formatted": "R$ 100,00"
}
```

#### POST `/carrinho/limpar/`
Limpa todo o carrinho.

**Resposta:**
```json
{
    "success": true,
    "message": "Carrinho limpo"
}
```

### 2. Lista de Desejos

#### POST `/favoritos/adicionar/<product_id>/`
Adiciona um produto à lista de desejos.

**Resposta:**
```json
{
    "success": true,
    "message": "Produto adicionado aos favoritos",
    "wishlist_total_items": 2
}
```

#### POST `/favoritos/remover/<product_id>/`
Remove um produto da lista de desejos.

**Resposta:**
```json
{
    "success": true,
    "message": "Produto removido dos favoritos",
    "wishlist_total_items": 1
}
```

### 3. Cupons

#### POST `/cupom/aplicar/`
Aplica um cupom de desconto.

**Parâmetros:**
- `code` (string): Código do cupom

**Resposta:**
```json
{
    "success": true,
    "message": "Cupom aplicado com sucesso",
    "discount": 10.00,
    "discount_formatted": "R$ 10,00",
    "new_total": 90.00,
    "new_total_formatted": "R$ 90,00"
}
```

#### POST `/cupom/remover/`
Remove o cupom aplicado.

**Resposta:**
```json
{
    "success": true,
    "message": "Cupom removido",
    "new_total": 100.00,
    "new_total_formatted": "R$ 100,00"
}
```

### 4. Frete

#### POST `/frete/calcular/`
Calcula o valor do frete.

**Parâmetros:**
- `cep` (string): CEP de destino
- `total` (float): Valor total do pedido

**Resposta:**
```json
{
    "success": true,
    "shipping_cost": 15.00,
    "shipping_cost_formatted": "R$ 15,00",
    "delivery_time": "3-5 dias úteis",
    "free_shipping": false
}
```

### 5. Chat de Suporte

#### POST `/chat/start/`
Inicia uma nova conversa de chat.

**Parâmetros:**
- `name` (string): Nome do usuário
- `email` (string): Email do usuário
- `subject` (string): Assunto da conversa

**Resposta:**
```json
{
    "success": true,
    "chat_id": 123,
    "message": "Chat iniciado com sucesso"
}
```

#### POST `/chat/send/`
Envia uma mensagem no chat.

**Parâmetros:**
- `chat_id` (int): ID do chat
- `message` (string): Mensagem
- `sender_type` (string): "user" ou "admin"

**Resposta:**
```json
{
    "success": true,
    "message_id": 456,
    "message": "Mensagem enviada"
}
```

#### GET `/chat/messages/<chat_id>/`
Retorna as mensagens de um chat.

**Resposta:**
```json
{
    "success": true,
    "messages": [
        {
            "id": 456,
            "content": "Olá, como posso ajudar?",
            "sender_type": "admin",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

#### GET `/chat/status/<chat_id>/`
Verifica o status de um chat.

**Resposta:**
```json
{
    "success": true,
    "status": "active",
    "last_activity": "2024-01-15T10:30:00Z",
    "unread_count": 2
}
```

### 6. Health Check

#### GET `/healthz`
Endpoint de health check.

**Resposta:**
```json
{
    "status": "ok",
    "time": "2024-01-15T10:30:00Z",
    "debug": false
}
```

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `400 Bad Request`: Dados inválidos
- `403 Forbidden`: Token CSRF inválido
- `404 Not Found`: Recurso não encontrado
- `429 Too Many Requests`: Rate limit excedido
- `500 Internal Server Error`: Erro interno do servidor

## Rate Limiting

- **APIs**: 10 requisições por minuto por IP
- **Formulários**: 1 requisição por segundo por IP
- **Login**: 5 tentativas por minuto por IP

## Tratamento de Erros

### Formato de Erro
```json
{
    "success": false,
    "error": "Error type",
    "message": "Descrição do erro",
    "details": "Detalhes adicionais (opcional)"
}
```

### Tipos de Erro Comuns

#### CSRF Token Inválido
```json
{
    "error": "CSRF token missing or incorrect",
    "detail": "Please refresh the page and try again."
}
```

#### Rate Limit Excedido
```json
{
    "error": "Rate limit exceeded",
    "message": "Too many requests. Please try again later."
}
```

#### Produto Não Encontrado
```json
{
    "success": false,
    "message": "Produto não encontrado"
}
```

## Exemplos de Uso

### JavaScript (Fetch API)

```javascript
// Adicionar produto ao carrinho
async function addToCart(productId, quantity = 1) {
    const formData = new FormData();
    formData.append('quantity', quantity);
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    
    try {
        const response = await fetch(`/carrinho/adicionar/${productId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('Produto adicionado:', data.message);
            updateCartDisplay(data);
        } else {
            console.error('Erro:', data.message);
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
    }
}

// Obter total do carrinho
async function getCartTotal() {
    try {
        const response = await fetch('/carrinho/total/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data;
        }
    } catch (error) {
        console.error('Erro ao obter total do carrinho:', error);
    }
}
```

### jQuery

```javascript
// Aplicar cupom
function applyCoupon(code) {
    $.ajax({
        url: '/cupom/aplicar/',
        method: 'POST',
        data: {
            code: code,
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
        },
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(data) {
            if (data.success) {
                alert('Cupom aplicado: ' + data.message);
                updateCartTotal(data.new_total_formatted);
            } else {
                alert('Erro: ' + data.message);
            }
        },
        error: function(xhr, status, error) {
            alert('Erro na requisição: ' + error);
        }
    });
}
```

## Segurança

### Headers de Segurança
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

### Content Security Policy
```
default-src 'self'; 
script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.googletagmanager.com; 
style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; 
font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; 
img-src 'self' data: https:; 
connect-src 'self' https://www.google-analytics.com; 
frame-src 'none';
```

## Monitoramento

### Performance
- Tempo de resposta das APIs
- Número de requisições por minuto
- Taxa de erro por endpoint

### Logs
- Todas as requisições são logadas
- Erros são registrados com stack trace
- Requisições lentas (>1s) são marcadas

### Métricas
- Core Web Vitals
- Tempo de carregamento de páginas
- Erros JavaScript
- Taxa de conversão do carrinho

## Changelog

### v1.0.0 (2024-01-15)
- Implementação inicial das APIs
- Sistema de carrinho completo
- Lista de desejos
- Sistema de cupons
- Cálculo de frete
- Chat de suporte
- Health check endpoint
- Rate limiting
- Tratamento de erros
- Documentação completa
