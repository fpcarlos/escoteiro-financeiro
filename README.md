# Financeiro — 17º PB Grupo Escoteiro do Ar Santos Dumont

Sistema Django para controle de entradas, despesas, contas e categorias do grupo.

## Como executar

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`. Cadastros administrativos também ficam em
`http://127.0.0.1:8000/admin/`.

## Funcionalidades

- painel mensal com saldo, entradas, despesas e lançamentos recentes;
- contas (caixa, banco, poupança e outros);
- categorias separadas por entrada e despesa;
- lançamentos com competência, documento e observações;
- busca e filtros por período, tipo, conta e categoria;
- autenticação obrigatória e trilha de criação/alteração;
- administração Django e testes automatizados.

## Recursos da versão 2

- upload de comprovantes em cada lançamento;
- centros de custo para ramos, eventos e projetos;
- orçamento anual com comparação entre previsto e realizado;
- importação e conciliação de extratos OFX, com bloqueio de duplicidades;
- prestação de contas em PDF e Excel, respeitando o período filtrado;
- perfis `Tesouraria`, `Diretoria` e `Consulta`.
- área administrativa própria para criar, editar, ativar e definir senhas de usuários.

Os perfis podem ser atribuídos pela opção **Usuários** do próprio sistema. Tesouraria
possui acesso completo, Diretoria pode incluir e editar sem excluir, e Consulta
tem acesso somente para leitura.

A gestão de usuários é inicialmente acessível ao superusuário criado com
`python manage.py createsuperuser`. Outros gestores podem receber as permissões
de usuários do Django caso seja necessário delegar essa administração.

## Próximas evoluções possíveis

- tela assistida de conciliação para vincular movimentos bancários manualmente;
- aprovação em duas etapas para pagamentos;
- notificações de orçamento excedido;
- backups automáticos e implantação em produção.
