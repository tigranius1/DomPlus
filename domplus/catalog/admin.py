from django.contrib import admin
from .models import Apartment, Favorite, ViewingRequest


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'district', 'price', 'area', 'rooms', 'floor', 'is_active')
    list_filter = ('district', 'is_active', 'rooms')
    search_fields = ('title', 'address', 'description')
    list_editable = ('is_active',)
    ordering = ('-created_at',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'session_key', 'created_at')
    list_filter = ('created_at',)


@admin.register(ViewingRequest)
class ViewingRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'apartment', 'preferred_date', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'phone', 'apartment__title')
    list_editable = ('is_processed',)