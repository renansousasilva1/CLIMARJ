from django.contrib import admin
from .models import Cidade

@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo_climatempo', 'link_precipitacao')
    search_fields = ('nome',)
