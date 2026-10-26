from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.contrib.auth.models import Group
from .models import Categoria, CentroCusto, Conta, Lancamento, Orcamento, TipoLancamento

class DateInput(forms.DateInput): input_type = "date"

class LancamentoForm(forms.ModelForm):
    class Meta:
        model = Lancamento
        exclude = ["criado_por"]
        widgets = {"data": DateInput(), "observacoes": forms.Textarea(attrs={"rows": 3})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tipo = self.data.get("tipo") or getattr(self.instance, "tipo", None)
        categorias = Categoria.objects.filter(ativa=True)
        if tipo in TipoLancamento.values: categorias = categorias.filter(tipo=tipo)
        self.fields["categoria"].queryset = categorias
        self.fields["conta"].queryset = Conta.objects.filter(ativa=True)

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "tipo", "ativa"]

class ContaForm(forms.ModelForm):
    class Meta:
        model = Conta
        fields = ["nome", "tipo", "saldo_inicial", "ativa"]

class CentroCustoForm(forms.ModelForm):
    class Meta:
        model = CentroCusto
        fields = ["nome", "descricao", "ativo"]

class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ["ano", "categoria", "centro_custo", "valor_previsto"]

class ImportacaoOFXForm(forms.Form):
    conta = forms.ModelChoiceField(queryset=Conta.objects.filter(ativa=True))
    categoria_entrada = forms.ModelChoiceField(queryset=Categoria.objects.filter(tipo="E", ativa=True), label="Categoria para entradas")
    categoria_despesa = forms.ModelChoiceField(queryset=Categoria.objects.filter(tipo="D", ativa=True), label="Categoria para despesas")
    centro_custo = forms.ModelChoiceField(queryset=CentroCusto.objects.filter(ativo=True), required=False)
    arquivo = forms.FileField(help_text="Arquivo OFX fornecido pelo banco")

class UsuarioCriacaoForm(UserCreationForm):
    first_name = forms.CharField(label="Nome")
    last_name = forms.CharField(label="Sobrenome")
    email = forms.EmailField(label="E-mail")
    groups = forms.ModelMultipleChoiceField(label="Perfis de acesso", queryset=Group.objects.filter(name__in=["Tesouraria", "Diretoria", "Consulta"]), widget=forms.CheckboxSelectMultiple)
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email", "groups", "password1", "password2")
    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            usuario.groups.set(self.cleaned_data["groups"])
        return usuario

class UsuarioEdicaoForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(label="Perfis de acesso", queryset=Group.objects.filter(name__in=["Tesouraria", "Diretoria", "Consulta"]), widget=forms.CheckboxSelectMultiple, required=False)
    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email", "groups", "is_active")

class UsuarioSenhaForm(SetPasswordForm):
    pass
