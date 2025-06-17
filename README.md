# PrintQA - Plataforma de Análise de Qualidade para Impressão 3D

![Python Version](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Tests](https://img.shields.io/badge/Testes-Passing-brightgreen)
![Coverage](https://img.shields.io/badge/Cobertura-100%25-brightgreen)
![License](https://img.shields.io/badge/Licença-MIT-blue)

PrintQA é uma plataforma web dedicada a elevar a qualidade e a taxa de sucesso de projetos de impressão 3D. Desenvolvida pela Print3D Labs, nossa ferramenta oferece uma análise automatizada para identificar e reportar falhas em modelos 3D antes que elas se tornem impressões falhas.

## STATUS DO PROJETO (Atualizado em: 17 de Junho de 2025)

* [✔️] Fase 1: Concepção e Planejamento.
* [✔️] Fase 2: Configuração de Ferramentas e Integrações.
* [✔️] Fase 3: MVP do Backend (Lógica de Análise de Malha e Normais).
* [✔️] Fase 4: Desenvolvimento e Testes da API Backend com FastAPI e Persistência de Dados.
* [➡️] **Próxima Fase:** Configuração de Ambiente de Produção/Deploy (Docker/Kubernetes).

## 🚀 Sobre o Projeto

Na Print3D Labs, nossa filosofia é que a qualidade não é um estágio final, mas a fundação de todo o processo de desenvolvimento. Construímos o PrintQA para resolver um problema real e custoso da comunidade 3D, aplicando os mais rigorosos processos de engenharia de software em cada etapa.

Cada funcionalidade é desenvolvida sob a metodologia de Test-Driven Development (TDD) e integrada através de pipelines de DevSecOps, garantindo que cada linha de código seja validada, segura e robusta. Entregamos este produto porque acreditamos que a melhor forma de demonstrar nosso compromisso com a excelência é através de software funcional, confiável e que resolve problemas reais para nossos usuários e clientes.

## 🛠️ Tecnologias Utilizadas

* **Backend Framework:** FastAPI
* **Banco de Dados:** MariaDB
* **ORM:** SQLAlchemy
* **Validação de Dados (API):** Pydantic
* **Análise 3D:** Trimesh
* **Testes:** Pytest, Pytest-Cov
* **Ambiente e Orquestração:** Docker, Docker Compose
* **CI/CD:** GitHub Actions
* **Gestão de Testes:** TestRail (integrado via `trcli`)

## ⚙️ Como Executar os Testes e a API Localmente (Dockerizado)

Para validar a lógica de análise e a API, utilizando um ambiente de banco de dados isolado via Docker Compose:

1. **Clone o repositório:**

    ```bash
    git clone https://github.com/spencerarq/PrintQA.git
    cd PrintQA
    ```

2. **Crie e configure um arquivo `.env`:**
    Na raiz do projeto, crie um arquivo `.env` (e adicione-o ao `.gitignore` se ainda não o fez) com suas credenciais.

    ```env
    # --- Credenciais do TestRail ---
    TESTRAIL_URL="https://seuid.testrail.io/"
    TESTRAIL_USER="seu.email@exemplo.com"
    TESTRAIL_KEY="sua_chave_api_ou_senha"

    # --- Credenciais do Banco de Dados (usado pelo Docker Compose) ---
    DB_USER=test_user
    DB_PASSWORD=sua_senha_segura
    DB_NAME=printqa_db

    # --- IDs para consistência de permissões (opcional, para Linux/macOS) ---
    USER_ID=1001
    GROUP_ID=1001
    ```

    *Substitua os valores pelos seus dados reais. As variáveis `DB_USER`, `DB_PASSWORD` e `DB_NAME` serão usadas para configurar o contêiner do MariaDB.*

3. **Inicie a API e o Banco de Dados:**

    ```bash
    docker compose up -d --build api
    ```

    * Este comando irá construir as imagens necessárias e iniciar os serviços da `api` e do `db` em segundo plano.

4. **Execute a suíte de testes:**

    ```bash
    docker compose run --rm tests
    ```

    * Este comando executa um contêiner descartável (`--rm`) do serviço `tests`, que roda o Pytest, gera os relatórios de cobertura e os envia ao TestRail.

5. **Acesse a API localmente:**
    * Abra seu navegador e vá para: `http://localhost:8000/docs` (para a documentação interativa Swagger UI).
    * Sua API está rodando no contêiner `api` e acessível na porta `8000` do seu `localhost`.

## 📊 Automação de Testes e Integração TestRail (CI/CD)

O projeto utiliza GitHub Actions para automatizar a execução de testes e o envio de resultados para o TestRail em cada `push` para os branches `main`, `develop` e `qa`, ou em cada `pull_request` para `develop` e `main`.

* **Configuração de Secrets:** As credenciais do TestRail (`TESTRAIL_URL`, `TESTRAIL_USER`, `TESTRAIL_KEY`) e do Banco de Dados (`DB_USER`, `DB_PASSWORD`) **devem ser configuradas como [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)** no seu repositório para garantir a segurança.
* **Workflow:** O arquivo de workflow (`.github/workflows/ci.yml`) gerencia a inicialização de um serviço de banco de dados em contêiner, a instalação de dependências, a execução de testes com **100% de cobertura de código**, e o envio de todos os resultados para o TestRail.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
