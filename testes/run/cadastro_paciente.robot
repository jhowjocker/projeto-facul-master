*** Settings ***
Library     SeleniumLibrary
Resource    ../resource/common.robot
Resource    ../pages/page_cadastro_paciente.robot
Resource    ../pages/page_agendamento.robot
Resource    ../resource/steps_validacao_bd.robot
Library     Dialogs

Suite Setup       Abrir Sessao Do Sistemas
Suite Teardown    Fechar Sessao Do Sistema


*** Test Cases ***
Cenario de Teste 01: Cadastro de clientes
    [Tags]    CT01
    Dado que a aplicação esta funcional
    Quando clico no botao cadastro
    Então faço o preenchimento do cadastro
    #Pause Execution    Mensagem: Teste finalizado. Clique em OK para liberar o prompt.

Cenario de Teste 02: Agendamento
    [Tags]    CT02
    Dado que estou na pagina de agendamento
    Quando escolho uma data para consulta
    Então o agendamento agendamento é finalizado
    E valido se voltou para tela inicial para um novo cadastro e agendamento

Cenario de Teste 03: Conferindo Banco de Dados pacientes
    [Tags]    CT03
    Dado que acesso o banco de dados para pacientes
    Então confirmo se as informações para pacientes foram cadastradas corretamente
    E confirmo se as informações para agendamento foram cadastradas corretamente
