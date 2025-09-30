from django.contrib import admin
from django.utils.html import format_html

from .models import SiteSettings, ContactMessage, Instructor, Gallery, BlogPost, Product, ProductCategory, ProductReview, Cart, CartItem, Order, OrderItem, Coupon, Wishlist, WishlistItem


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
	list_display = ("site_name", "contact_email", "updated_at")
	readonly_fields = ("created_at", "updated_at")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "category", "priority", "status", "created_at")
	list_filter = ("status", "category", "priority", "created_at")
	search_fields = ("name", "email", "subject", "message")
	readonly_fields = ("created_at", "updated_at", "ip_address", "user_agent")
	fieldsets = (
		("Informações do Remetente", {
			"fields": ("name", "email", "phone")
		}),
		("Mensagem", {
			"fields": ("subject", "message", "category", "priority")
		}),
		("Status e Resposta", {
			"fields": ("status", "response", "responded_by", "responded_at")
		}),
		("Metadados", {
			"fields": ("created_at", "updated_at", "ip_address", "user_agent"),
			"classes": ("collapse",)
		}),
	)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
	list_display = ("full_name", "experience_years", "is_active", "is_featured")
	list_filter = ("is_active", "is_featured", "created_at")
	search_fields = ("user__first_name", "user__last_name", "user__email")
	readonly_fields = ("created_at", "updated_at")


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
	list_display = ("title", "category", "is_featured", "order", "created_at")
	list_filter = ("category", "is_featured", "created_at")
	search_fields = ("title", "description")
	ordering = ("category", "order", "-created_at")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
	list_display = ("title", "author", "category", "status", "is_featured", "published_at")
	list_filter = ("status", "category", "is_featured", "created_at")
	search_fields = ("title", "content", "excerpt")
	prepopulated_fields = {"slug": ("title",)}
	readonly_fields = ("created_at", "updated_at", "view_count")


class ProductReviewInline(admin.TabularInline):
	model = ProductReview
	extra = 0
	readonly_fields = ("created_at",)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
	list_display = ("name", "is_active", "order", "product_count", "created_at")
	list_filter = ("is_active", "created_at")
	search_fields = ("name", "description")
	prepopulated_fields = {"slug": ("name",)}
	ordering = ("order", "name")
	
	def product_count(self, obj):
		return obj.products.count()
	product_count.short_description = "Produtos"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("name", "category", "price", "stock_quantity", "status", "is_featured", "is_bestseller", "created_at")
	list_filter = ("status", "category", "is_featured", "is_bestseller", "track_stock", "created_at")
	search_fields = ("name", "description", "short_description")
	prepopulated_fields = {"slug": ("name",)}
	readonly_fields = ("created_at", "updated_at", "view_count")
	inlines = [ProductReviewInline]
	
	fieldsets = (
		("Informações Básicas", {
			"fields": ("name", "slug", "description", "short_description", "category", "status")
		}),
		("Preços e Estoque", {
			"fields": ("price", "compare_price", "stock_quantity", "track_stock")
		}),
		("Imagens", {
			"fields": ("main_image", "images")
		}),
		("Atributos", {
			"fields": ("weight", "dimensions", "colors", "sizes")
		}),
		("SEO", {
			"fields": ("meta_title", "meta_description"),
			"classes": ("collapse",)
		}),
		("Destaque e Ordenação", {
			"fields": ("is_featured", "is_bestseller", "order")
		}),
		("Metadados", {
			"fields": ("created_at", "updated_at", "view_count"),
			"classes": ("collapse",)
		}),
	)
	
	def get_queryset(self, request):
		return super().get_queryset(request).select_related("category")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
	list_display = ("product", "name", "rating", "is_approved", "created_at")
	list_filter = ("rating", "is_approved", "created_at")
	search_fields = ("product__name", "name", "email", "title", "comment")
	readonly_fields = ("created_at",)
	
	def get_queryset(self, request):
		return super().get_queryset(request).select_related("product")


class CartItemInline(admin.TabularInline):
	model = CartItem
	extra = 0
	readonly_fields = ("created_at", "updated_at")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
	list_display = ("session_key", "total_items", "total_price", "created_at", "updated_at")
	list_filter = ("created_at", "updated_at")
	search_fields = ("session_key",)
	readonly_fields = ("created_at", "updated_at")
	inlines = [CartItemInline]
	
	def total_items(self, obj):
		return obj.total_items
	total_items.short_description = "Total de Itens"
	
	def total_price(self, obj):
		return f"R$ {obj.total_price:.2f}"
	total_price.short_description = "Total"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ("cart", "product", "quantity", "total_price", "created_at")
	list_filter = ("created_at", "updated_at")
	search_fields = ("product__name", "cart__session_key")
	readonly_fields = ("created_at", "updated_at")
	
	def total_price(self, obj):
		return f"R$ {obj.total_price:.2f}"
	total_price.short_description = "Total"
	
	def get_queryset(self, request):
		return super().get_queryset(request).select_related("cart", "product")


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	readonly_fields = ("total_price",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("order_number", "customer_name", "status", "payment_status", "total", "created_at")
	list_filter = ("status", "payment_status", "payment_method", "created_at")
	search_fields = ("order_number", "customer_name", "customer_email", "customer_phone")
	readonly_fields = ("order_number", "created_at", "updated_at")
	inlines = [OrderItemInline]
	
	fieldsets = (
		("Informações do Pedido", {
			"fields": ("order_number", "status", "payment_status", "created_at", "updated_at")
		}),
		("Informações do Cliente", {
			"fields": ("customer_name", "customer_email", "customer_phone")
		}),
		("Endereço de Entrega", {
			"fields": ("shipping_address", "shipping_city", "shipping_state", "shipping_zip_code")
		}),
		("Valores", {
			"fields": ("subtotal", "shipping_cost", "total")
		}),
		("Pagamento", {
			"fields": ("payment_method", "payment_reference")
		}),
		("Observações", {
			"fields": ("notes",)
		}),
	)
	
	def total(self, obj):
		return f"R$ {obj.total:.2f}"
	total.short_description = "Total"
	
	def get_queryset(self, request):
		return super().get_queryset(request).prefetch_related("items__product")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ("order", "product", "quantity", "price", "total_price")
	list_filter = ("order__status", "order__created_at")
	search_fields = ("order__order_number", "product__name")
	
	def total_price(self, obj):
		return f"R$ {obj.total_price:.2f}"
	total_price.short_description = "Total"
	
	def get_queryset(self, request):
		return super().get_queryset(request).select_related("order", "product")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
	list_display = ("code", "discount_type", "discount_value", "is_active", "valid_from", "valid_until", "used_count")
	list_filter = ("discount_type", "is_active", "valid_from", "valid_until")
	search_fields = ("code", "description")
	readonly_fields = ("used_count", "created_at")
	
	fieldsets = (
		("Informações Básicas", {
			"fields": ("code", "description", "is_active")
		}),
		("Desconto", {
			"fields": ("discount_type", "discount_value", "minimum_amount", "maximum_discount")
		}),
		("Limites", {
			"fields": ("usage_limit", "used_count")
		}),
		("Validade", {
			"fields": ("valid_from", "valid_until")
		}),
		("Metadados", {
			"fields": ("created_at",),
			"classes": ("collapse",)
		}),
	)


class WishlistItemInline(admin.TabularInline):
	model = WishlistItem
	extra = 0
	readonly_fields = ("created_at",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
	list_display = ("session_key", "total_items", "created_at", "updated_at")
	list_filter = ("created_at", "updated_at")
	search_fields = ("session_key",)
	readonly_fields = ("created_at", "updated_at")
	inlines = [WishlistItemInline]
	
	def total_items(self, obj):
		return obj.total_items
	total_items.short_description = "Total de Itens"


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
	list_display = ("wishlist", "product", "created_at")
	list_filter = ("created_at",)
	search_fields = ("product__name", "wishlist__session_key")
	readonly_fields = ("created_at",)
	
	def get_queryset(self, request):
		return super().get_queryset(request).select_related("wishlist", "product")
