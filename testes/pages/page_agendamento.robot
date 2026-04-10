*** Settings ***
Library     SeleniumLibrary
Resource    ../resource/common.robot
Library    DateTime

*** Variables ***
${URL_agend}          http://localhost:8000/agendamento.html
${campo_data}         (//input[@id='data'])[1]
${botao_agendar}      (//button[normalize-space()='Agendar'])[1]


*** Keywords ***
#Dado que abro Sessao Do Sistemas de agendamento
Dado que estou na pagina de agendamento
    Wait Until Page Contains    Agende sua Consulta.
    Sleep   5
    Log To Console    Cadastro enviado com sucesso!
        
Quando escolho uma data para consulta
    ${data_inicio}=        Get Current Date    increment=1 day    result_format=%d%m%Y
    ${data_limite}=        Get Current Date    increment=60 days    result_format=%d%m%Y
    ${data_para_input}=    Get Current Date    increment=5 days    result_format=%d%m%Y
    Click Element          ${campo_data}
    Input Text             ${campo_data}       ${data_para_input}
    Log To Console         Data agendada para: ${data_para_input}
    Sleep   5
    
Então o agendamento agendamento é finalizado
    Click Element          ${botao_agendar}
    Sleep   5
    Handle Alert           action=ACCEPT    timeout= 5s
    Log To Console         agendamento finalizado com sucesso!

E valido se voltou para tela inicial para um novo cadastro e agendamento
    Page Should Contain    Consulta.com
    Sleep   5
    Log To Console         Pagina web encontrada com sucesso!
