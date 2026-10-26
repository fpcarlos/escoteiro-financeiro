from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def sincronizar_perfis(sender, **kwargs):
    if sender.name != "financeiro": return
    permissoes = Permission.objects.filter(content_type__app_label="financeiro")
    regras = {
        "Tesouraria": permissoes,
        "Diretoria": permissoes.exclude(codename__startswith="delete_"),
        "Consulta": permissoes.filter(codename__startswith="view_"),
    }
    for nome, conjunto in regras.items():
        grupo, _ = Group.objects.get_or_create(name=nome)
        grupo.permissions.set(conjunto)
