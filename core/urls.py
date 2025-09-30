from django.urls import path
from . import views
from . import chat_views

app_name = 'core'

urlpatterns = [
    # Páginas principais
    path('', views.HomeView.as_view(), name='index'),
    path('sobre/', views.AboutView.as_view(), name='about'),
    path('servicos/', views.ServicesView.as_view(), name='services'),
    path('contato/', views.ContactView.as_view(), name='contact'),
    path('galeria/', views.GalleryListView.as_view(), name='gallery'),
    # Blog removido
    path('inscricao/', views.EnrollmentApplicationView.as_view(), name='enrollment'),
    path('calendario/', views.CalendarView.as_view(), name='calendar'),
    path('loja/', views.ShopView.as_view(), name='shop'),
    path('loja/categoria/<slug:slug>/', views.ShopCategoryView.as_view(), name='shop_category'),
    path('produto/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Carrinho e Pedidos
    path('carrinho/', views.CartView.as_view(), name='cart'),
    path('carrinho/adicionar/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrinho/remover/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('carrinho/atualizar/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('carrinho/limpar/', views.clear_cart, name='clear_cart'),
    path('carrinho/total/', views.cart_total, name='cart_total'),
    
    # Checkout
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('pedido/sucesso/', views.OrderSuccessView.as_view(), name='order_success'),
    path('pedido/<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    
    # Lista de Desejos
    path('favoritos/', views.WishlistView.as_view(), name='wishlist'),
    path('favoritos/adicionar/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('favoritos/remover/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Cupons
    path('cupom/aplicar/', views.apply_coupon, name='apply_coupon'),
    path('cupom/remover/', views.remove_coupon, name='remove_coupon'),
    
    # Frete
    path('frete/calcular/', views.calculate_shipping, name='calculate_shipping'),
    
    # Área do Cliente
    path('area-cliente/', views.CustomerAreaView.as_view(), name='customer_area'),
    
    # Relatórios (Admin)
    path('relatorios/vendas/', views.SalesReportView.as_view(), name='sales_report'),
    
    # Pagamento
    path('pagamento/<int:order_id>/', views.PaymentView.as_view(), name='payment'),
    path('webhook/mercadopago/', views.mercado_pago_webhook, name='mercado_pago_webhook'),
    path('pagamento/sucesso/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('pagamento/erro/', views.PaymentErrorView.as_view(), name='payment_error'),
    path('pagamento/pendente/', views.PaymentPendingView.as_view(), name='payment_pending'),
    
    # Chat de Suporte
    path('suporte/', chat_views.ChatSupportView.as_view(), name='chat_support'),
    path('chat/start/', chat_views.start_chat, name='start_chat'),
    path('chat/send/', chat_views.send_message, name='send_message'),
    path('chat/messages/<int:chat_id>/', chat_views.get_messages, name='get_messages'),
    path('chat/status/<int:chat_id>/', chat_views.chat_status, name='chat_status'),
    path('healthz', views.healthz, name='healthz'),
    
    # URLs antigas para compatibilidade
    path('sobre/', views.sobre, name='sobre'),
    path('servicos/', views.servicos, name='servicos'),
    path('contato/', views.contato, name='contato'),
]


