

import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar Faker para Brasil
fake = Faker('pt_BR')
random.seed(42)  # Para resultados reproduzíveis
np.random.seed(42)

def create_employee_data():
    logger.info("Gerando dados de funcionários...")
    
    departamentos = [
        'Atendimento ao Cliente', 'Vendas', 'Marketing', 'Tecnologia', 
        'Recursos Humanos', 'Financeiro', 'Operações', 'Compras',
        'Qualidade', 'Logística', 'Jurídico'
    ]
    
    geracoes = {
        'Baby Boomer': (1946, 1964),
        'Geração X': (1965, 1980), 
        'Millennial': (1981, 1996),
        'Geração Z': (1997, 2012)
    }
    
    # Probabilidades de turnover por departamento (realistas)
    turnover_rates = {
        'Atendimento ao Cliente': 0.45,
        'Operações': 0.40,
        'Vendas': 0.38,
        'Logística': 0.35,
        'Recursos Humanos': 0.32,
        'Qualidade': 0.30,
        'Marketing': 0.25,
        'Tecnologia': 0.23,
        'Financeiro': 0.21,
        'Compras': 0.18,
        'Jurídico': 0.15
    }
    
    employees = []
    
    for i in range(800):
        # Dados básicos
        departamento = random.choice(departamentos)
        
        # Geração (distribuição realista)
        geracao = np.random.choice(
            list(geracoes.keys()), 
            p=[0.08, 0.25, 0.50, 0.17]  # Baby Boomer, X, Millennial, Z
        )
        
        ano_nascimento = random.randint(geracoes[geracao][0], geracoes[geracao][1])
        idade = 2025 - ano_nascimento
        
        # Tempo de casa baseado na geração
        if geracao == 'Geração Z':
            tempo_casa = round(random.uniform(0.2, 4.0), 1)
        elif geracao == 'Millennial':
            tempo_casa = round(random.uniform(0.5, 12.0), 1)
        elif geracao == 'Geração X':
            tempo_casa = round(random.uniform(2.0, 25.0), 1)
        else:  # Baby Boomer
            tempo_casa = round(random.uniform(10.0, 35.0), 1)
        
        # Nível e salário
        nivel = np.random.choice(
            ['Júnior', 'Pleno', 'Sênior', 'Gerente', 'Diretor'], 
            p=[0.35, 0.30, 0.20, 0.12, 0.03]
        )
        
        salario_base = {
            'Júnior': random.randint(3000, 6000),
            'Pleno': random.randint(5500, 9500),
            'Sênior': random.randint(8500, 15000),
            'Gerente': random.randint(14000, 25000),
            'Diretor': random.randint(22000, 60000)
        }[nivel]
        
        # Multiplicador salarial por departamento
        multiplicador = {
            'Tecnologia': 1.3, 'Financeiro': 1.2, 'Jurídico': 1.25,
            'Marketing': 1.1, 'Vendas': 1.15, 'Recursos Humanos': 1.0,
            'Operações': 0.9, 'Atendimento ao Cliente': 0.85,
            'Logística': 0.9, 'Compras': 1.05, 'Qualidade': 0.95
        }.get(departamento, 1.0)
        
        salario = int(salario_base * multiplicador)
        
        # Engajamento base por departamento
        engajamento_base = {
            'Atendimento ao Cliente': 5.5, 'Vendas': 6.0, 'Operações': 5.8,
            'Logística': 6.2, 'Marketing': 7.2, 'Tecnologia': 7.5,
            'Recursos Humanos': 6.8, 'Financeiro': 7.0, 'Compras': 7.3,
            'Qualidade': 6.5, 'Jurídico': 7.1
        }[departamento]
        
        # Ajustar engajamento por tempo de casa
        if tempo_casa < 1:
            fator_tempo = 0.8
        elif tempo_casa < 3:
            fator_tempo = 1.1
        elif tempo_casa < 7:
            fator_tempo = 1.0
        elif tempo_casa < 15:
            fator_tempo = 0.95
        else:
            fator_tempo = 0.85
        
        engajamento = round(max(1, min(10, 
            np.random.normal(engajamento_base * fator_tempo, 1.2))), 1)
        
        # Performance correlacionada com engajamento
        performance_base = 1 + (engajamento - 1) * (4/9) * 0.6
        performance = round(max(1, min(5, 
            performance_base + np.random.normal(0, 0.4))), 1)
        
        # Determinar se está ativo baseado em probabilidades
        prob_turnover = turnover_rates[departamento]
        
        # Ajustar probabilidade por engajamento
        if engajamento < 4:
            prob_turnover *= 2.5
        elif engajamento < 6:
            prob_turnover *= 1.5
        elif engajamento > 8:
            prob_turnover *= 0.5
        
        # Ajustar por geração
        multiplicador_geracao = {
            'Geração Z': 1.8, 'Millennial': 1.2, 
            'Geração X': 0.9, 'Baby Boomer': 0.6
        }[geracao]
        prob_turnover *= multiplicador_geracao
        
        is_ativo = random.random() > prob_turnover
        
        # Dados de desligamento
        if not is_ativo:
            tipo_desligamento = 'Voluntário' if random.random() < 0.7 else 'Involuntário'
            data_desligamento = fake.date_between(start_date='-2y', end_date='today')
            score_risco = None
        else:
            tipo_desligamento = None
            data_desligamento = None
            
            # Score de risco para ativos
            risco_base = max(0, 100 - (engajamento * 10))
            fatores_risco = 0
            
            if tempo_casa < 1:
                fatores_risco += 20
            elif tempo_casa > 15:
                fatores_risco += 15
                
            if geracao == 'Geração Z':
                fatores_risco += 15
            elif geracao == 'Millennial':
                fatores_risco += 5
                
            if performance < 3:
                fatores_risco += 25
                
            score_risco = round(min(100, max(0, 
                risco_base + fatores_risco + np.random.normal(0, 10))), 1)
        
        # Tendência de engajamento
        if engajamento < 5:
            tendencia = 'Declinando'
        elif engajamento > 7.5:
            tendencia = 'Crescendo'
        else:
            tendencia = 'Estável'
        
        # Data de admissão
        data_admissao = fake.date_between(
            start_date=f'-{int(tempo_casa*365)}d', 
            end_date=f'-{max(0, int((tempo_casa-0.5)*365))}d'
        )
        
        employee = {
            'id_funcionario': f'EMP{i:04d}',
            'nome': fake.name(),
            'departamento': departamento,
            'nivel_cargo': nivel,
            'geracao': geracao,
            'idade': idade,
            'tempo_casa_anos': tempo_casa,
            'salario': salario,
            'score_engajamento': engajamento,
            'avaliacao_performance': performance,
            'is_ativo': is_ativo,
            'tipo_desligamento': tipo_desligamento,
            'data_desligamento': data_desligamento,
            'score_risco_turnover': score_risco,
            'tendencia_engajamento': tendencia,
            'data_admissao': data_admissao
        }
        
        employees.append(employee)
    
    return pd.DataFrame(employees)

def create_tables_and_insert_data():
    """Criar tabelas e inserir dados no PostgreSQL"""
    
    # Conectar ao banco
    database_url = os.getenv('DATABASE_URL') or 'postgresql://neondb_owner:npg_NsgmbIhUt1j6@ep-round-sound-a5mjdo64.us-east-2.aws.neon.tech:5432/neondb'
    engine = create_engine(database_url)
    
    logger.info("✅ Conectado ao PostgreSQL")
    
    # Gerar dados
    df = create_employee_data()
    logger.info(f"✅ Gerados {len(df)} funcionários")
    
    # Criar tabelas
    with engine.connect() as conn:
        # Limpar tabelas existentes
        conn.execute(text("DROP TABLE IF EXISTS funcionarios CASCADE"))
        conn.execute(text("DROP VIEW IF EXISTS funcionarios_alto_risco CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS metricas_departamento CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS metricas_geracao CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS resumo_executivo CASCADE"))
        
        # Criar tabela principal
        create_table_sql = """
        CREATE TABLE funcionarios (
            id_funcionario VARCHAR(20) PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            departamento VARCHAR(100) NOT NULL,
            nivel_cargo VARCHAR(50) NOT NULL,
            geracao VARCHAR(50) NOT NULL,
            idade INTEGER NOT NULL,
            tempo_casa_anos DECIMAL(4,1) NOT NULL,
            salario INTEGER NOT NULL,
            score_engajamento DECIMAL(3,1) NOT NULL,
            avaliacao_performance DECIMAL(2,1) NOT NULL,
            is_ativo BOOLEAN NOT NULL,
            tipo_desligamento VARCHAR(50),
            data_desligamento DATE,
            score_risco_turnover DECIMAL(5,1),
            tendencia_engajamento VARCHAR(50),
            data_admissao DATE NOT NULL
        );
        """
        conn.execute(text(create_table_sql))
        conn.commit()
        
        logger.info("✅ Tabela funcionarios criada")
    
    # Inserir dados usando pandas
    df.to_sql('funcionarios', engine, if_exists='append', index=False)
    logger.info("✅ Dados inseridos na tabela funcionarios")
    
    # Criar tabelas analíticas
    with engine.connect() as conn:
        # Métricas por departamento
        conn.execute(text("""
            CREATE TABLE metricas_departamento AS
            SELECT 
                departamento,
                COUNT(*) as total_funcionarios,
                COUNT(CASE WHEN is_ativo = true THEN 1 END) as funcionarios_ativos,
                ROUND(AVG(score_engajamento), 1) as engajamento_medio,
                ROUND(AVG(CASE WHEN is_ativo = true THEN score_risco_turnover END), 1) as risco_medio,
                ROUND(
                    (COUNT(*) - COUNT(CASE WHEN is_ativo = true THEN 1 END)) * 100.0 / COUNT(*), 
                    2
                ) as taxa_turnover,
                COUNT(CASE WHEN tipo_desligamento = 'Voluntário' THEN 1 END) as turnover_voluntario,
                COUNT(CASE WHEN tipo_desligamento = 'Involuntário' THEN 1 END) as turnover_involuntario,
                ROUND(AVG(tempo_casa_anos), 1) as tempo_casa_medio,
                ROUND(AVG(salario)) as salario_medio,
                ROUND(
                    COUNT(CASE WHEN is_ativo = true THEN 1 END) * 100.0 / COUNT(*), 
                    1
                ) as taxa_retencao
            FROM funcionarios 
            GROUP BY departamento
            ORDER BY taxa_turnover DESC;
        """))
        
        # Métricas por geração
        conn.execute(text("""
            CREATE TABLE metricas_geracao AS
            SELECT 
                geracao,
                COUNT(*) as total_funcionarios,
                COUNT(CASE WHEN is_ativo = true THEN 1 END) as funcionarios_ativos,
                ROUND(AVG(score_engajamento), 1) as engajamento_medio,
                ROUND(AVG(CASE WHEN is_ativo = true THEN score_risco_turnover END), 1) as risco_medio,
                ROUND(
                    (COUNT(*) - COUNT(CASE WHEN is_ativo = true THEN 1 END)) * 100.0 / COUNT(*), 
                    2
                ) as taxa_turnover,
                ROUND(AVG(tempo_casa_anos), 1) as tempo_casa_medio,
                ROUND(AVG(salario)) as salario_medio
            FROM funcionarios 
            GROUP BY geracao
            ORDER BY taxa_turnover DESC;
        """))
        
        # View de funcionários de alto risco
        conn.execute(text("""
            CREATE VIEW funcionarios_alto_risco AS
            SELECT 
                id_funcionario,
                nome,
                departamento,
                nivel_cargo,
                geracao,
                idade,
                tempo_casa_anos,
                salario,
                score_engajamento,
                score_risco_turnover,
                tendencia_engajamento,
                avaliacao_performance,
                CASE 
                    WHEN score_risco_turnover >= 90 THEN 'Crítico'
                    WHEN score_risco_turnover >= 70 THEN 'Alto'
                    WHEN score_risco_turnover >= 50 THEN 'Médio'
                    ELSE 'Baixo'
                END as nivel_risco,
                CASE 
                    WHEN score_risco_turnover >= 90 THEN 'Intervenção Urgente'
                    WHEN score_risco_turnover >= 70 THEN 'Monitoramento Intensivo'
                    WHEN score_risco_turnover >= 50 THEN 'Acompanhamento Regular'
                    ELSE 'Monitoramento Padrão'
                END as acao_recomendada
            FROM funcionarios 
            WHERE is_ativo = true AND score_risco_turnover >= 70
            ORDER BY score_risco_turnover DESC;
        """))
        
        # Resumo executivo
        conn.execute(text("""
            CREATE TABLE resumo_executivo AS
            SELECT 
                'Total Funcionários' as metrica,
                COUNT(*)::text as valor,
                'pessoas' as unidade
            FROM funcionarios
            UNION ALL
            SELECT 
                'Funcionários Ativos',
                COUNT(CASE WHEN is_ativo = true THEN 1 END)::text,
                'pessoas'
            FROM funcionarios
            UNION ALL
            SELECT 
                'Taxa de Turnover',
                ROUND((COUNT(*) - COUNT(CASE WHEN is_ativo = true THEN 1 END)) * 100.0 / COUNT(*), 1)::text,
                '%'
            FROM funcionarios
            UNION ALL
            SELECT 
                'Engajamento Médio',
                ROUND(AVG(score_engajamento), 1)::text,
                '/10'
            FROM funcionarios
            UNION ALL
            SELECT 
                'Funcionários Alto Risco',
                COUNT(CASE WHEN is_ativo = true AND score_risco_turnover >= 70 THEN 1 END)::text,
                'pessoas'
            FROM funcionarios
            UNION ALL
            SELECT 
                'Turnover Voluntário',
                ROUND(COUNT(CASE WHEN tipo_desligamento = 'Voluntário' THEN 1 END) * 100.0 / 
                      NULLIF(COUNT(CASE WHEN is_ativo = false THEN 1 END), 0), 1)::text,
                '% dos desligamentos'
            FROM funcionarios
            UNION ALL
            SELECT 
                'Tempo Médio de Casa',
                ROUND(AVG(tempo_casa_anos), 1)::text,
                'anos'
            FROM funcionarios
            UNION ALL
            SELECT 
                'Salário Médio',
                ROUND(AVG(salario))::text,
                'R$'
            FROM funcionarios;
        """))
        
        conn.commit()
        logger.info("✅ Tabelas analíticas criadas")
    
    # Relatório final
    with engine.connect() as conn:
        kpis = pd.read_sql("SELECT metrica, valor FROM resumo_executivo", conn)
        alto_risco = pd.read_sql("SELECT COUNT(*) as total FROM funcionarios_alto_risco", conn)
        
        logger.info("\n" + "="*60)
        logger.info("🎯 PEOPLE ANALYTICS BERN - BANCO CRIADO COM SUCESSO!")
        logger.info("="*60)
        
        logger.info("\n📊 KPIs PRINCIPAIS:")
        for _, row in kpis.iterrows():
            logger.info(f"• {row['metrica']}: {row['valor']}")
        
        logger.info(f"\n⚠️  Funcionários de Alto Risco: {alto_risco.iloc[0]['total']}")
        
        logger.info("\n🔌 CREDENCIAIS POWER BI:")
        logger.info("• Host: ep-round-sound-a5mjdo64.us-east-2.aws.neon.tech")
        logger.info("• Port: 5432")
        logger.info("• Database: neondb")
        logger.info("• Username: neondb_owner")
        logger.info("• Password: npg_NsgmbIhUt1j6")
        
        logger.info("\n📋 TABELAS DISPONÍVEIS:")
        logger.info("• funcionarios - Dataset principal (800 registros)")
        logger.info("• funcionarios_alto_risco - View com funcionários críticos")
        logger.info("• metricas_departamento - Análises por área")
        logger.info("• metricas_geracao - Análises por geração")
        logger.info("• resumo_executivo - KPIs para dashboard")
        
        logger.info("\n✅ Pronto para conectar no Power BI!")

if __name__ == "__main__":
    try:
        create_tables_and_insert_data()
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        raise
