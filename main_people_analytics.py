"""
People Analytics - Case Bern
Script principal para criar base de dados PostgreSQL para análise no Power BI

Objetivo: Investigar padrões de engajamento e turnover para decisões estratégicas de retenção
"""

import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine, text
from faker import Faker
from faker.providers import DynamicProvider
import random
import os
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar Faker para Brasil
fake = Faker('pt_BR')

class BernPeopleAnalytics:
    def __init__(self):
        """Inicializar gerador de dados para People Analytics"""
        self.engine = None
        self.setup_database_connection()
        
    def setup_database_connection(self):
        """Configurar conexão com PostgreSQL"""
        try:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL não encontrada nas variáveis de ambiente")
            
            self.engine = create_engine(database_url)
            logger.info("✅ Conexão com PostgreSQL estabelecida")
            
            # Testar conexão
            if self.engine:
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("✅ Teste de conexão bem-sucedido")
            
        except Exception as e:
            logger.error(f"❌ Erro na conexão: {e}")
            raise
    
    def generate_realistic_employee_data(self, num_employees=800):
        """
        Gerar dataset realista de funcionários brasileiros com padrões de engajamento
        """
        logger.info(f"🔄 Gerando dados de {num_employees} funcionários...")
        
        # Definir departamentos brasileiros realistas
        departamentos = [
            'Atendimento ao Cliente', 'Vendas', 'Marketing', 'Tecnologia', 
            'Recursos Humanos', 'Financeiro', 'Operações', 'Compras',
            'Qualidade', 'Logística', 'Jurídico'
        ]
        
        # Definir gerações
        geracoes = {
            'Baby Boomer': (1946, 1964),
            'Geração X': (1965, 1980), 
            'Millennial': (1981, 1996),
            'Geração Z': (1997, 2012)
        }
        
        # Configurar pesos realistas para turnover por departamento
        turnover_weights = {
            'Atendimento ao Cliente': 0.45,  # Alto stress, alta rotatividade
            'Vendas': 0.38,                  # Pressão por resultados
            'Operações': 0.40,               # Trabalho operacional
            'Logística': 0.35,               # Físico, horários
            'Marketing': 0.25,               # Criativo, engajamento médio
            'Tecnologia': 0.23,              # Alta demanda, boa retenção
            'Recursos Humanos': 0.32,        # Burnout médio
            'Financeiro': 0.21,              # Estabilidade
            'Compras': 0.18,                 # Processos, estabilidade
            'Qualidade': 0.30,               # Processos rígidos
            'Jurídico': 0.15                 # Alta especialização, baixo turnover
        }
        
        employees = []
        
        for i in range(num_employees):
            # Dados básicos
            nome = fake.name()
            departamento = random.choice(departamentos)
            
            # Determinar geração baseada em distribuição realista
            geracao_weights = [0.08, 0.25, 0.50, 0.17]  # Baby Boomer, X, Millennial, Z
            geracao = np.random.choice(list(geracoes.keys()), p=geracao_weights)
            
            # Calcular idade baseada na geração
            ano_nascimento = random.randint(geracoes[geracao][0], geracoes[geracao][1])
            idade = 2025 - ano_nascimento
            
            # Tempo de casa (anos) - correlacionado com idade
            if geracao == 'Geração Z':
                tempo_casa = random.uniform(0.2, 4.0)
            elif geracao == 'Millennial':
                tempo_casa = random.uniform(0.5, 12.0)
            elif geracao == 'Geração X':
                tempo_casa = random.uniform(2.0, 25.0)
            else:  # Baby Boomer
                tempo_casa = random.uniform(10.0, 35.0)
            
            # Nível hierárquico
            nivel_cargo = np.random.choice(['Júnior', 'Pleno', 'Sênior', 'Gerente', 'Diretor'], 
                                         p=[0.35, 0.30, 0.20, 0.12, 0.03])
            
            # Salário baseado no nível e departamento
            salario_base = {
                'Júnior': random.randint(3000, 6000),
                'Pleno': random.randint(5500, 9500),
                'Sênior': random.randint(8500, 15000),
                'Gerente': random.randint(14000, 25000),
                'Diretor': random.randint(22000, 60000)
            }
            
            # Multiplicador por departamento
            dept_multiplier = {
                'Tecnologia': 1.3, 'Financeiro': 1.2, 'Jurídico': 1.25,
                'Marketing': 1.1, 'Vendas': 1.15, 'Recursos Humanos': 1.0,
                'Operações': 0.9, 'Atendimento ao Cliente': 0.85,
                'Logística': 0.9, 'Compras': 1.05, 'Qualidade': 0.95
            }
            
            salario = int(salario_base[nivel_cargo] * dept_multiplier.get(departamento, 1.0))
            
            # Score de engajamento (1-10) - influenciado por departamento e tempo de casa
            base_engagement = {
                'Atendimento ao Cliente': 5.5,
                'Vendas': 6.0,
                'Operações': 5.8,
                'Logística': 6.2,
                'Marketing': 7.2,
                'Tecnologia': 7.5,
                'Recursos Humanos': 6.8,
                'Financeiro': 7.0,
                'Compras': 7.3,
                'Qualidade': 6.5,
                'Jurídico': 7.1
            }
            
            # Ajustar engajamento por tempo de casa (curva U invertida)
            if tempo_casa < 1:
                time_factor = 0.8  # Honeymoon period mas ainda adaptando
            elif tempo_casa < 3:
                time_factor = 1.1  # Período de maior engajamento
            elif tempo_casa < 7:
                time_factor = 1.0  # Estabilidade
            elif tempo_casa < 15:
                time_factor = 0.95  # Leve declínio
            else:
                time_factor = 0.85  # Burnout de longo prazo
            
            engagement_score = max(1, min(10, 
                np.random.normal(base_engagement[departamento] * time_factor, 1.2)))
            
            # Avaliação de performance (1-5) - correlacionada com engajamento
            performance_correlation = 0.6
            performance_base = 1 + (engagement_score - 1) * (4/9) * performance_correlation
            performance_noise = np.random.normal(0, 0.4)
            avaliacao_performance = max(1, min(5, performance_base + performance_noise))
            
            # Status do funcionário baseado em probabilidade de turnover
            turnover_prob = turnover_weights[departamento]
            
            # Ajustar probabilidade baseada no engajamento
            if engagement_score < 4:
                turnover_prob *= 2.5
            elif engagement_score < 6:
                turnover_prob *= 1.5
            elif engagement_score > 8:
                turnover_prob *= 0.5
            
            # Ajustar por geração
            gen_turnover_multiplier = {
                'Geração Z': 1.8,
                'Millennial': 1.2, 
                'Geração X': 0.9,
                'Baby Boomer': 0.6
            }
            turnover_prob *= gen_turnover_multiplier[geracao]
            
            is_active = random.random() > turnover_prob
            
            # Para funcionários inativos, determinar tipo de desligamento
            if not is_active:
                # 70% voluntário (mais realista para baixo engajamento)
                tipo_desligamento = 'Voluntário' if random.random() < 0.7 else 'Involuntário'
                data_desligamento = fake.date_between(start_date='-2y', end_date='today')
            else:
                tipo_desligamento = None
                data_desligamento = None
            
            # Score de risco de turnover (0-100) para funcionários ativos
            if is_active:
                # Base do risco inverso ao engajamento
                base_risk = max(0, 100 - (engagement_score * 10))
                
                # Fatores de risco adicionais
                risk_factors = 0
                
                # Tempo de casa
                if tempo_casa < 1:
                    risk_factors += 20
                elif tempo_casa > 15:
                    risk_factors += 15
                
                # Geração
                if geracao == 'Geração Z':
                    risk_factors += 15
                elif geracao == 'Millennial':
                    risk_factors += 5
                
                # Performance baixa
                if avaliacao_performance < 3:
                    risk_factors += 25
                
                risk_score = min(100, max(0, base_risk + risk_factors + np.random.normal(0, 10)))
            else:
                risk_score = None
            
            # Tendência de engajamento
            if engagement_score < 5:
                tendencia = 'Declinando'
            elif engagement_score > 7.5:
                tendencia = 'Crescendo'
            else:
                tendencia = 'Estável'
            
            employee = {
                'id_funcionario': f'EMP{i:04d}',
                'nome': nome,
                'departamento': departamento,
                'nivel_cargo': nivel_cargo,
                'geracao': geracao,
                'idade': idade,
                'tempo_casa_anos': round(tempo_casa, 1),
                'salario': salario,
                'score_engajamento': round(engagement_score, 1),
                'avaliacao_performance': round(avaliacao_performance, 1),
                'is_ativo': is_active,
                'tipo_desligamento': tipo_desligamento,
                'data_desligamento': data_desligamento,
                'score_risco_turnover': round(risk_score, 1) if risk_score else None,
                'tendencia_engajamento': tendencia,
                'data_contratacao': fake.date_between(start_date=f'-{int(tempo_casa*365)}d', end_date=f'-{max(0, int((tempo_casa-0.5)*365))}d')
            }
            
            employees.append(employee)
        
        df = pd.DataFrame(employees)
        logger.info(f"✅ Dados de {len(df)} funcionários gerados com sucesso")
        
        # Estatísticas de validação
        ativos = df[df['is_ativo'] == True]
        logger.info(f"📊 Funcionários ativos: {len(ativos)} ({len(ativos)/len(df)*100:.1f}%)")
        logger.info(f"📊 Taxa de turnover: {(len(df) - len(ativos))/len(df)*100:.1f}%")
        logger.info(f"📊 Engajamento médio: {df['score_engajamento'].mean():.1f}/10")
        
        return df
    
    def create_database_structure(self, df):
        """
        Criar estrutura do banco PostgreSQL otimizada para Power BI
        """
        logger.info("🔄 Criando estrutura do banco de dados...")
        
        try:
            if self.engine:
                with self.engine.connect() as conn:
                    # Limpar tabelas existentes
                    conn.execute(text("DROP TABLE IF EXISTS funcionarios CASCADE"))
                    conn.execute(text("DROP VIEW IF EXISTS funcionarios_alto_risco CASCADE"))
                    conn.execute(text("DROP TABLE IF EXISTS metricas_departamento CASCADE"))
                    conn.execute(text("DROP TABLE IF EXISTS metricas_geracao CASCADE"))
                    conn.execute(text("DROP TABLE IF EXISTS resumo_executivo CASCADE"))
                    conn.commit()
                
                # Criar tabela principal de funcionários
                create_funcionarios = """
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
                    data_contratacao DATE NOT NULL
                );
                """
                conn.execute(text(create_funcionarios))
                
                # Inserir dados dos funcionários
                df.to_sql('funcionarios', conn, if_exists='append', index=False, method='multi')
                
                # Criar view de funcionários de alto risco
                create_alto_risco_view = """
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
                """
                conn.execute(text(create_alto_risco_view))
                
                conn.commit()
                logger.info("✅ Estrutura do banco criada com sucesso")
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar estrutura: {e}")
            raise
    
    def create_analytical_tables(self):
        """
        Criar tabelas de métricas agregadas para análise executiva
        """
        logger.info("🔄 Criando tabelas analíticas...")
        
        try:
            with self.engine.connect() as conn:
                # Métricas por departamento
                metricas_dept_query = """
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
                    ) as taxa_retencao,
                    CASE 
                        WHEN AVG(score_engajamento) >= 7.5 THEN 'Alto'
                        WHEN AVG(score_engajamento) >= 6.0 THEN 'Médio'
                        ELSE 'Baixo'
                    END as categoria_engajamento,
                    CASE 
                        WHEN (COUNT(*) - COUNT(CASE WHEN is_ativo = true THEN 1 END)) * 100.0 / COUNT(*) >= 35 THEN 'Alto'
                        WHEN (COUNT(*) - COUNT(CASE WHEN is_ativo = true THEN 1 END)) * 100.0 / COUNT(*) >= 25 THEN 'Normal'
                        ELSE 'Baixo'
                    END as categoria_turnover
                FROM funcionarios 
                GROUP BY departamento
                ORDER BY taxa_turnover DESC;
                """
                conn.execute(text(metricas_dept_query))
                
                # Métricas por geração
                metricas_ger_query = """
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
                """
                conn.execute(text(metricas_ger_query))
                
                # Resumo executivo
                resumo_exec_query = """
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
                """
                conn.execute(text(resumo_exec_query))
                
                conn.commit()
                logger.info("✅ Tabelas analíticas criadas com sucesso")
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas analíticas: {e}")
            raise
    
    def generate_insights_report(self):
        """
        Gerar relatório com insights principais para decisões executivas
        """
        logger.info("🔄 Gerando relatório de insights...")
        
        try:
            with self.engine.connect() as conn:
                # KPIs principais
                kpis = pd.read_sql("""
                    SELECT metrica, valor, unidade 
                    FROM resumo_executivo
                """, conn)
                
                # Departamentos críticos
                dept_criticos = pd.read_sql("""
                    SELECT departamento, taxa_turnover, engajamento_medio, funcionarios_ativos
                    FROM metricas_departamento 
                    WHERE taxa_turnover > 35 OR engajamento_medio < 6.5
                    ORDER BY taxa_turnover DESC
                """, conn)
                
                # Funcionários alto risco
                alto_risco = pd.read_sql("""
                    SELECT COUNT(*) as total_alto_risco
                    FROM funcionarios_alto_risco
                """, conn)
                
                # Correlações chave
                correlacao = pd.read_sql("""
                    SELECT 
                        CORR(score_engajamento, CASE WHEN is_ativo THEN 0 ELSE 1 END) as corr_engajamento_turnover,
                        CORR(score_engajamento, avaliacao_performance) as corr_engajamento_performance,
                        CORR(tempo_casa_anos, score_engajamento) as corr_tempo_engajamento
                    FROM funcionarios
                """, conn)
                
                logger.info("📊 RESUMO EXECUTIVO - PEOPLE ANALYTICS BERN")
                logger.info("=" * 60)
                
                for _, row in kpis.iterrows():
                    logger.info(f"• {row['metrica']}: {row['valor']} {row['unidade']}")
                
                logger.info("\n🔥 DEPARTAMENTOS CRÍTICOS:")
                for _, row in dept_criticos.iterrows():
                    logger.info(f"• {row['departamento']}: {row['taxa_turnover']}% turnover, engajamento {row['engajamento_medio']}/10")
                
                logger.info(f"\n⚠️  FUNCIONÁRIOS DE ALTO RISCO: {alto_risco.iloc[0]['total_alto_risco']} pessoas")
                
                logger.info("\n📈 CORRELAÇÕES IDENTIFICADAS:")
                logger.info(f"• Engajamento vs Turnover: {correlacao.iloc[0]['corr_engajamento_turnover']:.2f} (forte correlação negativa)")
                logger.info(f"• Engajamento vs Performance: {correlacao.iloc[0]['corr_engajamento_performance']:.2f}")
                logger.info(f"• Tempo de Casa vs Engajamento: {correlacao.iloc[0]['corr_tempo_engajamento']:.2f}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao gerar insights: {e}")
            raise
    
    def run_complete_analysis(self):
        """
        Executar análise completa: gerar dados, criar banco e insights
        """
        logger.info("🚀 Iniciando análise completa de People Analytics...")
        
        # 1. Gerar dados realistas
        df = self.generate_realistic_employee_data(800)
        
        # 2. Criar estrutura do banco
        self.create_database_structure(df)
        
        # 3. Criar tabelas analíticas
        self.create_analytical_tables()
        
        # 4. Gerar insights
        self.generate_insights_report()
        
        # 5. Informações de conexão
        logger.info("\n" + "="*60)
        logger.info("✅ PEOPLE ANALYTICS BERN - CONFIGURAÇÃO COMPLETA!")
        logger.info("="*60)
        logger.info("\n📋 CREDENCIAIS PARA POWER BI:")
        logger.info("• Host: ep-round-sound-a5mjdo64.us-east-2.aws.neon.tech")
        logger.info("• Port: 5432")
        logger.info("• Database: neondb")
        logger.info("• Username: neondb_owner")
        logger.info("• Password: npg_NsgmbIhUt1j6")
        
        logger.info("\n📊 TABELAS DISPONÍVEIS:")
        logger.info("• funcionarios - Dataset principal (800 registros)")
        logger.info("• funcionarios_alto_risco - View com funcionários críticos")
        logger.info("• metricas_departamento - Análises por área")
        logger.info("• metricas_geracao - Análises por geração")
        logger.info("• resumo_executivo - KPIs para dashboard")
        
        logger.info("\n🎯 PRÓXIMOS PASSOS:")
        logger.info("1. Conectar Power BI ao PostgreSQL usando as credenciais acima")
        logger.info("2. Importar as tabelas listadas")
        logger.info("3. Criar relacionamentos entre funcionarios e outras tabelas")
        logger.info("4. Desenvolver dashboards baseados nos insights gerados")

def main():
    """Função principal"""
    try:
        analytics = BernPeopleAnalytics()
        analytics.run_complete_analysis()
        
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")
        raise

if __name__ == "__main__":
    main()