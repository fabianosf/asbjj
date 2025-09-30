# 🌍 Configuração de DNS - ASBJJ

## Informações do Servidor

- **IP do Servidor:** 92.113.33.16
- **Domínio:** asbjj.com.br
- **Subdomínio:** www.asbjj.com.br

## Configuração no Registro.br

Acesse o painel do **Registro.br** e configure os seguintes registros DNS:

### 1. Registro A (Principal)

```
Tipo: A
Nome: @
Dados: 92.113.33.16
TTL: 3600
```

Este registro faz com que `asbjj.com.br` aponte para o servidor.

### 2. Registro CNAME (WWW)

```
Tipo: CNAME
Nome: www
Dados: asbjj.com.br.
TTL: 3600
```

Este registro faz com que `www.asbjj.com.br` redirecione para `asbjj.com.br`.

### 3. Registro MX (Email - Opcional)

Se quiser usar email @asbjj.com.br:

```
Tipo: MX
Nome: @
Prioridade: 10
Dados: mail.asbjj.com.br.
TTL: 3600
```

## Verificação de DNS

Após configurar, aguarde a propagação do DNS (pode levar de 5 minutos a 48 horas).

### Comandos para verificar:

```bash
# Verificar registro A
nslookup asbjj.com.br

# Verificar registro CNAME
nslookup www.asbjj.com.br

# Teste completo
dig asbjj.com.br +short
dig www.asbjj.com.br +short
```

### Ferramentas Online:

- https://dnschecker.org/ - Verificar propagação global
- https://mxtoolbox.com/ - Verificar registros MX e DNS
- https://www.whatsmydns.net/ - Verificar propagação mundial

## Configuração de SSL após DNS

Quando o DNS estiver propagado, execute no servidor:

```bash
ssh fabianosf@92.113.33.16

# Instalar certificado SSL
sudo certbot --nginx -d asbjj.com.br -d www.asbjj.com.br

# Responda as perguntas:
# Email: seu_email@gmail.com
# Aceite os termos: (Y)
# Compartilhar email: (N)
# Redirect HTTP para HTTPS: (2)
```

### Renovação Automática do SSL

O Certbot configura renovação automática. Para testar:

```bash
# Testar renovação
sudo certbot renew --dry-run

# Verificar timer de renovação
sudo systemctl status certbot.timer
```

## Configuração Adicional

### Atualizar .env no Servidor

Após configurar SSL, atualize o arquivo `.env`:

```bash
ssh fabianosf@92.113.33.16
cd /var/www/asbjj
nano .env
```

Altere:

```bash
SITE_URL=https://asbjj.com.br
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

Reinicie a aplicação:

```bash
sudo supervisorctl restart asbjj:*
```

## Subdomínios Adicionais (Opcional)

Se quiser criar subdomínios como `loja.asbjj.com.br` ou `admin.asbjj.com.br`:

```
Tipo: CNAME
Nome: loja
Dados: asbjj.com.br.
TTL: 3600

Tipo: CNAME
Nome: admin
Dados: asbjj.com.br.
TTL: 3600
```

Atualize o Nginx e SSL:

```bash
sudo certbot --nginx -d asbjj.com.br -d www.asbjj.com.br -d loja.asbjj.com.br -d admin.asbjj.com.br
```

## Troubleshooting

### DNS não propaga

1. Limpe cache DNS local:
```bash
# Linux
sudo systemd-resolve --flush-caches

# Windows
ipconfig /flushdns

# Mac
sudo dscacheutil -flushcache
```

2. Use DNS público:
```bash
# Google DNS
8.8.8.8
8.8.4.4

# Cloudflare DNS
1.1.1.1
1.0.0.1
```

### Certificado SSL não instala

Verifique se:
- DNS está propagado
- Portas 80 e 443 estão abertas no firewall
- Nginx está respondendo na porta 80

```bash
# Verificar portas
sudo netstat -tlnp | grep -E ':(80|443)'

# Testar Nginx
curl -I http://asbjj.com.br
```

## Firewall (Importante!)

Certifique-se de que as portas estão abertas:

```bash
# UFW (Ubuntu Firewall)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
sudo ufw status
```

## CDN (Opcional - Cloudflare)

Para melhor performance global, use Cloudflare:

1. Acesse https://www.cloudflare.com/
2. Adicione o domínio asbjj.com.br
3. Altere os nameservers no Registro.br para os da Cloudflare
4. Configure SSL/TLS mode: "Full (strict)"
5. Ative cache e otimizações

## Status Atual

- ✅ Servidor configurado: 92.113.33.16
- ✅ Site acessível via IP: http://92.113.33.16
- ⏳ DNS: Aguardando configuração no Registro.br
- ⏳ SSL: Aguardando propagação do DNS

## Próximos Passos

1. **Configurar DNS** no Registro.br (você precisa fazer)
2. **Aguardar propagação** (5min a 48h)
3. **Instalar SSL** com certbot (executar comando acima)
4. **Atualizar .env** com HTTPS
5. **Testar site** em https://asbjj.com.br

## Suporte

Se precisar de ajuda, verifique:
- https://registro.br/
- https://certbot.eff.org/
- https://www.cloudflare.com/
