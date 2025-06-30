#!/usr/bin/env python3
"""
Script para criar e popular o banco de dados PostgreSQL com dados de funcionários da Bern
Para ser usado com Power BI para análise de People Analytics
"""

import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from data_generator import generate_employee_data
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_database_tables(engine):
    """Criar as tabelas no banco de dados"""
    
    # SQL para criar a tabela principal de funcionários
    create_funcionarios_table = """
    CREATE TABLE IF NOT EXISTS funcionarios (
        id_funcionario VARCHAR(10) PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        departamento VARCHAR(100) NOT NULL,
        nivel_cargo VARCHAR(50) NOT NULL,
        geracao VARCHAR(50) NOT NULL,
        idade INTEGER NOT NULL,
        data_admissao DATE NOT NULL,
        tempo_casa_anos DECIMAL(4,1) NOT NULL,
        salario INTEGER NOT NULL,
        score_engajamento DECIMAL(3,1) NOT NULL,
        avaliacao_performance DECIMAL(3,1) NOT NULL,
        status VARCHAR(20) NOT NULL,
        tipo_separacao VARCHAR(20),
        data_separacao DATE,
        score_risco_turnover DECIMAL(5,1) NOT NULL,
        tendencia_engajamento VARCHAR(20) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # SQL para criar tabela de métricas agregadas por departamento
    create_metricas_dept_table = """
    CREATE TABLE IF NOT EXISTS metricas_departamento (
        id SERIAL PRIMARY KEY,
        departamento VARCHAR(100) NOT NULL,
        total_funcionarios INTEGER NOT NULL,
        funcionarios_ativos INTEGER NOT NULL,
        engajamento_medio DECIMAL(3,1) NOT NULL,
        risco_medio DECIMAL(5,1) NOT NULL,
        taxa_turnover DECIMAL(5,2) NOT NULL,
        turnover_voluntario INTEGER NOT NULL,
        turnover_involuntario INTEGER NOT NULL,
        tempo_casa_medio DECIMAL(4,1) NOT NULL,
        salario_medio INTEGER NOT NULL,
        data_calculo DATE DEFAULT CURRENT_DATE,
        UNIQUE(departamento, data_calculo)
    );
    """
    
    # SQL para criar tabela de métricas por geração
    create_metricas_geracao_table = """
    CREATE TABLE IF NOT EXISTS metricas_geracao (
        id SERIAL PRIMARY KEY,
        geracao VARCHAR(50) NOT NULL,
        total_funcionarios INTEGER NOT NULL,
        funcionarios_ativos INTEGER NOT NULL,
        engajamento_medio DECIMAL(3,1) NOT NULL,
        risco_medio DECIMAL(5,1) NOT NULL,
        taxa_turnover DECIMAL(5,2) NOT NULL,
        idade_media DECIMAL(4,1) NOT NULL,
        tempo_casa_medio DECIMAL(4,1) NOT NULL,
        salario_medio INTEGER NOT NULL,
        data_calculo DATE DEFAULT CURRENT_DATE,
        UNIQUE(geracao, data_calculo)
    );
    """
    
    # SQL para criar view com funcionários de alto risco
    create_alto_risco_view = """
    CREATE OR REPLACE VIEW funcionarios_alto_risco AS
    SELECT 
        id_funcionario,
        nome,
        departamento,
        nivel_cargo,
        geracao,
        score_engajamento,
        score_risco_turnover,
        tendencia_engajamento,
        tempo_casa_anos,
        salario,
        CASE 
            WHEN score_risco_turnover >= 80 THEN 'Crítico'
            WHEN score_risco_turnover >= 70 THEN 'Alto'
            WHEN score_risco_turnover >= 50 THEN 'Médio'
            ELSE 'Baixo'
        END as nivel_risco
    FROM funcionarios 
    WHERE status = 'Ativo' AND score_risco_turnover >= 70
    ORDER BY score_risco_turnover DESC;
    """
    
    try:
        with engine.connect() as conn:
            logger.info("Criando tabela de funcionários...")
            conn.execute(text(create_funcionarios_table))
            
            logger.info("Criando tabela de métricas por departamento...")
            conn.execute(text(create_metricas_dept_table))
            
            logger.info("Criando tabela de métricas por geração...")
            conn.execute(text(create_metricas_geracao_table))
            
            logger.info("Criando view de funcionários de alto risco...")
            conn.execute(text(create_alto_risco_view))
            
            conn.commit()
            logger.info("Tabelas criadas com sucesso!")
            
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise

def insert_employee_data(engine, df):
    """Inserir dados dos funcionários no banco"""
    try:
        # Preparar dados para inserção
        df_insert = df.copy()
        
        # Renomear colunas para match com o banco
        column_mapping = {
            'ID_Funcionario': 'id_funcionario',
            'Nome': 'nome',
            'Departamento': 'departamento',
            'Nivel_Cargo': 'nivel_cargo',
            'Geracao': 'geracao',
            'Idade': 'idade',
            'Data_Admissao': 'data_admissao',
            'Tempo_Casa_Anos': 'tempo_casa_anos',
            'Salario': 'salario',
            'Score_Engajamento': 'score_engajamento',
            'Avaliacao_Performance': 'avaliacao_performance',
            'Status': 'status',
            'Tipo_Separacao': 'tipo_separacao',
            'Data_Separacao': 'data_separacao',
            'Score_Risco_Turnover': 'score_risco_turnover',
            'Tendencia_Engajamento': 'tendencia_engajamento'
        }
        
        df_insert = df_insert.rename(columns=column_mapping)
        
        # Converter datas
        df_insert['data_admissao'] = pd.to_datetime(df_insert['data_admissao'])
        df_insert['data_separacao'] = pd.to_datetime(df_insert['data_separacao'], errors='coerce')
        
        # Limpar tabela existente
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE funcionarios RESTART IDENTITY CASCADE;"))
            conn.commit()
        
        # Inserir dados
        logger.info(f"Inserindo {len(df_insert)} funcionários no banco...")
        df_insert.to_sql('funcionarios', engine, if_exists='append', index=False, method='multi')
        logger.info("Dados dos funcionários inseridos com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao inserir dados dos funcionários: {e}")
        raise

def calculate_and_insert_metrics(engine):
    """Calcular e inserir métricas agregadas"""
    try:
        with engine.connect() as conn:
            # Limpar tabelas de métricas
            conn.execute(text("TRUNCATE TABLE metricas_departamento RESTART IDENTITY;"))
            conn.execute(text("TRUNCATE TABLE metricas_geracao RESTART IDENTITY;"))
            
            # Calcular métricas por departamento
            dept_metrics_query = """
            INSERT INTO metricas_departamento (
                departamento, total_funcionarios, funcionarios_ativos, 
                engajamento_medio, risco_medio, taxa_turnover,
                turnover_voluntario, turnover_involuntario,
                tempo_casa_medio, salario_medio
            )
            SELECT 
                departamento,
                COUNT(*) as total_funcionarios,
                SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END) as funcionarios_ativos,
                ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_engajamento END), 1) as engajamento_medio,
                ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_risco_turnover END), 1) as risco_medio,
                ROUND(
                    (SUM(CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 
                    2
                ) as taxa_turnover,
                SUM(CASE WHEN tipo_separacao = 'Voluntário' THEN 1 ELSE 0 END) as turnover_voluntario,
                SUM(CASE WHEN tipo_separacao = 'Involuntário' THEN 1 ELSE 0 END) as turnover_involuntario,
                ROUND(AVG(CASE WHEN status = 'Ativo' THEN tempo_casa_anos END), 1) as tempo_casa_medio,
                ROUND(AVG(CASE WHEN status = 'Ativo' THEN salario END)) as salario_medio
            FROM funcionarios
            GROUP BY departamento;
            """
            
            # Calcular métricas por geração
            gen_metrics_query = """
            INSERT INTO metricas_geracao (
                geracao, total_funcionarios, funcionarios_ativos,
                engajamento_medio, risco_medio, taxa_turnover,
                idade_media, tempo_casa_medio, salario_medio
            )
            SELECT 
                geracao,
                COUNT(*) as total_funcionarios,
                SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END) as funcionarios_ativos,
                ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_engajamento END), 1) as engajamento_medio,
                ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_risco_turnover END), 1) as risco_medio,
                ROUND(
                    (SUM(CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 
                    2
                ) as taxa_turnover,
                ROUND(AVG(idade), 1) as idade_media,
                ROUND(AVG(CASE WHEN status = 'Ativo' THEN tempo_casa_anos END), 1) as tempo_casa_medio,
                ROUND(AVG(CASE WHEN status = 'Ativo' THEN salario END)) as salario_medio
            FROM funcionarios
            GROUP BY geracao;
            """
            
            logger.info("Calculando métricas por departamento...")
            conn.execute(text(dept_metrics_query))
            
            logger.info("Calculando métricas por geração...")
            conn.execute(text(gen_metrics_query))
            
            conn.commit()
            logger.info("Métricas calculadas e inseridas com sucesso!")
            
    except Exception as e:
        logger.error(f"Erro ao calcular métricas: {e}")
        raise

def create_power_bi_summary(engine):
    """Criar resumo executivo para Power BI"""
    try:
        with engine.connect() as conn:
            # Criar tabela de resumo executivo
            create_summary_table = """
            CREATE TABLE IF NOT EXISTS resumo_executivo (
                id SERIAL PRIMARY KEY,
                metrica VARCHAR(100) NOT NULL,
                valor DECIMAL(10,2) NOT NULL,
                descricao TEXT,
                categoria VARCHAR(50) NOT NULL,
                data_calculo DATE DEFAULT CURRENT_DATE
            );
            """
            
            conn.execute(text(create_summary_table))
            
            # Limpar dados anteriores
            conn.execute(text("TRUNCATE TABLE resumo_executivo RESTART IDENTITY;"))
            
            # Inserir resumo executivo
            summary_insert = """
            INSERT INTO resumo_executivo (metrica, valor, descricao, categoria) VALUES
            (
                'Total de Funcionários', 
                (SELECT COUNT(*) FROM funcionarios),
                'Número total de funcionários na base de dados',
                'Geral'
            ),
            (
                'Funcionários Ativos', 
                (SELECT COUNT(*) FROM funcionarios WHERE status = 'Ativo'),
                'Número de funcionários atualmente ativos',
                'Geral'
            ),
            (
                'Taxa de Turnover (%)', 
                (SELECT ROUND((COUNT(CASE WHEN status = 'Desligado' THEN 1 END)::DECIMAL / COUNT(*)) * 100, 2) FROM funcionarios),
                'Percentual de funcionários que deixaram a empresa',
                'Turnover'
            ),
            (
                'Taxa Turnover Voluntário (%)', 
                (SELECT ROUND((COUNT(CASE WHEN tipo_separacao = 'Voluntário' THEN 1 END)::DECIMAL / COUNT(*)) * 100, 2) FROM funcionarios),
                'Percentual de turnover voluntário sobre o total',
                'Turnover'
            ),
            (
                'Engajamento Médio', 
                (SELECT ROUND(AVG(score_engajamento), 1) FROM funcionarios WHERE status = 'Ativo'),
                'Score médio de engajamento dos funcionários ativos',
                'Engajamento'
            ),
            (
                'Funcionários Alto Risco', 
                (SELECT COUNT(*) FROM funcionarios WHERE status = 'Ativo' AND score_risco_turnover >= 70),
                'Número de funcionários com alto risco de turnover',
                'Risco'
            ),
            (
                'Tempo de Casa Médio (Anos)', 
                (SELECT ROUND(AVG(tempo_casa_anos), 1) FROM funcionarios WHERE status = 'Ativo'),
                'Tempo médio de casa dos funcionários ativos',
                'Retenção'
            ),
            (
                'Salário Médio (R$)', 
                (SELECT ROUND(AVG(salario)) FROM funcionarios WHERE status = 'Ativo'),
                'Salário médio dos funcionários ativos',
                'Compensação'
            );
            """
            
            conn.execute(text(summary_insert))
            conn.commit()
            
            logger.info("Resumo executivo criado com sucesso!")
            
    except Exception as e:
        logger.error(f"Erro ao criar resumo executivo: {e}")
        raise

def main():
    """Função principal"""
    try:
        # Obter URL do banco de dados
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL não encontrada nas variáveis de ambiente")
        
        # Criar engine do SQLAlchemy
        engine = create_engine(database_url)
        logger.info("Conectado ao banco PostgreSQL com sucesso!")
        
        # Gerar dados dos funcionários
        logger.info("Gerando dados dos funcionários...")
        df = generate_employee_data(800)  # 800 funcionários
        logger.info(f"Gerados {len(df)} registros de funcionários")
        
        # Criar tabelas
        create_database_tables(engine)
        
        # Inserir dados dos funcionários
        insert_employee_data(engine, df)
        
        # Calcular e inserir métricas agregadas
        calculate_and_insert_metrics(engine)
        
        # Criar resumo executivo
        create_power_bi_summary(engine)
        
        # Mostrar informações de conexão para Power BI
        logger.info("\n" + "="*60)
        logger.info("BANCO DE DADOS CRIADO COM SUCESSO!")
        logger.info("="*60)
        logger.info("\nTabelas criadas:")
        logger.info("- funcionarios: Dados detalhados de todos os funcionários")
        logger.info("- metricas_departamento: Métricas agregadas por departamento")
        logger.info("- metricas_geracao: Métricas agregadas por geração")
        logger.info("- resumo_executivo: KPIs principais para dashboard")
        logger.info("- funcionarios_alto_risco: View com funcionários de alto risco")
        
        logger.info("\nPara conectar ao Power BI, use:")
        logger.info(f"Host: {os.getenv('PGHOST')}")
        logger.info(f"Port: {os.getenv('PGPORT')}")
        logger.info(f"Database: {os.getenv('PGDATABASE')}")
        logger.info(f"Username: {os.getenv('PGUSER')}")
        logger.info(f"Password: {os.getenv('PGPASSWORD')}")
        
        # Mostrar algumas estatísticas
        with engine.connect() as conn:
            result = conn.execute(text("SELECT categoria, metrica, valor FROM resumo_executivo ORDER BY categoria, metrica"))
            logger.info("\nResumo dos KPIs:")
            for row in result:
                logger.info(f"- {row.metrica}: {row.valor}")
        
        logger.info("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Erro na execução principal: {e}")
        raise

if __name__ == "__main__":
    main()