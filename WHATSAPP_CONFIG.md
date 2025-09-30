# Configuração do WhatsApp para Notificações

## Como funciona

Quando alguém envia uma mensagem pelo formulário de contato do site, o sistema:

1. **Salva a mensagem** no banco de dados
2. **Envia um email** para o administrador (opcional)
3. **Cria um link do WhatsApp** com a mensagem formatada

## Configuração

### 1. Adicione seu número no arquivo `.env`

Edite o arquivo `.env` e adicione:

```bash
# WhatsApp - Configure com seu número no formato: 5521999999999
# Formato: código país (55) + DDD (21) + número (999999999)
ADMIN_WHATSAPP=5521989307826
```

**Importante:**
- Use o código do país (55 para Brasil)
- Inclua o DDD
- Não use espaços, hífens ou parênteses
- Exemplo: `5521989307826` para o número (21) 98930-7826

### 2. Reinicie o servidor

```bash
python manage.py runserver
```

## Como funciona no Django Admin

No painel administrativo Django (`/admin/`), você verá:

1. Acesse **Mensagens de Contato**
2. Clique em uma mensagem para ver os detalhes
3. Você verá um campo **URL WhatsApp** com um link
4. Clique no link ou copie e cole no navegador
5. O WhatsApp abrirá com a mensagem pré-formatada

## Formato da Mensagem

A mensagem enviada via WhatsApp terá este formato:

```
🔔 *Nova mensagem de contato ASBJJ*

👤 *Nome:* João Silva
📧 *E-mail:* joao@example.com
📱 *Telefone:* (21) 98765-4321
📋 *Categoria:* Aulas

💬 *Mensagem:*
Gostaria de saber mais sobre as aulas de Jiu-Jitsu.

⏰ Enviado em: 30/09/2025 às 19:45
```

## Opções Avançadas

### WhatsApp Business API

Para envio automático de mensagens (sem precisar clicar no link), você pode integrar com:

1. **Twilio WhatsApp API**
   - https://www.twilio.com/whatsapp
   - Requer conta Twilio
   - Permite envio automático

2. **WhatsApp Business API Oficial**
   - https://business.whatsapp.com/developers
   - Requer aprovação do Facebook
   - Melhor para grandes volumes

### Exemplo de integração com Twilio

```python
# settings.py
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN', default='')
TWILIO_WHATSAPP_FROM = env('TWILIO_WHATSAPP_FROM', default='')

# views.py
def send_whatsapp_notification(self, contact_message):
    from twilio.rest import Client
    
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN]):
        return
    
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    mensagem = f"""🔔 Nova mensagem de contato ASBJJ
    
Nome: {contact_message.name}
Email: {contact_message.email}
Mensagem: {contact_message.message}"""
    
    client.messages.create(
        from_=f'whatsapp:{settings.TWILIO_WHATSAPP_FROM}',
        to=f'whatsapp:{settings.ADMIN_WHATSAPP}',
        body=mensagem
    )
```

## Teste

1. Acesse o site: http://127.0.0.1:8001/contato/
2. Preencha o formulário de contato
3. Envie a mensagem
4. Acesse o admin: http://127.0.0.1:8001/admin/
5. Vá em **Core > Mensagens de Contato**
6. Clique na mensagem
7. Copie o link **URL WhatsApp**
8. Cole no navegador ou envie para o celular
9. O WhatsApp abrirá com a mensagem

## Troubleshooting

### O campo URL WhatsApp está vazio
- Verifique se `ADMIN_WHATSAPP` está configurado no `.env`
- Reinicie o servidor Django

### O link não abre no WhatsApp
- Verifique se o número está no formato correto (sem espaços ou caracteres especiais)
- Teste o link manualmente: `https://api.whatsapp.com/send?phone=5521989307826&text=teste`

### Quero envio automático
- Configure Twilio ou WhatsApp Business API (veja seção "Opções Avançadas")

## Recursos Adicionais

- [WhatsApp Click to Chat](https://faq.whatsapp.com/5913398998672934)
- [Twilio WhatsApp Quickstart](https://www.twilio.com/docs/whatsapp/quickstart/python)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
