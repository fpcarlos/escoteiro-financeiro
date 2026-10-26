from django.db import migrations


def criar_dados_iniciais(apps, schema_editor):
    Conta = apps.get_model("financeiro", "Conta")
    Categoria = apps.get_model("financeiro", "Categoria")
    Conta.objects.get_or_create(nome="Caixa", defaults={"tipo": "CAIXA", "saldo_inicial": 0, "ativa": True})
    categorias = {
        "E": ["Mensalidades", "Doações", "Eventos e campanhas", "Outras entradas"],
        "D": ["Materiais", "Alimentação", "Transporte", "Manutenção", "Taxas e tarifas", "Outras despesas"],
    }
    for tipo, nomes in categorias.items():
        for nome in nomes:
            Categoria.objects.get_or_create(nome=nome, tipo=tipo, defaults={"ativa": True})


def remover_dados_iniciais(apps, schema_editor):
    Categoria = apps.get_model("financeiro", "Categoria")
    Categoria.objects.filter(nome__in=["Mensalidades", "Doações", "Eventos e campanhas", "Outras entradas", "Materiais", "Alimentação", "Transporte", "Manutenção", "Taxas e tarifas", "Outras despesas"]).delete()


class Migration(migrations.Migration):
    dependencies = [("financeiro", "0001_initial")]
    operations = [migrations.RunPython(criar_dados_iniciais, remover_dados_iniciais)]
