# PrintQA - Plataforma de Análise de Qualidade para Impressão 3D

![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Tests](https://img.shields.io/badge/Testes-Passing-brightgreen)
![License](https://img.shields.io/badge/Licença-MIT-blue)

PrintQA é uma plataforma web dedicada a elevar a qualidade e a taxa de sucesso de projetos de impressão 3D. Desenvolvida pela Print3D Labs, nossa ferramenta oferece uma análise automatizada para identificar e reportar falhas em modelos 3D antes que elas se tornem impressões falhas.

## STATUS DO PROJETO (Atualizado em: 12 de Junho de 2025)

* [✔️] Fase 1: Concepção e Planejamento.
* [✔️] Fase 2: Configuração de Ferramentas e Integrações.
* [✔️] Fase 3: MVP do Backend (Lógica de Análise de Malha e Normais).
* [➡️] **Próxima Fase:** Desenvolvimento da API Backend com FastAPI.

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

#### Planejadas para as próximas fases:
* **API:** FastAPI
* **Banco de Dados:** MariaDB
* **Frontend:** React / Vue.js
* **CI/CD:** GitHub Actions (para automação de testes e integração TestRail)
* **Infraestrutura:** Docker, Docker Compose
* **Monitoramento:** Prometheus, Grafana

## ⚙️ Como Executar os Testes Atuais

Para validar a lógica de análise implementada até o momento:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/spencerarq/PrintQA.git](https://github.com/spencerarq/PrintQA.git)
    cd PrintQA
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/Scripts/activate # Para Windows/Git Bash
    # ou source venv/bin/activate # Para Linux/macOS
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute os testes (sem integração direta com TestRail):**
    ```bash
    pytest
    ```

## 📊 Como Integrar e Enviar Resultados para o TestRail

Neste projeto, a integração com o TestRail é feita através do **TestRail CLI (trcli)**, garantindo uma abordagem robusta e agnóstica ao framework de testes.

### Configuração do TestRail

Para que a integração funcione, configure os seguintes itens no seu TestRail:
* **API Habilitada:** Em `Admin > Site Settings`, certifique-se de que a API do TestRail está habilitada.
* **Campo Personalizado `Automation ID`:** Crie um campo personalizado para casos de teste com:
    * **Label:** `Automation ID`
    * **System Name:** `automation_id`
    * **Type:** `Text`
    * Atribua-o a todos os projetos ou especificamente ao projeto "PrintQA".

### Configuração Local (`.env`)

Para rodar a integração localmente, crie um arquivo `.env` na raiz do seu projeto (e adicione-o ao `.gitignore`) com suas credenciais e IDs: