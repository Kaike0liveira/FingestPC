"""Smoke test para FingestPC.

Este script faz um fluxo básico: registra um usuário, faz login, adiciona despesas,
chama a API `/api/summary` e baixa o export Excel (`/export`).

Uso:
  python smoke_test.py --url http://127.0.0.1:5000

Execute o servidor Flask antes de rodar este script.
"""
import argparse
import time
import requests
import os


def main(base_url):
    s = requests.Session()
    ts = int(time.time())
    username = f'smoke_{ts}'
    password = 'SmokePass123!'
    email = f'{username}@example.com'

    print('1) Registrando usuário:', username)
    # get csrf token
    import re
    r = s.get(f'{base_url}/register')
    m = re.search(r'name="csrf_token" value="([^"]+)"', r.text)
    token = m.group(1) if m else None
    data = {'username': username, 'password': password, 'email': email}
    if token:
        data['csrf_token'] = token
    r = s.post(f'{base_url}/register', data=data)
    print('  register ->', r.status_code)

    print('2) Fazendo login')
    r = s.get(f'{base_url}/login')
    m = re.search(r'name="csrf_token" value="([^"]+)"', r.text)
    token = m.group(1) if m else None
    login_data = {'username': username, 'password': password}
    if token:
        login_data['csrf_token'] = token
    r = s.post(f'{base_url}/login', data=login_data)
    print('  login ->', r.status_code)
    if r.status_code != 200 and r.status_code != 302:
        print('  Falha no login. Resposta:', r.text[:400])
        return

    print('3) Adicionando despesas (3 entradas)')
    expenses = [
        {'amount': '25.50', 'category': 'food', 'date': ''},
        {'amount': '120.00', 'category': 'bills', 'date': ''},
        {'amount': '9.99', 'category': 'coffee', 'date': ''},
    ]
    # acquire csrf for add_expense
    rget = s.get(f'{base_url}/add_expense')
    m = re.search(r'name="csrf_token" value="([^"]+)"', rget.text)
    token = m.group(1) if m else None
    for e in expenses:
        d = dict(e)
        if token:
            d['csrf_token'] = token
        r = s.post(f'{base_url}/add_expense', data=d)
        print('  add_expense ->', r.status_code)

    print('4) Chamando /api/summary')
    r = s.get(f'{base_url}/api/summary')
    print('  api/summary ->', r.status_code)
    try:
        print('  JSON ->', r.json())
    except Exception:
        print('  Não retornou JSON. Conteúdo:', r.text[:400])

    print('5) Baixando export (Excel)')
    r = s.get(f'{base_url}/export')
    print('  export ->', r.status_code)
    if r.status_code == 200:
        fname = f'smoke_export_{username}.xlsx'
        with open(fname, 'wb') as f:
            f.write(r.content)
        print('  Salvo em', os.path.abspath(fname))
    else:
        print('  Falha ao exportar. Resposta curta:', r.text[:200])

    print('6) Verificando dashboard (GET)')
    r = s.get(f'{base_url}/dashboard')
    print('  dashboard ->', r.status_code)

    print('\nSmoke test concluído.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--url', default='http://127.0.0.1:5000', help='Base URL do app')
    args = p.parse_args()
    main(args.url.rstrip('/'))
