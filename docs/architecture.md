# Arquitetura do Sistema RelatIA

## Visão Geral

RelatIA é uma aplicação web Django que utiliza agentes de inteligência artificial para realizar análises detalhadas de código-fonte. A arquitetura do sistema segue uma abordagem modular, onde cada componente tem uma responsabilidade bem definida, permitindo fácil manutenção e extensão.

## Diagrama de Arquitetura
## Componentes Principais

### 1. Interface Web (Frontend)
- **Tecnologias**: Django Templates, HTML, CSS, JavaScript
- **Funcionalidades**:
  - Interface de upload de arquivos
  - Visualização de relatórios em formato estruturado
  - Dashboard para acompanhamento de análises
  - Navegação pelo histórico de análises

### 2. Backend Django
- **Tecnologias**: Django, Python, Poetry
- **Componentes**:
  - **Modelos (Models)**:
    - `UploadedFile`: Representa arquivos enviados e seus metadados
    - `AnalysisReport`: Armazena relatórios completos
    - `AnalysisResult`: Mantém resultados individuais por agente/tipo de análise
  - **Views**:
    - `upload_view`: Gerencia o upload de arquivos
    - `report_view`: Exibe relatórios de análise
    - `history_view`: Lista análises anteriores
  - **Controllers**:
    - `AnalysisManager`: Coordena o processo de análise
    - `ReportGenerator`: Compila resultados em relatórios formatados

### 3. Sistema de Agentes IA
- **Tecnologias**: Crew AI, LangChain
- **Padrão de Design**: Factory Pattern
- **Componentes**:
  - `AgentFactory`: Cria e configura diferentes tipos de agentes
  - `TaskFactory`: Define tarefas específicas para cada agente
  - **Tipos de Agentes**:
    - `StructureAgent`: Analisa estrutura, arquitetura e design do código
    - `SecurityAgent`: Identifica vulnerabilidades e problemas de segurança
    - `QualityAgent`: Avalia qualidade, legibilidade e manutenibilidade

### 4. Sistema de Armazenamento
- **Banco de Dados**: PostgreSQL
  - Armazena metadados, usuários, relatórios e resultados
- **Armazenamento de Arquivos**:
  - Sistema de arquivos local (desenvolvimento)
  - Solução de armazenamento escalável (produção)

### 5. Infraestrutura
- **Containerização**: Docker e Docker Compose
- **Orquestração**: Makefile para comandos comuns
- **Gerenciamento de Dependências**: Poetry