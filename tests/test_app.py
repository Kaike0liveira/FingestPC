import os
import tempfile
import sqlite3
import pytest

# set DB path before importing app
tmpfd, tmpdb = tempfile.mkstemp()
os.close(tmpfd)
os.environ['FINGEST_DB_PATH'] = tmpdb

from app import app, init_db

@pytest.fixture(scope='module')
def client():
    # disable CSRF for tests
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    init_db()
    with app.test_client() as c:
        yield c


def test_register_login_add_edit_delete(client):
    # register
    rv = client.post('/register', data={'username': 'testuser', 'password': 'TestPass123', 'email': 't@test.local'}, follow_redirects=True)
    assert b'Registrado' in rv.data or rv.status_code in (200, 302)

    # login
    rv = client.post('/login', data={'username': 'testuser', 'password': 'TestPass123'}, follow_redirects=True)
    assert b'Bem-vindo' in rv.data or rv.status_code in (200, 302)

    # add expense
    rv = client.post('/add_expense', data={'amount': '10.00', 'category': 'other'}, follow_redirects=True)
    assert b'Gasto adicionado' in rv.data or rv.status_code in (200, 302)

    # check total
    rv = client.get('/api/summary')
    assert rv.status_code == 200
    j = rv.get_json()
    assert j['total'] == 10.0

    # find expense id
    conn = sqlite3.connect(tmpdb)
    cur = conn.cursor()
    cur.execute('SELECT id FROM expenses WHERE user_id = (SELECT id FROM users WHERE username = ?) LIMIT 1', ('testuser',))
    row = cur.fetchone()
    assert row is not None
    exp_id = row[0]
    conn.close()

    # edit expense
    rv = client.post(f'/expense/{exp_id}/edit', data={'amount': '15.50', 'category': 'other'}, follow_redirects=True)
    assert rv.status_code in (200, 302)

    rv = client.get('/api/summary')
    j = rv.get_json()
    assert j['total'] == 15.5

    # delete
    rv = client.post(f'/expense/{exp_id}/delete', follow_redirects=True)
    assert rv.status_code in (200, 302)

    rv = client.get('/api/summary')
    j = rv.get_json()
    assert j['total'] == 0.0
