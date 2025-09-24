from django.contrib import admin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
	list_display = ("site_name", "contact_email", "updated_at")
	readonly_fields = ("created_at", "updated_at")
