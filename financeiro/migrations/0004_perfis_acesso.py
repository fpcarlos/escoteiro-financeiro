from django.db import migrations


def criar_perfis(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    tipos = ContentType.objects.filter(app_label="financeiro")
    permissoes = Permission.objects.filter(content_type__in=tipos)
    tesouraria, _ = Group.objects.get_or_create(name="Tesouraria")
    diretoria, _ = Group.objects.get_or_create(name="Diretoria")
    consulta, _ = Group.objects.get_or_create(name="Consulta")
    tesouraria.permissions.set(permissoes)
    diretoria.permissions.set(permissoes.exclude(codename__startswith="delete_"))
    consulta.permissions.set(permissoes.filter(codename__startswith="view_"))


def remover_perfis(apps, schema_editor):
    apps.get_model("auth", "Group").objects.filter(name__in=["Tesouraria", "Diretoria", "Consulta"]).delete()


class Migration(migrations.Migration):
    dependencies = [("financeiro", "0003_auto_20261026_1918")]
    operations = [migrations.RunPython(criar_perfis, remover_perfis)]
