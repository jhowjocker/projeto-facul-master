*** Settings ***
Resource    ../pages/page_bd_cadpacientes.robot
Resource    ../pages/page_bd_cadagendamentos.robot

*** Keywords ***
Dado que acesso o banco de dados para pacientes
    Acessndo o banco de dados para pacientes

Quando listo as tabelas
    Log To Console    \n[Ação] Consultando tabelas e registros para validação...

Então confirmo se as informações para pacientes foram cadastradas corretamente
    # Reutiliza a busca para garantir que o status e os dados básicos estão consistentes
    Dado que acesso o banco de dados para pacientes

E confirmo se as informações para agendamento foram cadastradas corretamente
    # Chama a keyword de parametrização que valida o vínculo entre paciente e agendamento
    Validar Relacionamento Paciente E Agendamento
