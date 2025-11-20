import os
import threading
import time
import webbrowser

from app import app, init_db

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # ensure DB path is set to project DB by default
    os.environ.setdefault('FINGEST_DB_PATH', os.path.join(BASE_DIR, 'database.db'))
    # create uploads folder
    os.makedirs(os.path.join(BASE_DIR, 'static', 'uploads'), exist_ok=True)
    init_db()

    def open_browser(url):
        time.sleep(1.2)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    url = 'http://127.0.0.1:5000'
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()
    # run flask app
    app.run(host='127.0.0.1', port=5000)
