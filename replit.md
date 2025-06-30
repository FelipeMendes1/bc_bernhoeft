# Dashboard People Analytics - Bern

## Overview

Este é um projeto de People Analytics para a empresa Bern que fornece insights abrangentes de RH através de análise de dados de funcionários. O projeto inclui geração de dados sintéticos realistas, análise estatística e um banco de dados PostgreSQL configurado para integração com Power BI.

## System Architecture

O projeto segue uma arquitetura modular focada em análise de dados:

- **Database Layer**: PostgreSQL com dados sintéticos de 800 funcionários brasileiros
- **Data Generation**: Scripts Python para criar dados realistas com padrões de engajamento e turnover
- **Analytics Engine**: Análise estatística usando Pandas, NumPy e SQL
- **Power BI Integration**: Banco de dados estruturado para dashboards executivos
- **SQL Queries**: Consultas otimizadas para análises específicas de People Analytics

## Key Components

### 1. Data Generation (`data_generator.py`)
- Gera datasets realistas de funcionários brasileiros usando biblioteca Faker
- Inclui elementos específicos do Brasil (departamentos, faixas salariais, gerações)
- Cria dados sintéticos com correlações e padrões realistas
- Suporte a contagem customizável de funcionários e distribuições demográficas

### 2. Database Setup (`create_database.py`)
- **Script principal**: Cria e popula banco PostgreSQL
- Gera 800 funcionários com dados realistas para análise
- Cria tabelas estruturadas para análise de People Analytics
- Configura views e métricas agregadas para Power BI

### 3. Analytics Engine (`analytics.py`)
- **PeopleAnalytics Class**: Funcionalidade de análise principal (mantida para referência)
- Calcula métricas principais de RH (turnover, engajamento, tempo de casa)
- Análises por departamento e demografias
- Insights para funcionários ativos vs. desligados

### 4. Power BI Integration (`consultas_powerbi.sql`)
- Consultas SQL otimizadas para dashboards Power BI
- Views específicas para análises de correlação e risco
- Queries para KPIs executivos e análises detalhadas
- Estruturas de dados preparadas para visualizações

## Database Structure

O banco PostgreSQL contém as seguintes tabelas:

### Tabelas Principais
- **funcionarios**: 800 registros de funcionários com dados completos
- **metricas_departamento**: Métricas agregadas por departamento
- **metricas_geracao**: Métricas agregadas por geração
- **resumo_executivo**: KPIs principais para dashboard
- **funcionarios_alto_risco**: View com funcionários de risco >= 70

### Dados Gerados
- Total de funcionários: 800
- Funcionários ativos: 542 (67.75%)
- Taxa de turnover: 32.25%
- Taxa de turnover voluntário: 21.25%
- Engajamento médio: 6.8/10
- Funcionários de alto risco: 57 (10.5% dos ativos)

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Plotly**: Interactive visualization (Express and Graph Objects)
- **Scikit-learn**: Machine learning algorithms
- **SciPy**: Statistical analysis

### Data Generation
- **Faker**: Synthetic data generation with Brazilian localization
- **Random/Datetime**: Built-in Python libraries for data generation

### Styling
- Custom CSS for enhanced UI/UX
- Responsive design elements
- Professional dashboard styling

## Deployment Strategy

The application is designed for easy deployment on Replit:

- **Single Entry Point**: `app.py` serves as the main application file
- **Modular Structure**: Components are separated for maintainability
- **Dependency Management**: All required packages are standard Python libraries
- **Configuration**: Streamlit configuration is embedded in the application

To run the application:
1. Install dependencies: `pip install streamlit pandas numpy plotly scikit-learn faker scipy`
2. Run the application: `streamlit run app.py`
3. Access the dashboard through the provided URL

## Conectividade Power BI

### Credenciais de Conexão
- **Host:** ep-round-sound-a5mjdo64.us-east-2.aws.neon.tech
- **Port:** 5432
- **Database:** neondb
- **Username:** neondb_owner
- **Password:** npg_NsgmbIhUt1j6

### Arquivos de Apoio
- `Guia_PowerBI_PeopleAnalytics.md`: Guia completo para conexão e análise
- `consultas_powerbi.sql`: Consultas SQL otimizadas para Power BI

## Changelog

- 30 de junho de 2025: Criação do banco PostgreSQL com dados de People Analytics
- 30 de junho de 2025: Geração de 800 funcionários com dados realistas brasileiros
- 30 de junho de 2025: Configuração de tabelas e views para análise no Power BI
- 30 de junho de 2025: Documentação completa para integração

## User Preferences

Estilo de comunicação preferido: Linguagem simples e do dia a dia.