from django.contrib import admin
from .models import *

class ArgumentInline(admin.TabularInline):
    model = Argument
    extra = 1

class SourceInline(admin.TabularInline):
    model = Source
    extra = 1

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'topic', 'visibility', 'created_at']
    list_filter = ['topic', 'visibility']
    search_fields = ['title', 'hypothesis']
    inlines = [ArgumentInline]

@admin.register(Argument)
class ArgumentAdmin(admin.ModelAdmin):
    list_display = ['summary', 'card', 'type']
    list_filter = ['type']
    inlines = [SourceInline]