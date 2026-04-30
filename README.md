# Projeto de Automação E2E - Agendamento de Consultas 🚀

Este projeto foi desenvolvido como parte do TCC para o curso de **Análise e Desenvolvimento de Sistemas (ADS)**. O objetivo é realizar a automação completa do fluxo de uma aplicação de agendamento, desde o cadastro do paciente até a validação da persistência dos dados no banco.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.11
* **Framework de Automação:** Robot Framework
* **Bibliotecas:** SeleniumLibrary, DateTime, Process, FakerLibrary
* **Backend:** Flask
* **Banco de Dados:** Supabase (PostgreSQL)
* **Arquitetura:** Page Objects e BDD (Behavior Driven Development)

## 🏗️ Estrutura do Projeto

* `cadastro_paciente.robot`: Motor principal da execução (Cenários de Teste).
* `resources/`: Arquivos que isolam as regras de negócio, seletores, APIs e variáveis.
* `config/`: Arquivos de configuração de ambiente e massa de dados.
* `testes/run/results/`: Local onde são gerados os logs e relatórios (report.html).

## 🚀 Como Executar

Para facilitar a execução pela nossa equipe, criamos um script de automação de ambiente:

1.  Certifique-se de ter o Python e o Google Chrome instalados.
2.  Instale as dependências:
    ```bash
    pip install robotframework-seleniumlibrary>=6.0.0 robotframework-faker requests robotframework-requests
    ```
3.  Execute o arquivo `.bat` na raiz do projeto:
    ```bash
    ./executar_testes.bat
    ```
    *Este script irá subir os servidores locais, executar os testes e encerrar os processos automaticamente.*

## 📊 Relatórios

Após a execução, o Robot Framework gera um relatório detalhado em HTML localizado na pasta de resultados, permitindo a análise técnica de cada passo automatizado.

---
**Equipe de ADS - 2026**