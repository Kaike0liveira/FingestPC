# Fingest – Gestor Financeiro Inteligente

Projeto demo chamado **FingestPC** — um gestor financeiro simples com autenticação, painel com gráficos, previsão de gastos (Regressão Linear), exportação para Excel e painel administrativo.

## Funcionalidades
- Registro e login (primeiro usuário registrado vira `admin`).
- Sessões por cookies.
- Dashboard com gráficos (Chart.js).
- Previsão de gastos por mês usando `scikit-learn` (Linear Regression).
- Exportação de despesas para Excel (`pandas` + `openpyxl`).
- Adição de gastos, configurações de limite mensal e perfil com upload de foto.
- Painel admin em `/admin` para gestão de usuários.
- API simples `/api/summary` retornando `{ total: X, limit: Y }`.

## Estrutura do projeto

FingestPC/
│ app.py
│ requirements.txt
│ README.md
│ .gitignore
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_expense.html
│   ├── settings.html
│   ├── profile.html
│   └── admin_dashboard.html
│
└── static/
    ├── style.css
    └── uploads/   (deixar vazio)

## Instalação (Local - Windows PowerShell)

1. Crie e ative virtualenv:

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1
```

2. Instale dependências:

```powershell
pip install -r requirements.txt
```

3. (Opcional) criar `.env` com `SECRET_KEY`:

```text
SECRET_KEY=uma_chave_secreta_aqui
```

4. Rodar localmente:

```powershell
python app.py
```

O app iniciará em `http://127.0.0.1:5000`.

## Deploy (Linux) — Gunicorn + Nginx (resumo)

1. Em servidor Linux, criar venv e instalar dependências.
2. Usar Gunicorn para rodar: `gunicorn -w 4 -b 127.0.0.1:8000 app:app`.
3. Configurar Nginx como proxy reverso para o Gunicorn.
4. Ativar HTTPS com Certbot.

Exemplo de systemd (service):

```
[Unit]
Description=Gunicorn instance for Fingest

[Service]
User=www-data
WorkingDirectory=/path/to/FingestPC
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

## Banco de Dados

O projeto usa `sqlite` e cria `database.db` no diretório do projeto. Tabelas:

- `users` (id, username, password, email, role, photo)
- `expenses` (id, amount, category, date, user_id)
- `settings` (user_id, monthly_limit)

## Notas
- Foto de perfil salva em `static/uploads` com nome `user_ID.ext`.
- Primeiro usuário registrado vira administrador automaticamente.

## Testes automatizados

- Há um script de smoke test `smoke_test.py` que automatiza registro/login/adicionar despesas/export.
- Para rodar localmente:

```powershell
# numa janela: rodar o servidor
python app.py

# noutra janela: rodar smoke test
.\venv\Scripts\Activate.ps1
python smoke_test.py --url http://127.0.0.1:5000
```

## Integração Contínua

Um workflow do GitHub Actions (`.github/workflows/ci.yml`) foi adicionado. Ele instala dependências, inicia o servidor e executa o `smoke_test.py` em pushes e pull requests para `main`.

## Próximos passos sugeridos
- Melhorar validações e tratamento de erros.
- Adicionar testes automáticos.
- Subir para GitHub e configurar CI/CD.
