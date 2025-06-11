# PrintQA - Plataforma de Análise de Qualidade para Impressão 3D

![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Tests](https://img.shields.io/badge/Testes-Passing-brightgreen)
![License](https://img.shields.io/badge/Licença-MIT-blue)

PrintQA é uma plataforma web dedicada a elevar a qualidade e a taxa de sucesso de projetos de impressão 3D. Desenvolvida pela Print3D Labs, nossa ferramenta oferece uma análise automatizada para identificar e reportar falhas em modelos 3D antes que elas se tornem impressões falhas.

## STATUS DO PROJETO (Atualizado em: 11 de Junho de 2025)

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
* **Gestão de Testes:** TestRail
* **Controle de Versão:** Git & GitHub

#### Planejadas para as próximas fases:
* **API:** FastAPI
* **Banco de Dados:** MariaDB
* **Frontend:** React / Vue.js
* **CI/CD:** GitHub Actions
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
    source venv/Scripts/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute os testes:**
    ```bash
    pytest
    ```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.