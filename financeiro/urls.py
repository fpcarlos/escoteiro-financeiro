from django.urls import path
from . import views

urlpatterns = [
 path("", views.DashboardView.as_view(), name="dashboard"),
 path("lancamentos/", views.LancamentoListView.as_view(), name="lancamento-list"),
 path("lancamentos/novo/", views.LancamentoCreateView.as_view(), name="lancamento-create"),
 path("lancamentos/<int:pk>/editar/", views.LancamentoUpdateView.as_view(), name="lancamento-update"),
 path("lancamentos/<int:pk>/excluir/", views.LancamentoDeleteView.as_view(), name="lancamento-delete"),
 path("cadastros/", views.CadastroListView.as_view(), name="cadastros"),
 path("contas/nova/", views.ContaCreateView.as_view(), name="conta-create"), path("contas/<int:pk>/editar/", views.ContaUpdateView.as_view(), name="conta-update"),
 path("categorias/nova/", views.CategoriaCreateView.as_view(), name="categoria-create"), path("categorias/<int:pk>/editar/", views.CategoriaUpdateView.as_view(), name="categoria-update")]
urlpatterns += [
 path("centros/nova/", views.CentroCustoCreateView.as_view(), name="centro-create"), path("centros/<int:pk>/editar/", views.CentroCustoUpdateView.as_view(), name="centro-update"),
 path("orcamentos/", views.OrcamentoListView.as_view(), name="orcamento-list"), path("orcamentos/novo/", views.OrcamentoCreateView.as_view(), name="orcamento-create"), path("orcamentos/<int:pk>/editar/", views.OrcamentoUpdateView.as_view(), name="orcamento-update"),
 path("importar-ofx/", views.ImportacaoOFXView.as_view(), name="importar-ofx"), path("relatorios/prestacao.xlsx", views.exportar_excel, name="exportar-excel"), path("relatorios/prestacao.pdf", views.exportar_pdf, name="exportar-pdf")]
urlpatterns += [path("usuarios/", views.UsuarioListView.as_view(), name="usuario-list"), path("usuarios/novo/", views.UsuarioCreateView.as_view(), name="usuario-create"), path("usuarios/<int:pk>/editar/", views.UsuarioUpdateView.as_view(), name="usuario-update"), path("usuarios/<int:pk>/senha/", views.UsuarioSenhaView.as_view(), name="usuario-senha")]
