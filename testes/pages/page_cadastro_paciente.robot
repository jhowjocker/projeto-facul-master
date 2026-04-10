*** Settings ***
Library     SeleniumLibrary
Resource    ../resource/common.robot
Library     FakerLibrary    locale=pt_BR

*** Variables ***

${cadastro}      (//a[normalize-space()='Cadastro'])[1]
${nome}          (//input[@id='nome'])[1]
${sobrenome}     (//input[@id='sobrenome'])[1]
${cpf}           (//input[@id='cpf'])[1]
${email}         (//input[@id='email'])[1]
${cep}           (//input[@id='cep'])[1]
${numero}        (//input[@id='numero'])[1]
${logradouro}    (//input[@id='logradouro'])[1]
${bairro}        (//input[@id='bairro'])[1]
${cidade}        (//input[@id='cidade'])[1]
${estado}        (//input[@id='estado'])[1]
${enviar}        (//button[normalize-space()='enviar'])[1]

#[Arguments]    ${Augusto}    ${Machado}    ${81836971001}    ${augusto_machado@gmail.com}    ${03570000}    ${1400}    ${Avenida Alziro Zarur}    ${Parque Savoy}    ${São Paulo}    ${SP}

*** Keywords ***
Dado que a aplicação esta funcional
    Log To Console        Abrindo navegador
    Page Should Contain   Consulta.com
    Log To Console        Pagina web encontrada com sucesso!
    
Quando clico no botao cadastro
    Wait Until Element Is Visible    ${cadastro}
    Click Element    ${cadastro}
    Sleep   5
    Log To Console    Acesso a pagina de cadastro efetuada com sucesso!

Então faço o preenchimento do cadastro
    # Aguarda o primeiro campo estar visível para garantir que a página carregou
    ${NOME_FAKE}                     FakerLibrary.First Name
    Wait Until Element Is Visible    ${nome}
    Click Element                    ${nome}
    Input Text    ${nome}            ${NOME_FAKE}
    Log To Console    Nome gerado: ${NOME_FAKE}
    
    ${SOBRENOME_PARTE1}              FakerLibrary.Last Name
    ${SOBRENOME_PARTE2}              FakerLibrary.Last Name
    ${SOBRENOME_FAKE}                Set Variable    ${SOBRENOME_PARTE1} ${SOBRENOME_PARTE2}
    Wait Until Element Is Visible    ${sobrenome}
    Click Element                    ${sobrenome}
    Input Text    ${sobrenome}       ${SOBRENOME_FAKE}
    
    ${CPF_FAKE}                      FakerLibrary.Cpf
    Wait Until Element Is Visible    ${cpf}
    Click Element                    ${cpf}
    Input Text    ${cpf}             ${CPF_FAKE}
    
    ${EMAIL_FAKE}                    FakerLibrary.Email
    Wait Until Element Is Visible    ${email}
    Click Element                    ${email}
    Input Text    ${email}           ${EMAIL_FAKE}
    Log To Console    E-mail gerado: ${EMAIL_FAKE}

    ${CEP_FAKE}                      FakerLibrary.Postcode
    Wait Until Element Is Visible    ${cep}
    Click Element                    ${cep}
    Input Text    ${cep}             ${CEP_FAKE}

    ${NUMERO_FAKE}                   FakerLibrary.Building Number
    Wait Until Element Is Visible    ${numero}
    Click Element                    ${numero}
    Input Text    ${numero}          ${NUMERO_FAKE}

    ${LOGRADOURO_FAKE}               FakerLibrary.Street Name
    Wait Until Element Is Visible    ${logradouro}
    Click Element                    ${logradouro}
    Input Text    ${logradouro}      ${LOGRADOURO_FAKE}

    ${BAIRRO_FAKE}                   FakerLibrary.Bairro
    Wait Until Element Is Visible    ${bairro}
    Click Element                    ${bairro}
    Input Text    ${bairro}          ${BAIRRO_FAKE}

    ${CIDADE_FAKE}                   FakerLibrary.City
    Wait Until Element Is Visible    ${cidade}
    Click Element                    ${cidade}
    Input Text    ${cidade}          ${CIDADE_FAKE}

    ${ESTADO_FAKE}                   FakerLibrary.State Abbr
    Wait Until Element Is Visible    ${estado}
    Click Element                    ${estado}
    Input Text    ${estado}          ${ESTADO_FAKE}

    Sleep   5
    Log To Console    Cadastro preenchido com sucesso!
    Wait Until Element Is Visible    ${enviar}
    Click Element                    ${enviar}
    Sleep   5
    Handle Alert    action=ACCEPT    timeout= 5s