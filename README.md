# PrintQA - Plataforma de Análise de Qualidade para Impressão 3D

![Python Version](https://img.shields.io/badge/Python-3.12+-blue.svg) 
![Tests](https://img.shields.io/badge/Testes-Passing-brightgreen)
![Coverage](https://img.shields.io/badge/Cobertura-100%25-brightgreen) 
![License](https://img.shields.io/badge/Licença-MIT-blue)

PrintQA é uma plataforma web dedicada a elevar a qualidade e a taxa de sucesso de projetos de impressão 3D. Desenvolvida pela Print3D Labs, nossa ferramenta oferece uma análise automatizada para identificar e reportar falhas em modelos 3D antes que elas se tornem impressões falhas.

## STATUS DO PROJETO (Atualizado em: 15 de Junho de 2025) * 
* [✔️] Fase 1: Concepção e Planejamento.
* [✔️] Fase 2: Configuração de Ferramentas e Integrações.
* [✔️] Fase 3: MVP do Backend (Lógica de Análise de Malha e Normais).
* [✔️] **Fase 4: Desenvolvimento e Testes da API Backend com FastAPI e Persistência de Dados.** 
* [➡️] **Próxima Fase:** Configuração de Ambiente de Produção/Deploy (Docker/Kubernetes). 

## 🚀 Sobre o Projeto

Na Print3D Labs, nossa filosofia é que a qualidade não é um estágio final, mas a fundação de todo o processo de desenvolvimento. Construímos o PrintQA para resolver um problema real e custoso da comunidade 3D, aplicando os mais rigorosos processos de engenharia de software em cada etapa.

Cada funcionalidade é desenvolvida sob a metodologia de Test-Driven Development (TDD) e integrada através de pipelines de DevSecOps, garantindo que cada linha de código seja validada, segura e robusta. Entregamos este produto porque acreditamos que a melhor forma de demonstrar nosso compromisso com a excelência é através de software funcional, confiável e que resolve problemas reais para nossos usuários e clientes.

## 🛠️ Tecnologias Utilizadas

#### Implementadas até o momento:
* **Linguagem:** Python
* **Testes (Backend):** Pytest
* **Análise 3D:** Trimesh
* **Gestão de Testes:** TestRail (com integração de resultados via CLI)
* **Controle de Versão:** Git & GitHub
* **Web Framework:** FastAPI
* **Banco de Dados:** MariaDB (Local e CI/CD com Docker)
* **Orquestração de Contêineres:** Docker Compose (para ambiente de desenvolvimento/testes local)
* **CI/CD:** GitHub Actions (para automação de testes e integração TestRail)

#### Planejadas para as próximas fases:
* **API:** (já implementada em parte, expandir)
* **Frontend:** React / Vue.js
* **Infraestrutura:** Docker, Docker Compose (para deploy), Kubernetes
* **Monitoramento:** Prometheus, Grafana

## ⚙️ Como Executar os Testes e a API Localmente (Dockerizado)

Para validar a lógica de análise e a API, utilizando um ambiente de banco de dados isolado via Docker Compose:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/spencerarq/PrintQA.git](https://github.com/spencerarq/PrintQA.git)
    cd PrintQA
    ```

2.  **Crie e configure um arquivo `.env`:**
    Na raiz do projeto, crie um arquivo `.env` (e adicione-o ao `.gitignore`) com suas credenciais e IDs.
    ```
    TESTRAIL_URL="https://seuid.testrail.io/"
    TESTRAIL_USER="seu.email@exemplo.com"
    TESTRAIL_KEY="sua_chave_api_ou_senha"
    TESTRAIL_PROJECT_ID=1
    TESTRAIL_SUITE_ID=1

    # Credenciais para o banco de dados local (Docker Compose)
    DB_PASSWORD=sua_senha_do_db_local_docker # Senha que você usou no docker-compose.yml para MYSQL_ROOT_PASSWORD
    DB_NAME=test_printqa_db                  # Nome do DB no docker-compose.yml para MYSQL_DATABASE
    DB_USER=root                             # Usuário root do container MySQL/MariaDB
    DB_HOST=localhost                        # Host do DB acessível do seu ambiente local
    DB_PORT=3306                             # Porta mapeada do DB no docker-compose.yml

    # DATABASE_URL completa para sua aplicação e testes 
    (deve corresponder ao DB_USER/DB_PASSWORD/DB_HOST/DB_NAME/DB_PORT acima)
    DATABASE_URL="mysql+mysqlconnector://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    ```
    *Substitua os valores pelos seus dados reais.*

3.  **Construa e inicie os contêineres Docker:**
    ```bash
    docker compose -f 'docker-compose.yml' up -d --build
    ```
    * Este comando irá construir as imagens `api` e `tests`, e iniciar os serviços `db`, `api` e `tests` em segundo plano.

4.  **Execute os testes dentro do contêiner de testes:**
    ```bash
    docker compose run --rm tests
    ```
    * Este comando executa os testes Pytest, coleta 100% de cobertura de código e envia os resultados para o TestRail.
    * Você pode ver os logs completos da execução dos testes e do envio para o TestRail diretamente no seu terminal.

5.  **Acesse a API localmente (após iniciar com `docker compose up -d`):**
    * Abra seu navegador e vá para: `http://localhost:8000/docs` (para a documentação interativa Swagger UI).
    * Sua API está rodando no contêiner `api` e acessível na porta `8000` do seu `localhost`.

## 📊 Automação de Testes e Integração TestRail (CI/CD)

O projeto utiliza GitHub Actions para automatizar a execução de testes e o envio de resultados para o TestRail em cada `push` para os branches `main`, `develop` e `qa`, ou em cada `pull_request` para `develop` e `main`.

* **Configuração de Secrets:** As credenciais do TestRail (`TESTRAIL_URL`, `TESTRAIL_USER`, `TESTRAIL_KEY`) e do Banco de Dados (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` ou `DATABASE_URL` construída) **devem ser configuradas como [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)** no seu repositório para garantir a segurança.
* **Workflow:** O arquivo de workflow (`.github/workflows/ci.yml`) gerencia a inicialização de um serviço de banco de dados em contêiner, a instalação de dependências, a execução de testes e a coleta de **100% de cobertura de código**, e o envio de todos os resultados para o TestRail utilizando `trcli`.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.