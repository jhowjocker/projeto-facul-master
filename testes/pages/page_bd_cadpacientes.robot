*** Settings ***
Library    RequestsLibrary
Library    Collections
Library    json

*** Variables ***
${URL_SUPABASE_REST}    https://dpugattsztlslyiudneu.supabase.co/rest/v1/
${URL_API_LOCAL}        http://127.0.0.1:5000/api
${TABELA_PACIENTES}     pacientes
${TABELA_AGENDAMENTOS}  agendamentos
${SUPABASE_KEY}         sb_publishable_uSrDS1XXeyM6Gdn_Wlfb2g_zVjONOcx
${PACIENTE_ID_TESTE}    300

*** Keywords ***
Acessndo o banco de dados para pacientes
    [Documentation]    Faz um GET filtrando pelo ID para confirmar a persistência.
    
    ${headers}    Create Dictionary    
    ...    apikey=${SUPABASE_KEY}    
    ...    Authorization=Bearer ${SUPABASE_KEY}    
    ...    Content-Type=application/json

    Create Session    supabase    ${URL_SUPABASE_REST}    headers=${headers}    verify=True

    ${response}    GET On Session    supabase    url=${TABELA_PACIENTES}?select=*

    Status Should Be    200    ${response}
    
    ${total_registros}    Get Length    ${response.json()}
    Should Be True    ${total_registros} > 0    Nenhum paciente encontrado no banco de dados!

Validar Relacionamento Paciente E Agendamento
    [Documentation]    Busca o último paciente cadastrado, depois valida se existe
    ...                um agendamento vinculado ao paciente_id correspondente.

    Log To Console    \n=== INICIANDO VALIDAÇÃO DE RELACIONAMENTO ===\n

    # --- HEADERS (reutilizável) ---
    ${headers}    Create Dictionary
    ...    apikey=${SUPABASE_KEY}
    ...    Authorization=Bearer ${SUPABASE_KEY}
    ...    Content-Type=application/json

    Create Session    supabase_val    ${URL_SUPABASE_REST}    headers=${headers}    verify=True

    # --- Buscar o último paciente cadastrado ---
    Log To Console    \nBuscando último paciente para conferência final...
    ${resp_paciente}    GET On Session    supabase_val
    ...    url=/${TABELA_PACIENTES}?select=id,nome,cpf&order=id.desc&limit=1

    Status Should Be    200    ${resp_paciente}
    Should Not Be Empty    ${resp_paciente.json()}    Nenhum paciente encontrado para validar o relacionamento.

    ${paciente}         Set Variable    ${resp_paciente.json()[0]}
    ${id_paciente}      Set Variable    ${paciente['id']}
    ${nome_paciente}    Set Variable    ${paciente['nome']}
    ${cpf_paciente}     Set Variable    ${paciente['cpf']}

    Log To Console    \n[Paciente encontrado] ID: ${id_paciente} | Nome: ${nome_paciente} | CPF: ${cpf_paciente}\n

    # --- Buscar agendamento vinculado ao paciente_id ---
    Log To Console    Buscando agendamento vinculado ao ID ${id_paciente}...
    ${resp_agendamento}    GET On Session    supabase_val
    ...    url=/${TABELA_AGENDAMENTOS}?select=id,id_paciente,data_consulta&id_paciente=eq.${id_paciente}&order=id.desc&limit=1

    Status Should Be    200    ${resp_agendamento}

    ${total}    Get Length    ${resp_agendamento.json()}
    Should Be True    ${total} > 0
    ...    FALHA: Nenhum agendamento encontrado para id_paciente=${id_paciente}!

    ${agendamento}      Set Variable    ${resp_agendamento.json()[0]}
    ${id_ag}            Set Variable    ${agendamento['id']}
    ${paciente_id_ag}   Set Variable    ${agendamento['id_paciente']}
    ${data_ag}          Set Variable    ${agendamento['data_consulta']}

    # --- Validar o relacionamento ---
    Should Be Equal As Strings    ${paciente_id_ag}    ${id_paciente}

    Log To Console    \n==========================================================
    Log To Console    ✅ CONFERÊNCIA DE DADOS REALIZADA COM SUCESSO
    Log To Console    ----------------------------------------------------------
    Log To Console    PACIENTE: ${nome_paciente} (ID: ${id_paciente})
    Log To Console    AGENDAMENTO: ID ${id_ag} para a data ${data_ag}
    Log To Console    ==========================================================\n