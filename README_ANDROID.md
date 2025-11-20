Fingest - Android & PWA packaging

Opções para transformar a aplicação Flask em um app Android:

1) PWA (recomendado, simples)
- O app já inclui `static/manifest.json` e um `service worker` básico.
- Requisitos: serve via HTTPS (para instalar como PWA). Se você hospedar em um servidor (Heroku, Railway, VPS), os usuários podem instalar pelo navegador no Android.
- Vantagens: funciona em qualquer plataforma, instalação simples, menos trabalho.
- Limitações: depende de estar hospedado (ou accessible) via HTTPS para instalar.

2) WebView wrapper (fácil)
- Crie um projeto Android no Android Studio e adicione uma `WebView` que aponte para `https://seu-dominio.com` (ou `http://10.0.2.2:5000` em emulador).
- Vantagens: rápido para empacotar, mínimo esforço.
- Limitações: ainda depende do servidor estar disponível.

3) Empacotar o servidor Python localmente (mais complexo)
- Opções: Chaquopy (integra Python em um app Android via Android Studio), BeeWare / Briefcase (experimental), ou usar Termux para rodar o servidor local.
- Requisitos: conhecimento de Android build, configuração de libs nativas e permissões.
- Não recomendado se você busca rapidez.

4) Transformar em app nativo com GUI (alternativa)
- Reescrever a interface com Kivy (Buildozer) ou Toga (BeeWare). Buildozer requer Linux para empacotar APKs.

- Instruções rápidas (PWA)
- Hospede o projeto (por exemplo, num VPS ou serviço como Railway/Heroku).
- Certifique-se que `https://` está configurado.
- Acesse o site pelo Chrome no Android e escolha "Adicionar à tela inicial".

Gerar EXE Windows (offline)
- Para gerar um EXE que rode o servidor local e abra o navegador, use PyInstaller (script `build_windows.ps1` incluído).
- Coloque um arquivo `icon.ico` na raiz do projeto se quiser um ícone customizado (opcional). O script detecta e inclui automaticamente.

Exemplo rápido (PowerShell):
```powershell
Set-Location "c:\Users\kaike\OneDrive\Área de Trabalho\Fingest\FingestPC"
.\venv\Scripts\Activate.ps1
pip install pyinstaller
.\build_windows.ps1
```

O EXE resultante (`dist\run_app.exe`) inicia um servidor local e abre o navegador apontando para `http://127.0.0.1:5000` — assim o app roda completamente offline no computador onde for executado.

Pacote e instalador (Windows)
- Para criar um pacote redistribuível ZIP (pronto para distribuir): execute `build_windows.ps1` para gerar o EXE e depois `build_zip.ps1`. O script `build_zip.ps1` cria `Fingest_windows_package.zip` contendo o EXE, `templates/`, `static/` e README.
- Para criar um instalador `.exe` do Windows, use Inno Setup (instale Inno Setup e adicione `iscc.exe` ao PATH). Em seguida execute `build_installer.ps1` que chamará o compilador com o arquivo `installer.iss`.

Exemplo (ZIP):
```powershell
.\build_windows.ps1
.\build_zip.ps1
```

Exemplo (Inno):
```powershell
# Instale Inno Setup e adicione iscc.exe ao PATH
.\build_installer.ps1
```

Instruções rápidas (WebView wrapper)
- Crie novo projeto Android Studio > Empty Activity.
- No `AndroidManifest.xml` permitir internet.
- No `MainActivity` configure WebView com `webView.loadUrl("https://seu-dominio.com")`.

Notas finais
- Se quiser, eu posso:
  - Gerar um exemplo de projeto Android Studio com uma WebView que aponta para um host configurável.
  - Ajudar a subir o app para um serviço gratuito (Railway) para que você possa testar PWA.
  - Gerar um `build_windows.ps1` (já criado) e explicar como criar o EXE com PyInstaller.
