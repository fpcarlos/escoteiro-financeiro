from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

class TipoLancamento(models.TextChoices):
    ENTRADA = "E", "Entrada"
    DESPESA = "D", "Despesa"

class Categoria(models.Model):
    nome = models.CharField(max_length=80)
    tipo = models.CharField(max_length=1, choices=TipoLancamento.choices)
    ativa = models.BooleanField(default=True)
    class Meta:
        ordering = ["tipo", "nome"]
        constraints = [models.UniqueConstraint(fields=["nome", "tipo"], name="categoria_nome_tipo_unico")]
    def __str__(self): return f"{self.nome} ({self.get_tipo_display()})"

class CentroCusto(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.CharField(max_length=200, blank=True)
    ativo = models.BooleanField(default=True)
    class Meta:
        ordering = ["nome"]
        verbose_name = "Centro de custo"
        verbose_name_plural = "Centros de custo"
    def __str__(self): return self.nome

class Conta(models.Model):
    class Tipo(models.TextChoices):
        CAIXA = "CAIXA", "Caixa"
        BANCO = "BANCO", "Conta bancária"
        POUPANCA = "POUPANCA", "Poupança"
        OUTRA = "OUTRA", "Outra"
    nome = models.CharField(max_length=80, unique=True)
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.BANCO)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ativa = models.BooleanField(default=True)
    class Meta: ordering = ["nome"]
    def __str__(self): return self.nome
    @property
    def saldo_atual(self):
        entradas = self.lancamentos.filter(tipo=TipoLancamento.ENTRADA).aggregate(total=models.Sum("valor"))["total"] or Decimal("0")
        despesas = self.lancamentos.filter(tipo=TipoLancamento.DESPESA).aggregate(total=models.Sum("valor"))["total"] or Decimal("0")
        return self.saldo_inicial + entradas - despesas

class Lancamento(models.Model):
    descricao = models.CharField(max_length=160)
    tipo = models.CharField(max_length=1, choices=TipoLancamento.choices)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField(verbose_name="Data do lançamento")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="lancamentos")
    conta = models.ForeignKey(Conta, on_delete=models.PROTECT, related_name="lancamentos")
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.PROTECT, related_name="lancamentos", null=True, blank=True)
    documento = models.CharField(max_length=60, blank=True, help_text="Recibo, nota fiscal ou referência")
    observacoes = models.TextField(blank=True)
    comprovante = models.FileField(upload_to="comprovantes/%Y/%m/", blank=True)
    identificador_bancario = models.CharField(max_length=120, blank=True, null=True, unique=True, editable=False)
    conciliado = models.BooleanField(default=False)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="lancamentos_criados")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-data", "-id"]
        indexes = [models.Index(fields=["data", "tipo"])]
    def __str__(self): return f"{self.descricao} — R$ {self.valor}"
    def clean(self):
        if self.valor is not None and self.valor <= 0: raise ValidationError({"valor": "O valor deve ser maior que zero."})
        if self.categoria_id and self.tipo and self.categoria.tipo != self.tipo: raise ValidationError({"categoria": "A categoria deve ser do mesmo tipo do lançamento."})

class Orcamento(models.Model):
    ano = models.PositiveSmallIntegerField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="orcamentos")
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.PROTECT, related_name="orcamentos", null=True, blank=True)
    valor_previsto = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        ordering = ["-ano", "categoria__nome"]
        constraints = [models.UniqueConstraint(fields=["ano", "categoria", "centro_custo"], name="orcamento_anual_unico")]
    def __str__(self): return f"{self.ano} · {self.categoria.nome}"
    @property
    def valor_realizado(self):
        filtros = {"data__year": self.ano, "categoria": self.categoria}
        if self.centro_custo_id: filtros["centro_custo"] = self.centro_custo
        return Lancamento.objects.filter(**filtros).aggregate(v=models.Sum("valor"))["v"] or Decimal("0")
    @property
    def percentual(self):
        return (self.valor_realizado / self.valor_previsto * 100) if self.valor_previsto else Decimal("0")
