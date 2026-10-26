from django.contrib import admin
from .models import Categoria, CentroCusto, Conta, Lancamento, Orcamento

@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = ("data", "descricao", "tipo", "valor", "categoria", "conta", "criado_por")
    list_filter = ("tipo", "data", "categoria", "conta")
    search_fields = ("descricao", "documento", "observacoes")
    date_hierarchy = "data"

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "ativa")
    list_filter = ("tipo", "ativa")

@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "saldo_inicial", "ativa")
    list_filter = ("tipo", "ativa")

admin.site.register(CentroCusto)
admin.site.register(Orcamento)
