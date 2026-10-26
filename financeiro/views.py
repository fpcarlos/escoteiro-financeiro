from datetime import date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView
from .forms import CategoriaForm, CentroCustoForm, ContaForm, ImportacaoOFXForm, LancamentoForm, OrcamentoForm, UsuarioCriacaoForm, UsuarioEdicaoForm, UsuarioSenhaForm
from .models import Categoria, CentroCusto, Conta, Lancamento, Orcamento, TipoLancamento
from .services import importar_ofx, relatorio_pdf, relatorio_xlsx

class FinanceWriteMixin(PermissionRequiredMixin):
    raise_exception = True

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "financeiro/dashboard.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = date.today(); mes = self.request.GET.get("mes", hoje.strftime("%Y-%m"))
        try: ano, numero_mes = (int(parte) for parte in mes.split("-"))
        except (TypeError, ValueError): ano, numero_mes, mes = hoje.year, hoje.month, hoje.strftime("%Y-%m")
        qs = Lancamento.objects.filter(data__year=ano, data__month=numero_mes)
        entradas = qs.filter(tipo="E").aggregate(v=Sum("valor"))["v"] or Decimal("0")
        despesas = qs.filter(tipo="D").aggregate(v=Sum("valor"))["v"] or Decimal("0")
        saldo = sum((c.saldo_atual for c in Conta.objects.filter(ativa=True)), Decimal("0"))
        context.update(mes=mes, entradas=entradas, despesas=despesas, resultado=entradas-despesas, saldo_geral=saldo, recentes=Lancamento.objects.select_related("categoria", "conta")[:8])
        return context

class LancamentoListView(LoginRequiredMixin, ListView):
    model = Lancamento; paginate_by = 20; context_object_name = "lancamentos"
    def get_queryset(self):
        qs = super().get_queryset().select_related("categoria", "conta", "criado_por")
        busca = self.request.GET.get("q", "").strip()
        if busca: qs = qs.filter(Q(descricao__icontains=busca) | Q(documento__icontains=busca))
        for campo in ("tipo", "conta", "categoria"):
            valor = self.request.GET.get(campo)
            if valor: qs = qs.filter(**{campo if campo == "tipo" else f"{campo}_id": valor})
        if self.request.GET.get("inicio"): qs = qs.filter(data__gte=self.request.GET["inicio"])
        if self.request.GET.get("fim"): qs = qs.filter(data__lte=self.request.GET["fim"])
        return qs
    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c.update(contas=Conta.objects.filter(ativa=True), categorias=Categoria.objects.filter(ativa=True), tipos=TipoLancamento.choices, filtros=self.request.GET)
        return c

class AuthorFormMixin:
    def form_valid(self, form):
        if hasattr(form.instance, "criado_por_id") and not form.instance.criado_por_id: form.instance.criado_por = self.request.user
        messages.success(self.request, "Registro salvo com sucesso.")
        return super().form_valid(form)

class LancamentoCreateView(LoginRequiredMixin, FinanceWriteMixin, AuthorFormMixin, CreateView):
    permission_required = "financeiro.add_lancamento"
    model = Lancamento; form_class = LancamentoForm; success_url = reverse_lazy("lancamento-list")
class LancamentoUpdateView(LoginRequiredMixin, FinanceWriteMixin, AuthorFormMixin, UpdateView):
    permission_required = "financeiro.change_lancamento"
    model = Lancamento; form_class = LancamentoForm; success_url = reverse_lazy("lancamento-list")
class LancamentoDeleteView(LoginRequiredMixin, FinanceWriteMixin, DeleteView):
    permission_required = "financeiro.delete_lancamento"
    model = Lancamento; success_url = reverse_lazy("lancamento-list")
    def form_valid(self, form): messages.success(self.request, "Lançamento excluído."); return super().form_valid(form)
class CadastroListView(LoginRequiredMixin, TemplateView):
    template_name = "financeiro/cadastros.html"
    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs); c.update(contas=Conta.objects.all(), categorias=Categoria.objects.all(), centros=CentroCusto.objects.all()); return c
class BaseCadastroCreate(LoginRequiredMixin, FinanceWriteMixin, AuthorFormMixin, CreateView):
    success_url = reverse_lazy("cadastros")
    def get_permission_required(self): return (f"financeiro.add_{self.model._meta.model_name}",)
class BaseCadastroUpdate(LoginRequiredMixin, FinanceWriteMixin, AuthorFormMixin, UpdateView):
    success_url = reverse_lazy("cadastros")
    def get_permission_required(self): return (f"financeiro.change_{self.model._meta.model_name}",)
class ContaCreateView(BaseCadastroCreate): model, form_class = Conta, ContaForm
class ContaUpdateView(BaseCadastroUpdate): model, form_class = Conta, ContaForm
class CategoriaCreateView(BaseCadastroCreate): model, form_class = Categoria, CategoriaForm
class CategoriaUpdateView(BaseCadastroUpdate): model, form_class = Categoria, CategoriaForm
class CentroCustoCreateView(BaseCadastroCreate): model, form_class = CentroCusto, CentroCustoForm
class CentroCustoUpdateView(BaseCadastroUpdate): model, form_class = CentroCusto, CentroCustoForm

class OrcamentoListView(LoginRequiredMixin, ListView):
    model = Orcamento; context_object_name = "orcamentos"
    def get_queryset(self):
        try: ano = int(self.request.GET.get("ano", date.today().year))
        except (TypeError, ValueError): ano = date.today().year
        return Orcamento.objects.filter(ano=ano).select_related("categoria", "centro_custo")
    def get_context_data(self, **kwargs):
        c=super().get_context_data(**kwargs); c["ano"]=self.request.GET.get("ano", date.today().year); return c
class OrcamentoCreateView(LoginRequiredMixin, FinanceWriteMixin, AuthorFormMixin, CreateView):
    model=Orcamento; form_class=OrcamentoForm; permission_required="financeiro.add_orcamento"; success_url=reverse_lazy("orcamento-list")
class OrcamentoUpdateView(LoginRequiredMixin, FinanceWriteMixin, AuthorFormMixin, UpdateView):
    model=Orcamento; form_class=OrcamentoForm; permission_required="financeiro.change_orcamento"; success_url=reverse_lazy("orcamento-list")

class ImportacaoOFXView(LoginRequiredMixin, FinanceWriteMixin, TemplateView):
    template_name="financeiro/importar_ofx.html"; permission_required="financeiro.add_lancamento"
    def get_context_data(self, **kwargs): c=super().get_context_data(**kwargs); c["form"]=kwargs.get("form", ImportacaoOFXForm()); return c
    def post(self, request):
        form=ImportacaoOFXForm(request.POST, request.FILES)
        if form.is_valid():
            criados, ignorados=importar_ofx(form.cleaned_data["arquivo"], form.cleaned_data["conta"], form.cleaned_data["categoria_entrada"], form.cleaned_data["categoria_despesa"], request.user, form.cleaned_data["centro_custo"])
            messages.success(request, f"Importação concluída: {criados} lançamentos criados e {ignorados} duplicados ignorados.")
            return redirect("lancamento-list")
        return self.render_to_response(self.get_context_data(form=form))

def _lancamentos_relatorio(request):
    qs=Lancamento.objects.select_related("categoria","conta","centro_custo").all()
    if request.GET.get("inicio"): qs=qs.filter(data__gte=request.GET["inicio"])
    if request.GET.get("fim"): qs=qs.filter(data__lte=request.GET["fim"])
    if request.GET.get("centro_custo"): qs=qs.filter(centro_custo_id=request.GET["centro_custo"])
    return qs.order_by("data","id")
def exportar_excel(request):
    if not request.user.is_authenticated: return redirect("login")
    response=HttpResponse(relatorio_xlsx(_lancamentos_relatorio(request)), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"]='attachment; filename="prestacao-de-contas.xlsx"'; return response
def exportar_pdf(request):
    if not request.user.is_authenticated: return redirect("login")
    response=HttpResponse(relatorio_pdf(_lancamentos_relatorio(request), "Prestação de contas — 17º PB Santos Dumont"), content_type="application/pdf")
    response["Content-Disposition"]='attachment; filename="prestacao-de-contas.pdf"'; return response

class UsuarioListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model=get_user_model(); template_name="financeiro/usuario_list.html"; context_object_name="usuarios"; permission_required="auth.view_user"; raise_exception=True
    def get_queryset(self): return super().get_queryset().prefetch_related("groups").order_by("first_name","username")
class UsuarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model=get_user_model(); form_class=UsuarioCriacaoForm; template_name="financeiro/usuario_form.html"; permission_required="auth.add_user"; raise_exception=True; success_url=reverse_lazy("usuario-list")
    def form_valid(self, form): messages.success(self.request,"Usuário criado com sucesso."); return super().form_valid(form)
class UsuarioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model=get_user_model(); form_class=UsuarioEdicaoForm; template_name="financeiro/usuario_form.html"; permission_required="auth.change_user"; raise_exception=True; success_url=reverse_lazy("usuario-list")
    def get_queryset(self):
        qs=super().get_queryset()
        return qs if self.request.user.is_superuser else qs.filter(is_superuser=False)
    def form_valid(self, form):
        if form.instance == self.request.user and not form.cleaned_data.get("is_active"):
            form.add_error("is_active","Você não pode desativar o próprio usuário."); return self.form_invalid(form)
        messages.success(self.request,"Usuário atualizado com sucesso."); return super().form_valid(form)
class UsuarioSenhaView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name="financeiro/usuario_senha.html"; permission_required="auth.change_user"; raise_exception=True
    def get_usuario(self):
        qs=get_user_model().objects.all()
        if not self.request.user.is_superuser: qs=qs.filter(is_superuser=False)
        from django.shortcuts import get_object_or_404
        return get_object_or_404(qs, pk=self.kwargs["pk"])
    def get_context_data(self, **kwargs):
        c=super().get_context_data(**kwargs); c["object"]=self.get_usuario(); c["form"]=kwargs.get("form", UsuarioSenhaForm(self.get_usuario())); return c
    def post(self, request, *args, **kwargs):
        usuario=self.get_usuario(); form=UsuarioSenhaForm(usuario, request.POST)
        if form.is_valid(): form.save(); messages.success(request,"Senha alterada com sucesso."); return redirect("usuario-list")
        return self.render_to_response(self.get_context_data(form=form))
