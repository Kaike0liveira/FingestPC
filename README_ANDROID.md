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

Instruções rápidas (PWA)
- Hospede o projeto (por exemplo, num VPS ou serviço como Railway/Heroku).
- Certifique-se que `https://` está configurado.
- Acesse o site pelo Chrome no Android e escolha "Adicionar à tela inicial".

Instruções rápidas (WebView wrapper)
- Crie novo projeto Android Studio > Empty Activity.
- No `AndroidManifest.xml` permitir internet.
- No `MainActivity` configure WebView com `webView.loadUrl("https://seu-dominio.com")`.

Notas finais
- Se quiser, eu posso:
  - Gerar um exemplo de projeto Android Studio com uma WebView que aponta para um host configurável.
  - Ajudar a subir o app para um serviço gratuito (Railway) para que você possa testar PWA.
  - Gerar um `build_windows.ps1` (já criado) e explicar como criar o EXE com PyInstaller.
