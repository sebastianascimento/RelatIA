# Guia de Instalação do RelatIA

Este guia fornece instruções detalhadas para instalar e configurar o RelatIA em ambiente de desenvolvimento ou produção.

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) (versão 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (versão 2.0+)
- [Git](https://git-scm.com/downloads) (opcional)

## Passo a Passo para Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/RelatIA.git
cd RelatIA

# Configure e inicie os serviço
make setup

# Acesse a aplicação
# Navegue para http://localhost:8000