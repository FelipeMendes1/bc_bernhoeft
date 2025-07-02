# People Analytics - Case Bern

Este projeto contém uma solução completa de People Analytics, incluindo a geração de dados, scripts de análise em Python e um dashboard interativo no Power BI para investigar padrões de engajamento e retenção de talentos.

## 📊 Dashboard Power BI

O arquivo BI é totalmente dependente do que acontece nesse repositório e provavelmente estará atrelado ao arquivo zipado do projeto para visualização.

O dashboard é dividido em 4 páginas principais:

1.  **Visão Executiva:** Apresenta os KPIs macro da organização, como Taxa de Turnover, Engajamento Médio, e a composição da força de trabalho.
2.  **Análise de Turnover:** Um mergulho profundo nos padrões de saída, com rankings departamentais, análise de turnover voluntário e um heatmap de risco por departamento e geração.
3.  **Matriz de Engajamento:** Um gráfico de dispersão estratégico (9-Box Grid) para segmentar talentos com base na performance e no engajamento.
4.  **Painel de Ação:** Uma lista interativa e filtrável dos funcionários em alto risco, projetada para auxiliar na tomada de decisões de retenção.

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e executar os scripts Python deste projeto em sua máquina local.

#### 1. Pré-requisitos

- [Python](https://www.python.org/downloads/) (versão 3.9 ou superior)
- [Git](https://git-scm.com/downloads/)

#### 2. Clonar o Repositório

```bash
git clone https://github.com/FelipeMendes1/bc_bernhoeft.git
cd bc_bernhoeft\PeopleAnalytics (1)\PeopleAnalytics
```

#### 3. Configurar o Ambiente Virtual

É uma boa prática isolar as dependências do projeto.

```bash
# Criar o ambiente virtual
python -m venv .venv

# Ativar o ambiente virtual
# No Windows (CMD/PowerShell):
.\.venv\Scripts\activate
# No macOS/Linux:
source .venv/bin/activate
```

#### 4. Instalar as Dependências

Este projeto utiliza `uv` para um gerenciamento de pacotes rápido e eficiente.

```bash
#Instalar o uv
pip install uv

#Sincronizar as dependências do projeto com base no arquivo uv.lock
uv sync
```

#### 5. Executar o Script do Banco de Dados

Este passo irá criar e popular as tabelas no banco de dados PostgreSQL na nuvem.

```bash
python create_database_simple.py
```

_Nota: Este script utiliza as credenciais de conexão fornecidas abaixo. Não é necessário ter o PostgreSQL instalado localmente._

#### 6. Rodar a Análise Principal

Para executar as análises definidas no script principal:

```bash
python main_people_analytics.py
```

## ⚙️ Estrutura e Arquivos

Este projeto contém uma solução completa de People Analytics para análise no Power BI com dados realistas de 800 funcionários brasileiros.

#### Arquivos Principais

- **`create_database_simple.py`**

  - Script para criar e popular o banco PostgreSQL.
  - Gera 800 funcionários com dados realistas brasileiros.
  - Cria tabelas otimizadas para análise no Power BI.

- **`main_people_analytics.py`**

  - Versão melhorada do script de análise.
  - Código limpo e documentado com funcionalidade completa integrada.

- **`replit.md`**
  - Documentação técnica do projeto, arquitetura e changelog.

---

## 🔌 Conexão PostgreSQL

**Credenciais para Power BI e Scripts:**

```
Host: ep-round-sound-a5mjdo64.us-east-2.aws.neon.tech
Port: 5432
Database: neondb
Username: neondb_owner
Password: npg_NsgmbIhUt1j6
```
