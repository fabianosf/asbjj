"""
Serviço de pagamento com Mercado Pago
"""
import os
from decimal import Decimal
from django.conf import settings
from mercadopago import SDK


class MercadoPagoService:
    """Serviço para integração com Mercado Pago"""
    
    def __init__(self):
        # Usar credenciais do ambiente ou valores padrão para desenvolvimento
        self.access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', 'TEST-1234567890')
        self.sdk = SDK(self.access_token)
    
    def create_preference(self, order):
        """Cria uma preferência de pagamento no Mercado Pago"""
        try:
            # Preparar itens do pedido
            items = []
            for item in order.items.all():
                items.append({
                    "title": item.product.name,
                    "quantity": item.quantity,
                    "unit_price": float(item.price),
                    "currency_id": "BRL"
                })
            
            # Dados do comprador
            payer = {
                "name": order.customer_name,
                "email": order.customer_email,
                "phone": {
                    "number": order.customer_phone
                },
                "address": {
                    "street_name": order.shipping_address,
                    "city_name": order.shipping_city,
                    "state_name": order.shipping_state,
                    "zip_code": order.shipping_zip_code
                }
            }
            
            # Configuração da preferência
            preference_data = {
                "items": items,
                "payer": payer,
                "back_urls": {
                    "success": f"{settings.SITE_URL}/pedido/sucesso/",
                    "failure": f"{settings.SITE_URL}/pedido/erro/",
                    "pending": f"{settings.SITE_URL}/pedido/pendente/"
                },
                "auto_return": "approved",
                "external_reference": str(order.id),
                "notification_url": f"{settings.SITE_URL}/webhook/mercadopago/",
                "statement_descriptor": "ASBJJ",
                "metadata": {
                    "order_id": order.id,
                    "order_number": order.order_number
                }
            }
            
            # Criar preferência
            preference = self.sdk.preference().create(preference_data)
            
            if preference["status"] == 201:
                return {
                    "success": True,
                    "preference_id": preference["response"]["id"],
                    "init_point": preference["response"]["init_point"],
                    "sandbox_init_point": preference["response"]["sandbox_init_point"]
                }
            else:
                return {
                    "success": False,
                    "error": "Erro ao criar preferência no Mercado Pago"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}"
            }
    
    def get_payment_info(self, payment_id):
        """Obtém informações de um pagamento"""
        try:
            payment = self.sdk.payment().get(payment_id)
            
            if payment["status"] == 200:
                return {
                    "success": True,
                    "payment": payment["response"]
                }
            else:
                return {
                    "success": False,
                    "error": "Pagamento não encontrado"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao buscar pagamento: {str(e)}"
            }
    
    def process_webhook(self, data):
        """Processa webhook do Mercado Pago"""
        try:
            if data.get("type") == "payment":
                payment_id = data.get("data", {}).get("id")
                
                if payment_id:
                    payment_info = self.get_payment_info(payment_id)
                    
                    if payment_info["success"]:
                        payment = payment_info["payment"]
                        external_reference = payment.get("external_reference")
                        
                        if external_reference:
                            # Atualizar status do pedido
                            from .models import Order
                            
                            try:
                                order = Order.objects.get(id=external_reference)
                                
                                # Mapear status do Mercado Pago para status do pedido
                                status_mapping = {
                                    "approved": "paid",
                                    "pending": "pending",
                                    "rejected": "failed",
                                    "cancelled": "failed",
                                    "refunded": "refunded"
                                }
                                
                                payment_status = status_mapping.get(
                                    payment.get("status"), 
                                    "pending"
                                )
                                
                                order.payment_status = payment_status
                                order.payment_reference = payment_id
                                order.save()
                                
                                return {
                                    "success": True,
                                    "message": f"Pedido {order.order_number} atualizado"
                                }
                                
                            except Order.DoesNotExist:
                                return {
                                    "success": False,
                                    "error": "Pedido não encontrado"
                                }
            
            return {
                "success": False,
                "error": "Webhook não processado"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar webhook: {str(e)}"
            }


# Instância global do serviço
mercado_pago_service = MercadoPagoService()
