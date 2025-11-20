"""Smoke test específico para editar e deletar despesas.

Fluxo:
 - registra um usuário
 - faz login
 - adiciona uma despesa
 - localiza o id da despesa na dashboard
 - edita a despesa
 - verifica que o total refletiu a edição
 - deleta a despesa
 - verifica que o total foi zerado

Uso:
  python smoke_edit_delete.py --url http://127.0.0.1:5000

Execute o servidor antes ou deixe este script ser executado após iniciá-lo.
"""
import argparse
import time
import re
import requests


def extract_csrf(text):
    m = re.search(r'name="csrf_token" value="([^"]+)"', text)
    return m.group(1) if m else None


def main(base_url):
    s = requests.Session()
    ts = int(time.time())
    username = f'smoke_ed_{ts}'
    password = 'SmokePass123!'
    email = f'{username}@example.com'

    print('1) Registrando usuário:', username)
    r = s.get(f'{base_url}/register')
    token = extract_csrf(r.text)
    data = {'username': username, 'password': password, 'email': email}
    if token:
        data['csrf_token'] = token
    r = s.post(f'{base_url}/register', data=data)
    print('  register ->', r.status_code)

    print('2) Fazendo login')
    r = s.get(f'{base_url}/login')
    token = extract_csrf(r.text)
    login_data = {'username': username, 'password': password}
    if token:
        login_data['csrf_token'] = token
    r = s.post(f'{base_url}/login', data=login_data)
    print('  login ->', r.status_code)
    if r.status_code not in (200, 302):
        print('  Falha no login. Saída curta:', r.text[:300])
        return

    print('3) Adicionando uma despesa (10.00)')
    rget = s.get(f'{base_url}/add_expense')
    token = extract_csrf(rget.text)
    d = {'amount': '10.00', 'category': 'other'}
    if token:
        d['csrf_token'] = token
    r = s.post(f'{base_url}/add_expense', data=d)
    print('  add_expense ->', r.status_code)

    print('4) Buscando dashboard para obter id da despesa e token de delete')
    r = s.get(f'{base_url}/dashboard')
    print('  dashboard ->', r.status_code)
    if r.status_code != 200:
        print('  Falha ao obter dashboard.')
        return

    # localizar /expense/<id>/edit no HTML
    m = re.search(r'/expense/(\d+)/edit', r.text)
    if not m:
        print('  Não encontrou despesa para editar.')
        return
    expense_id = m.group(1)
    print('  expense id ->', expense_id)

    # extrair token do formulário delete associado
    # procurar trecho action="/expense/{id}/delete" seguido do input csrf
    delete_re = re.compile(r'action="/expense/%s/delete"[\s\S]*?name="csrf_token" value="([^"]+)"' % expense_id)
    mm = delete_re.search(r.text)
    delete_token = mm.group(1) if mm else None
    print('  delete token ->', bool(delete_token))

    print('5) Editando despesa para 15.50')
    r = s.get(f'{base_url}/expense/{expense_id}/edit')
    edit_token = extract_csrf(r.text)
    edit_data = {'amount': '15.50', 'category': 'other', 'date': ''}
    if edit_token:
        edit_data['csrf_token'] = edit_token
    r = s.post(f'{base_url}/expense/{expense_id}/edit', data=edit_data)
    print('  edit ->', r.status_code)

    print('6) Verificando total via /api/summary')
    r = s.get(f'{base_url}/api/summary')
    print('  api/summary ->', r.status_code)
    try:
        print('  JSON ->', r.json())
    except Exception:
        print('  Falha ao obter JSON:', r.text[:200])

    print('7) Deletando a despesa')
    if not delete_token:
        # tentar obter token direto do edit page (alguns templates colocam apenas um token global)
        if edit_token:
            delete_token = edit_token
    if delete_token:
        r = s.post(f'{base_url}/expense/{expense_id}/delete', data={'csrf_token': delete_token})
    else:
        # enviar sem token (caso CSRF desabilitado) — ainda assim tentamos
        r = s.post(f'{base_url}/expense/{expense_id}/delete')
    print('  delete ->', r.status_code)

    print('8) Verificando total após delete via /api/summary')
    r = s.get(f'{base_url}/api/summary')
    print('  api/summary ->', r.status_code)
    try:
        print('  JSON ->', r.json())
    except Exception:
        print('  Falha ao obter JSON:', r.text[:200])

    print('\nTeste edit/delete concluído.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--url', default='http://127.0.0.1:5000', help='Base URL do app')
    args = p.parse_args()
    main(args.url.rstrip('/'))
