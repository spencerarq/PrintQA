# PrintQA - Plataforma de Análise de Qualidade para Impressão 3D

![Python Version](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Tests](https://img.shields.io/badge/Testes-Passing-brightgreen)
![Coverage](https://img.shields.io/badge/Cobertura-100%25-brightgreen)
![License](https://img.shields.io/badge/Licença-MIT-blue)

PrintQA é uma plataforma web dedicada a elevar a qualidade e a taxa de sucesso de projetos de impressão 3D. Desenvolvida pela Print3D Labs, nossa ferramenta oferece uma análise automatizada para identificar e reportar falhas em modelos 3D antes que elas se tornem impressões falhas.

## STATUS DO PROJETO (Atualizado em: 18 de Junho de 2025)

* [✔️] Fase 1: Concepção e Planejamento.
* [✔️] Fase 2: Configuração de Ferramentas e Integrações.
* [✔️] Fase 3: MVP do Backend (Lógica de Análise de Malha e Normais).
* [✔️] Fase 4: Desenvolvimento e Testes da API Backend com FastAPI e Persistência de Dados.
* [✔️] Fase 5: **Desenvolvimento e Integração do Frontend (Frontend - básico).**
* [➡️] **Próxima Fase:** Refinamento do Frontend e Configuração de Ambiente de Produção/Deploy.

## 🚀 Sobre o Projeto

Na Print3D Labs, nossa filosofia é que a qualidade não é um estágio final, mas a fundação de todo o processo de desenvolvimento. Construímos o PrintQA para resolver um problema real e custoso da comunidade 3D, aplicando os mais rigorosos processos de engenharia de software em cada etapa.

Cada funcionalidade é desenvolvida sob a metodologia de Test-Driven Development (TDD) e integrada através de pipelines de DevSecOps, garantindo que cada linha de código seja validada, segura e robusta. Entregamos este produto porque acreditamos que a melhor forma de demonstrar nosso compromisso com a excelência é através de software funcional, confiável e que resolve problemas reais para nossos usuários e clientes.

## 🛠️ Tecnologias Utilizadas

* **Backend Framework:** FastAPI
* **Frontend Framework:** React servido por Nginx
* **Banco de Dados:** MariaDB
* **ORM:** SQLAlchemy
* **Validação de Dados (API):** Pydantic
* **Análise 3D:** Trimesh
* **Testes:** Pytest, Pytest-Cov
* **Ambiente e Orquestração:** Docker, Docker Compose
* **CI/CD:** GitHub Actions
* **Gestão de Testes:** TestRail (integrado via `trcli`)

## ⚙️ Como Executar o Frontend, Backend e Testes Localmente (Dockerizado)

Para interagir com a aplicação completa e validar a lógica de análise, utilizando ambientes de banco de dados isolados via Docker Compose:

1. **Clone o repositório:**

    ```bash
    git clone [https://github.com/spencerarq/PrintQA.git](https://github.com/spencerarq/PrintQA.git)
    cd PrintQA
    ```

2. **Crie e configure um arquivo `.env`:**
    Na raiz do projeto, crie um arquivo `.env` (e adicione-o ao `.gitignore` ) com suas credenciais.

    ```env
    # .env

    # --- Credenciais do TestRail (para CI/CD, opcional para local se não usar TestRail localmente) ---
    TESTRAIL_URL="[https://seuid.testrail.io/](https://seuid.testrail.io/)"
    TESTRAIL_USER="seu.email@exemplo.com"
    TESTRAIL_KEY="sua_chave_api_ou_senha"
    TESTRAIL_PROJECT_ID="1"
    TESTRAIL_SUITE_ID="1"
    TESTRAIL_RUN_ID=2
    TESTRAIL_DRY_RUN=false (false envia resultado ao TestRail, true não envia)

    # --- Credenciais do Banco de Dados Principal (para ambiente de desenvolvimento) ---
    DB_USER=rf-qa
    DB_PASSWORD=sua_senha_segura
    DB_NAME=printqa_db

    # --- Nome do Banco de Dados para Testes (usado pelo serviço 'tests' no Docker Compose) ---
    TEST_DB_NAME=test_printqa_db

    # --- Variáveis para o Frontend ---
    # A URL da API que o frontend usará. Para desenvolvimento local, aponta para a API no localhost.
    VITE_API_URL="http://localhost:8000"

    # --- IDs para consistência de permissões (opcional, para Linux/macOS) ---
    USER_ID=1001
    GROUP_ID=1001
    ```

    * Substitua os valores pelos seus dados reais. As variáveis de banco de dados e TestRail são cruciais para o funcionamento.

3. **Inicie a Aplicação Completa (Frontend, Backend e Bancos de Dados):**

    ```bash
    docker compose up -d --build
    ```

    * Este comando irá construir as imagens mais recentes (`api`, `frontend`, `tests`, `db`, `test_db`) e iniciar todos os serviços em segundo plano.

4. **Acesse a Aplicação e a API localmente:**

    * **Frontend (Aplicação Web):** Abra seu navegador e vá para: `http://localhost:3000`
        * Esta é a interface do usuário do PrintQA, servida pelo contêiner Nginx.

    * **Backend (Documentação da API):** Abra seu navegador e vá para: `http://localhost:8000/docs`
        * Esta é a documentação interativa Swagger UI da sua API (FastAPI).

5. **Execute a suíte de testes (Backend):**

    ```bash
    docker compose run --rm tests
    ```

    * Este comando executa um contêiner descartável (`--rm`) do serviço `tests`, que roda o Pytest, gera os relatórios de cobertura e os envia ao TestRail, usando um banco de dados de teste isolado.

## 📊 Automação de Testes e Integração TestRail (CI/CD)

O projeto utiliza GitHub Actions para automatizar a execução de testes e o envio de resultados para o TestRail em cada `push` para os branches `main`, `develop` e `qa`, ou em cada `pull_request` para `develop` e `main`.

* **Configuração de Secrets:**
    As credenciais do TestRail
    (`TESTRAIL_URL`, `TESTRAIL_USER`, `TESTRAIL_KEY`, `TESTRAIL_PROJECT_ID`, `TESTRAIL_SUITE_ID`, `TESTRAIL_RUN_ID`, `TESTRAIL_DRY_RUN`)
    Banco de Dados
    (`DB_USER`, `DB_PASSWORD`, `DB_NAME`, `TEST_DB_NAME`)
    **devem ser configuradas como [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)** no seu repositório para garantir a segurança.
* **Workflow:** O arquivo de workflow (`.github/workflows/ci.yml`) gerencia a inicialização dos serviços em contêiner, a instalação de dependências, a execução de testes de backend com Pytest e a execução de testes End-to-End do Frontend (aguardando implementação completa dos scripts e runners E2E). Ele também é configurado para envio de relatórios para o TestRail.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
