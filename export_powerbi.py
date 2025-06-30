#!/usr/bin/env python3
"""
Script para exportar dados do PostgreSQL para arquivos CSV/Excel
Para importação direta no Power BI - People Analytics Bern
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def export_data_for_powerbi():
    """Exportar dados estruturados para Power BI"""
    try:
        # Conectar ao banco
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL não encontrada nas variáveis de ambiente")
        
        engine = create_engine(database_url)
        logger.info("Conectado ao banco PostgreSQL com sucesso!")
        
        # 1. DADOS PRINCIPAIS DOS FUNCIONÁRIOS
        logger.info("Exportando dados principais dos funcionários...")
        funcionarios_query = """
        SELECT 
            id_funcionario,
            nome,
            departamento,
            nivel_cargo,
            geracao,
            idade,
            data_admissao,
            tempo_casa_anos,
            salario,
            score_engajamento,
            avaliacao_performance,
            status,
            tipo_separacao,
            data_separacao,
            score_risco_turnover,
            tendencia_engajamento,
            CASE 
                WHEN score_risco_turnover >= 80 THEN 'Crítico'
                WHEN score_risco_turnover >= 70 THEN 'Alto'
                WHEN score_risco_turnover >= 50 THEN 'Médio'
                ELSE 'Baixo'
            END as nivel_risco_categoria,
            CASE 
                WHEN score_engajamento <= 4 THEN 'Baixo'
                WHEN score_engajamento <= 7 THEN 'Médio'
                ELSE 'Alto'
            END as nivel_engajamento_categoria,
            CASE 
                WHEN tempo_casa_anos < 1 THEN '< 1 ano'
                WHEN tempo_casa_anos < 3 THEN '1-3 anos'
                WHEN tempo_casa_anos < 7 THEN '3-7 anos'
                WHEN tempo_casa_anos < 15 THEN '7-15 anos'
                ELSE '15+ anos'
            END as faixa_tempo_casa,
            CASE 
                WHEN idade < 30 THEN '< 30 anos'
                WHEN idade < 40 THEN '30-39 anos'
                WHEN idade < 50 THEN '40-49 anos'
                WHEN idade < 60 THEN '50-59 anos'
                ELSE '60+ anos'
            END as faixa_etaria
        FROM funcionarios
        ORDER BY id_funcionario
        """
        
        df_funcionarios = pd.read_sql(funcionarios_query, engine)
        df_funcionarios.to_csv('dados_funcionarios_bern.csv', index=False, encoding='utf-8')
        df_funcionarios.to_excel('dados_funcionarios_bern.xlsx', index=False)
        
        # 2. MÉTRICAS POR DEPARTAMENTO
        logger.info("Exportando métricas por departamento...")
        metricas_dept_query = """
        SELECT 
            departamento,
            total_funcionarios,
            funcionarios_ativos,
            engajamento_medio,
            risco_medio,
            taxa_turnover,
            turnover_voluntario,
            turnover_involuntario,
            tempo_casa_medio,
            salario_medio,
            ROUND((funcionarios_ativos::DECIMAL / total_funcionarios) * 100, 1) as taxa_retencao,
            CASE 
                WHEN engajamento_medio >= 7.5 THEN 'Alto'
                WHEN engajamento_medio >= 6.5 THEN 'Médio'
                ELSE 'Baixo'
            END as categoria_engajamento,
            CASE 
                WHEN taxa_turnover >= 40 THEN 'Crítico'
                WHEN taxa_turnover >= 25 THEN 'Alto'
                ELSE 'Normal'
            END as categoria_turnover
        FROM metricas_departamento
        ORDER BY engajamento_medio DESC
        """
        
        df_metricas_dept = pd.read_sql(metricas_dept_query, engine)
        df_metricas_dept.to_csv('metricas_departamento_bern.csv', index=False, encoding='utf-8')
        
        # 3. MÉTRICAS POR GERAÇÃO
        logger.info("Exportando métricas por geração...")
        metricas_gen_query = """
        SELECT 
            geracao,
            total_funcionarios,
            funcionarios_ativos,
            engajamento_medio,
            risco_medio,
            taxa_turnover,
            idade_media,
            tempo_casa_medio,
            salario_medio,
            ROUND((funcionarios_ativos::DECIMAL / total_funcionarios) * 100, 1) as taxa_retencao
        FROM metricas_geracao
        ORDER BY idade_media
        """
        
        df_metricas_gen = pd.read_sql(metricas_gen_query, engine)
        df_metricas_gen.to_csv('metricas_geracao_bern.csv', index=False, encoding='utf-8')
        
        # 4. FUNCIONÁRIOS DE ALTO RISCO
        logger.info("Exportando funcionários de alto risco...")
        alto_risco_query = """
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
                WHEN score_risco_turnover >= 80 THEN 'Crítico'
                WHEN score_risco_turnover >= 70 THEN 'Alto'
                ELSE 'Médio'
            END as nivel_risco,
            CASE 
                WHEN score_engajamento <= 4 AND tendencia_engajamento = 'Declinando' THEN 'Intervenção Urgente'
                WHEN score_risco_turnover >= 80 THEN 'Monitoramento Intensivo'
                WHEN score_risco_turnover >= 70 THEN 'Ação Preventiva'
                ELSE 'Acompanhamento Regular'
            END as acao_recomendada
        FROM funcionarios 
        WHERE status = 'Ativo' AND score_risco_turnover >= 70
        ORDER BY score_risco_turnover DESC
        """
        
        df_alto_risco = pd.read_sql(alto_risco_query, engine)
        df_alto_risco.to_csv('funcionarios_alto_risco_bern.csv', index=False, encoding='utf-8')
        
        # 5. ANÁLISE DE CORRELAÇÕES
        logger.info("Exportando análise de correlações...")
        correlacao_query = """
        SELECT 
            id_funcionario,
            departamento,
            nivel_cargo,
            geracao,
            idade,
            tempo_casa_anos,
            salario,
            score_engajamento,
            avaliacao_performance,
            score_risco_turnover,
            status,
            CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END as turnover_flag
        FROM funcionarios
        WHERE score_engajamento IS NOT NULL 
        AND avaliacao_performance IS NOT NULL
        ORDER BY id_funcionario
        """
        
        df_correlacao = pd.read_sql(correlacao_query, engine)
        df_correlacao.to_csv('dados_correlacao_bern.csv', index=False, encoding='utf-8')
        
        # 6. RESUMO EXECUTIVO PARA DASHBOARD
        logger.info("Exportando resumo executivo...")
        resumo_query = """
        SELECT 
            metrica,
            valor,
            descricao,
            categoria
        FROM resumo_executivo
        ORDER BY categoria, metrica
        """
        
        df_resumo = pd.read_sql(resumo_query, engine)
        df_resumo.to_csv('resumo_executivo_bern.csv', index=False, encoding='utf-8')
        
        # 7. ANÁLISE TEMPORAL POR COORTE DE CONTRATAÇÃO
        logger.info("Exportando análise temporal...")
        temporal_query = """
        SELECT 
            EXTRACT(YEAR FROM data_admissao) as ano_contratacao,
            EXTRACT(MONTH FROM data_admissao) as mes_contratacao,
            departamento,
            COUNT(*) as funcionarios_contratados,
            SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END) as ainda_ativos,
            SUM(CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END) as ja_sairam,
            ROUND((SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 1) as taxa_retencao,
            ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_engajamento END), 1) as engajamento_medio_ativos,
            ROUND(AVG(tempo_casa_anos), 1) as tempo_casa_medio
        FROM funcionarios
        WHERE data_admissao >= '2018-01-01'
        GROUP BY 1, 2, 3
        HAVING COUNT(*) >= 2
        ORDER BY 1 DESC, 2 DESC, 3
        """
        
        df_temporal = pd.read_sql(temporal_query, engine)
        df_temporal.to_csv('analise_temporal_bern.csv', index=False, encoding='utf-8')
        
        # 8. MATRIZ DE RISCO VS ENGAJAMENTO
        logger.info("Exportando matriz de risco vs engajamento...")
        matriz_query = """
        SELECT 
            CASE 
                WHEN score_engajamento <= 4 THEN 'Baixo'
                WHEN score_engajamento <= 7 THEN 'Médio'
                ELSE 'Alto'
            END as nivel_engajamento,
            CASE 
                WHEN score_risco_turnover < 50 THEN 'Baixo'
                WHEN score_risco_turnover < 70 THEN 'Médio'
                ELSE 'Alto'
            END as nivel_risco,
            COUNT(*) as funcionarios,
            ROUND(AVG(score_engajamento), 1) as engajamento_medio,
            ROUND(AVG(score_risco_turnover), 1) as risco_medio,
            ROUND(AVG(tempo_casa_anos), 1) as tempo_casa_medio,
            ROUND(AVG(salario)) as salario_medio
        FROM funcionarios 
        WHERE status = 'Ativo'
        GROUP BY 1, 2
        ORDER BY 1, 2
        """
        
        df_matriz = pd.read_sql(matriz_query, engine)
        df_matriz.to_csv('matriz_risco_engajamento_bern.csv', index=False, encoding='utf-8')
        
        # Gerar estatísticas do export
        logger.info("\n" + "="*60)
        logger.info("DADOS EXPORTADOS COM SUCESSO PARA POWER BI!")
        logger.info("="*60)
        logger.info(f"\nArquivos gerados:")
        logger.info(f"1. dados_funcionarios_bern.csv ({len(df_funcionarios)} registros)")
        logger.info(f"2. dados_funcionarios_bern.xlsx ({len(df_funcionarios)} registros)")
        logger.info(f"3. metricas_departamento_bern.csv ({len(df_metricas_dept)} departamentos)")
        logger.info(f"4. metricas_geracao_bern.csv ({len(df_metricas_gen)} gerações)")
        logger.info(f"5. funcionarios_alto_risco_bern.csv ({len(df_alto_risco)} funcionários)")
        logger.info(f"6. dados_correlacao_bern.csv ({len(df_correlacao)} registros)")
        logger.info(f"7. resumo_executivo_bern.csv ({len(df_resumo)} KPIs)")
        logger.info(f"8. analise_temporal_bern.csv ({len(df_temporal)} registros)")
        logger.info(f"9. matriz_risco_engajamento_bern.csv ({len(df_matriz)} combinações)")
        
        # Estatísticas principais
        funcionarios_ativos = len(df_funcionarios[df_funcionarios['status'] == 'Ativo'])
        funcionarios_desligados = len(df_funcionarios[df_funcionarios['status'] == 'Desligado'])
        taxa_turnover = (funcionarios_desligados / len(df_funcionarios) * 100)
        
        logger.info(f"\nEstatísticas principais:")
        logger.info(f"- Total de funcionários: {len(df_funcionarios)}")
        logger.info(f"- Funcionários ativos: {funcionarios_ativos}")
        logger.info(f"- Taxa de turnover: {taxa_turnover:.1f}%")
        logger.info(f"- Funcionários de alto risco: {len(df_alto_risco)}")
        logger.info(f"- Engajamento médio: {df_funcionarios[df_funcionarios['status'] == 'Ativo']['score_engajamento'].mean():.1f}/10")
        
        logger.info(f"\nDepartamentos com maior risco:")
        for dept in df_metricas_dept.nlargest(3, 'taxa_turnover')[['departamento', 'taxa_turnover']].values:
            logger.info(f"- {dept[0]}: {dept[1]:.1f}% turnover")
        
        logger.info("\n" + "="*60)
        logger.info("Próximos passos:")
        logger.info("1. Importar os arquivos CSV/Excel no Power BI")
        logger.info("2. Configurar relacionamentos entre as tabelas")
        logger.info("3. Criar dashboards baseados no case Bern")
        logger.info("4. Implementar as análises sugeridas")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a exportação: {e}")
        return False

if __name__ == "__main__":
    success = export_data_for_powerbi()
    if success:
        print("\n✅ Dados exportados com sucesso para Power BI!")
    else:
        print("\n❌ Erro durante a exportação dos dados.")