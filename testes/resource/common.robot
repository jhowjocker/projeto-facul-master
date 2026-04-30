*** Settings ***
Library     SeleniumLibrary
Library     Process
Resource    ../config/config_cadastro_paciente.robot

*** Variables ***
${URL}                 http://localhost:8000
${BROWSER}             chrome
${INICIAR_SERVICOS}    ${True}
${ENCERRAR_SERVICOS_NO_ROBOT}    ${True}

*** Keywords ***
Abrir Sessao Do Sistemas
    IF    ${INICIAR_SERVICOS}
        Iniciando serviços
    END
    Open Browser                ${URL}    ${BROWSER}    options=add_argument("--log-level=3")
    #Minimize Browser Window
    Maximize Browser Window
    Execute JavaScript         window.focus();
    Sleep                       5s
    Set Selenium Timeout        10 seconds
    
Fechar Sessao Do Sistema
    Close Browser
    IF    ${ENCERRAR_SERVICOS_NO_ROBOT}
        Log To Console    \nEncerrando serviços Python...
        Run Process    taskkill /F /IM python.exe /T    shell=True    stdout=${null}    stderr=${null}
    ELSE
        Log To Console    \nSessão encerrada. Limpeza de serviços será feita pelo script externo.
    END