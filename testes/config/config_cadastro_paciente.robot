*** Settings ***
Library    Process
Library    SeleniumLibrary

***Variables***
# Define o caminho para a raiz do projeto (subindo dois níveis de testes/config)
${PROJECT_ROOT}    ${CURDIR}${/}..${/}..

# Define o caminho para o Python do seu ambiente virtual
${PYTHON_VENV}    ${PROJECT_ROOT}${/}backend${/}venv${/}Scripts${/}python.exe

*** Keywords ***
Iniciando serviços
    Log To Console    \n[1/3] Iniciando Backend (Flask) com VENV...
    # Inicia o processo do backend usando o executável do venv e define o cwd para a raiz do projeto
    ${backend_process}=    Start Process    ${PYTHON_VENV}    backend/app.py    alias=backend_flask    cwd=${PROJECT_ROOT}
    Set Suite Variable    ${backend_process}

    Log To Console    [2/3] Iniciando Frontend (HTTP Server) com VENV na raiz do projeto...
    # Inicia o servidor de arquivos estáticos na raiz do projeto, onde está o index.html
    ${frontend_process}=    Start Process    ${PYTHON_VENV}    -m    http.server    8000    alias=frontend_http    cwd=${PROJECT_ROOT}
    Set Suite Variable    ${frontend_process}

    Log To Console    Aguardando 15 segundos para os serviços subirem...
    Sleep    15s
    Log To Console    Serviços prontos.