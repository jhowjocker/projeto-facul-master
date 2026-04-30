@echo off
:: Maximiza a janela do prompt se não estiver com o argumento 'max'
if not "%1"=="max" start /MAX "" "%0" max & exit /b

echo [0/4] Limpando processos Python anteriores...
:: Isso garante que as portas 5000 e 8000 estejam livres
taskkill /F /FI "IMAGENAME eq python.exe" /T >nul 2>&1

echo [1/4] Ativando Ambiente Virtual...
call "%~dp0backend\venv\Scripts\activate"

echo [1.5/4] Verificando dependências...
:: Garante que as bibliotecas críticas estejam instaladas
pip install --quiet -r "%~dp0backend\requirements.txt" bcrypt

echo [2/4] Iniciando Servidor Unificado (Flask na porta 5000)...
:: O /b faz o comando rodar na MESMA janela, sem abrir outra
start /b python "%~dp0backend\app.py" > backend_log.txt 2>&1

echo Aguardando 15 segundos para os servicos subirem...
timeout /t 15

echo [4/4] Rodando testes do Robot Framework...
:: Agora o Robot roda aqui mesmo e você verá o log subindo
call python -m robot -v URL:http://localhost:5000 -v INICIAR_SERVICOS:False -v ENCERRAR_SERVICOS_NO_ROBOT:False --outputdir "%~dp0testes\results" --report report.html --log log.html "%~dp0testes\run"

echo [FIM] Encerrando servicos...
:: Cleanup extra caso o Suite Teardown do Robot falhe por algum motivo
taskkill /F /IM python.exe /T >nul 2>&1

pause

::--------------------------------------------------------------------------------------------------------------::