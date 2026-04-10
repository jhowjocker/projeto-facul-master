*** Settings ***
Library    RequestsLibrary
Library    Collections
Library    json

*** Variables ***
${URL_BASE}      https://dpugattsztlslyiudneu.supabase.co/rest/v1/
${TABELA_AG}        agendamentos
${SUPABASE_KEY}  sb_publishable_uSrDS1XXeyM6Gdn_Wlfb2g_zVjONOcx
${AGENDAMENTO_ID}  1  # O ID que você quer confirmar

*** Keywords ***
Dado que acesso o banco de dados para agendamentos
    [Documentation]    Faz um GET filtrando pelo ID para confirmar a persistência.
    
    ${headers}    Create Dictionary    
    ...    apikey=${SUPABASE_KEY}    
    ...    Authorization=Bearer ${SUPABASE_KEY}    
    ...    Content-Type=application/json

    Create Session    supabase    ${URL_BASE}    headers=${headers}    verify=True

    ${response}    GET On Session    supabase    
    ...    url=/${TABELA_AG}?select=*

    Status Should Be    200    ${response}
    
    ${total_registros}    Get Length    ${response.json()}
    Should Be True    ${total_registros} > 0    Nenhum agendamento encontrado no banco de dados!
