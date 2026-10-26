from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from .models import Categoria, Conta, Lancamento

class FinanceiroTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user("tesoureiro", password="senha-forte-123")
        self.user.user_permissions.set(Permission.objects.filter(content_type__app_label="financeiro"))
        self.conta=Conta.objects.get(nome="Caixa")
        self.conta.saldo_inicial=Decimal("100.00"); self.conta.save()
        self.entrada=Categoria.objects.create(nome="Mensalidade de teste", tipo="E")
        self.despesa=Categoria.objects.create(nome="Material de teste", tipo="D")
    def test_dashboard_exige_login(self): self.assertEqual(self.client.get(reverse("dashboard")).status_code, 302)
    def test_saldo_da_conta(self):
        Lancamento.objects.create(descricao="Contribuição", tipo="E", valor=50, data=date.today(), categoria=self.entrada, conta=self.conta, criado_por=self.user)
        Lancamento.objects.create(descricao="Corda", tipo="D", valor=20, data=date.today(), categoria=self.despesa, conta=self.conta, criado_por=self.user)
        self.assertEqual(self.conta.saldo_atual, Decimal("130.00"))
    def test_categoria_precisa_corresponder_ao_tipo(self):
        item=Lancamento(descricao="Inválido", tipo="D", valor=10, data=date.today(), categoria=self.entrada, conta=self.conta, criado_por=self.user)
        with self.assertRaises(ValidationError): item.full_clean()
    def test_cria_lancamento_pela_interface(self):
        self.client.force_login(self.user)
        r=self.client.post(reverse("lancamento-create"), {"descricao":"Mensalidade","tipo":"E","valor":"25.50","data":date.today(),"categoria":self.entrada.pk,"conta":self.conta.pk,"documento":"","observacoes":""})
        self.assertRedirects(r, reverse("lancamento-list")); self.assertEqual(Lancamento.objects.count(),1)
    def test_telas_principais_renderizam(self):
        self.client.force_login(self.user)
        for nome in ("dashboard", "lancamento-list", "cadastros", "lancamento-create", "conta-create", "categoria-create", "centro-create", "orcamento-list", "orcamento-create", "importar-ofx"):
            with self.subTest(nome=nome): self.assertEqual(self.client.get(reverse(nome)).status_code, 200)
    def test_importacao_ofx_evita_duplicidade(self):
        self.client.force_login(self.user)
        conteudo=b"<OFX><BANKTRANLIST><STMTTRN><TRNAMT>42.50<DTPOSTED>20261020<FITID>ABC123<MEMO>Doacao</STMTTRN></BANKTRANLIST></OFX>"
        dados={"conta":self.conta.pk,"categoria_entrada":self.entrada.pk,"categoria_despesa":self.despesa.pk,"arquivo":SimpleUploadedFile("extrato.ofx",conteudo)}
        self.client.post(reverse("importar-ofx"),dados)
        dados["arquivo"]=SimpleUploadedFile("extrato.ofx",conteudo)
        self.client.post(reverse("importar-ofx"),dados)
        self.assertEqual(Lancamento.objects.filter(identificador_bancario__isnull=False).count(),1)
    def test_perfil_consulta_nao_altera(self):
        leitor=get_user_model().objects.create_user("leitor",password="senha-forte-123")
        leitor.groups.add(Group.objects.get(name="Consulta")); self.client.force_login(leitor)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code,200)
        self.assertEqual(self.client.get(reverse("lancamento-create")).status_code,403)
    def test_exportacoes(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("exportar-excel")).status_code,200)
        self.assertEqual(self.client.get(reverse("exportar-pdf")).status_code,200)
    def test_superusuario_gerencia_usuarios(self):
        admin=get_user_model().objects.create_superuser("admin","admin@example.com","senha-admin-123")
        self.client.force_login(admin)
        self.assertEqual(self.client.get(reverse("usuario-list")).status_code,200)
        grupo=Group.objects.get(name="Consulta")
        resposta=self.client.post(reverse("usuario-create"),{"username":"novo","first_name":"Novo","last_name":"Usuário","email":"novo@example.com","groups":[grupo.pk],"password1":"senha-nova-123","password2":"senha-nova-123"})
        self.assertRedirects(resposta,reverse("usuario-list"))
        novo=get_user_model().objects.get(username="novo")
        self.assertTrue(novo.groups.filter(name="Consulta").exists())
    def test_usuario_comum_nao_acessa_gestao(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("usuario-list")).status_code,403)
