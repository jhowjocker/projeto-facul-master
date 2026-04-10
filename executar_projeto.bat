@echo off
:: Maximiza a janela do prompt se não estiver com o argumento 'max'
if not "%1"=="max" start /MAX "" "%0" max & exit /b

echo [0/4] Limpando processos Python anteriores...
:: Isso garante que as portas 5000 e 8000 estejam livres
taskkill /F /IM python.exe /T >nul 2>&1

echo [1/4] Ativando Ambiente Virtual...
call backend\venv\Scripts\activate

echo [2/4] Iniciando Backend (Flask na porta 5000) em segundo plano...
:: O /b faz o comando rodar na MESMA janela, sem abrir outra
start /b python backend/app.py

echo [3/4] Iniciando Frontend (HTTP Server na porta 8000) em segundo plano...
:: O /b faz o comando rodar na MESMA janela
start /b python -m http.server 8000

echo Aguardando 15 segundos para os servicos subirem...
timeout /t 15

echo [4/4] Rodando testes do Robot Framework...
:: Agora o Robot roda aqui mesmo e você verá o log subindo
call python -m robot -v INICIAR_SERVICOS:False -v ENCERRAR_SERVICOS_NO_ROBOT:False --outputdir "%~dp0testes\results" --report report.html --log log.html "%~dp0testes\run"

echo [FIM] Encerrando servicos...
:: Cleanup extra caso o Suite Teardown do Robot falhe por algum motivo
taskkill /F /IM python.exe /T >nul 2>&1

pause

::--------------------------------------------------------------------------------------------------------------::