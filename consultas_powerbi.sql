-- ============================================================
-- CONSULTAS SQL PARA POWER BI - PEOPLE ANALYTICS BERN
-- ============================================================

-- 1. DADOS GERAIS DOS FUNCIONÁRIOS (Para importação principal)
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
    END as faixa_tempo_casa
FROM funcionarios;

-- 2. KPIS PRINCIPAIS (Para cards do dashboard)
SELECT 
    'Total de Funcionários' as kpi,
    COUNT(*)::INTEGER as valor,
    'funcionarios' as unidade
FROM funcionarios
UNION ALL
SELECT 
    'Funcionários Ativos' as kpi,
    COUNT(*)::INTEGER as valor,
    'funcionarios' as unidade
FROM funcionarios WHERE status = 'Ativo'
UNION ALL
SELECT 
    'Taxa de Turnover' as kpi,
    ROUND((COUNT(CASE WHEN status = 'Desligado' THEN 1 END)::DECIMAL / COUNT(*)) * 100, 1)::DECIMAL as valor,
    'percentual' as unidade
FROM funcionarios
UNION ALL
SELECT 
    'Engajamento Médio' as kpi,
    ROUND(AVG(score_engajamento), 1)::DECIMAL as valor,
    'score' as unidade
FROM funcionarios WHERE status = 'Ativo'
UNION ALL
SELECT 
    'Funcionários Alto Risco' as kpi,
    COUNT(*)::INTEGER as valor,
    'funcionarios' as unidade
FROM funcionarios WHERE status = 'Ativo' AND score_risco_turnover >= 70;

-- 3. ANÁLISE POR DEPARTAMENTO (Para gráficos comparativos)
SELECT 
    departamento,
    COUNT(*) as total_funcionarios,
    SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END) as funcionarios_ativos,
    SUM(CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END) as funcionarios_desligados,
    ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_engajamento END), 1) as engajamento_medio,
    ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_risco_turnover END), 1) as risco_medio,
    ROUND((SUM(CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 1) as taxa_turnover,
    SUM(CASE WHEN tipo_separacao = 'Voluntário' THEN 1 ELSE 0 END) as turnover_voluntario,
    ROUND(AVG(CASE WHEN status = 'Ativo' THEN tempo_casa_anos END), 1) as tempo_casa_medio,
    ROUND(AVG(CASE WHEN status = 'Ativo' THEN salario END)) as salario_medio
FROM funcionarios
GROUP BY departamento
ORDER BY engajamento_medio DESC;

-- 4. ANÁLISE POR GERAÇÃO (Para análise demográfica)
SELECT 
    geracao,
    COUNT(*) as total_funcionarios,
    SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END) as funcionarios_ativos,
    ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_engajamento END), 1) as engajamento_medio,
    ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_risco_turnover END), 1) as risco_medio,
    ROUND((SUM(CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 1) as taxa_turnover,
    ROUND(AVG(idade), 1) as idade_media,
    ROUND(AVG(CASE WHEN status = 'Ativo' THEN tempo_casa_anos END), 1) as tempo_casa_medio,
    ROUND(AVG(CASE WHEN status = 'Ativo' THEN salario END)) as salario_medio
FROM funcionarios
GROUP BY geracao
ORDER BY idade_media;

-- 5. FUNCIONÁRIOS DE ALTO RISCO (Para lista detalhada)
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
        ELSE 'Médio'
    END as nivel_risco
FROM funcionarios 
WHERE status = 'Ativo' AND score_risco_turnover >= 70
ORDER BY score_risco_turnover DESC;

-- 6. CORRELAÇÃO ENGAJAMENTO VS PERFORMANCE (Para scatter plot)
SELECT 
    id_funcionario,
    nome,
    departamento,
    nivel_cargo,
    score_engajamento,
    avaliacao_performance,
    score_risco_turnover,
    tempo_casa_anos,
    salario
FROM funcionarios 
WHERE status = 'Ativo'
ORDER BY score_engajamento DESC;

-- 7. DISTRIBUIÇÃO POR TEMPO DE CASA (Para análise de retenção)
SELECT 
    CASE 
        WHEN tempo_casa_anos < 1 THEN '< 1 ano'
        WHEN tempo_casa_anos < 3 THEN '1-3 anos'
        WHEN tempo_casa_anos < 7 THEN '3-7 anos'
        WHEN tempo_casa_anos < 15 THEN '7-15 anos'
        ELSE '15+ anos'
    END as faixa_tempo_casa,
    COUNT(*) as total_funcionarios,
    SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END) as funcionarios_ativos,
    SUM(CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END) as funcionarios_desligados,
    ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_engajamento END), 1) as engajamento_medio,
    ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_risco_turnover END), 1) as risco_medio,
    ROUND((SUM(CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 1) as taxa_turnover
FROM funcionarios
GROUP BY 1
ORDER BY 
    CASE 
        WHEN faixa_tempo_casa = '< 1 ano' THEN 1
        WHEN faixa_tempo_casa = '1-3 anos' THEN 2
        WHEN faixa_tempo_casa = '3-7 anos' THEN 3
        WHEN faixa_tempo_casa = '7-15 anos' THEN 4
        ELSE 5
    END;

-- 8. ANÁLISE DE SALÁRIOS POR NÍVEL (Para análise de equidade)
SELECT 
    nivel_cargo,
    COUNT(*) as funcionarios,
    ROUND(AVG(salario)) as salario_medio,
    ROUND(MIN(salario)) as salario_minimo,
    ROUND(MAX(salario)) as salario_maximo,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY salario)) as q1_salario,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salario)) as mediana_salario,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY salario)) as q3_salario,
    ROUND(AVG(score_engajamento), 1) as engajamento_medio
FROM funcionarios 
WHERE status = 'Ativo'
GROUP BY nivel_cargo
ORDER BY salario_medio DESC;

-- 9. TENDÊNCIA DE ENGAJAMENTO (Para análise temporal)
SELECT 
    tendencia_engajamento,
    COUNT(*) as funcionarios,
    ROUND(AVG(score_engajamento), 1) as engajamento_medio_atual,
    ROUND(AVG(score_risco_turnover), 1) as risco_medio,
    COUNT(CASE WHEN score_risco_turnover >= 70 THEN 1 END) as funcionarios_alto_risco
FROM funcionarios 
WHERE status = 'Ativo'
GROUP BY tendencia_engajamento
ORDER BY engajamento_medio_atual DESC;

-- 10. ANÁLISE DE TURNOVER VOLUNTÁRIO VS INVOLUNTÁRIO
SELECT 
    departamento,
    COUNT(CASE WHEN tipo_separacao = 'Voluntário' THEN 1 END) as turnover_voluntario,
    COUNT(CASE WHEN tipo_separacao = 'Involuntário' THEN 1 END) as turnover_involuntario,
    COUNT(CASE WHEN status = 'Desligado' THEN 1 END) as total_turnover,
    ROUND(
        (COUNT(CASE WHEN tipo_separacao = 'Voluntário' THEN 1 END)::DECIMAL / 
         NULLIF(COUNT(CASE WHEN status = 'Desligado' THEN 1 END), 0)) * 100, 1
    ) as perc_voluntario
FROM funcionarios
GROUP BY departamento
HAVING COUNT(CASE WHEN status = 'Desligado' THEN 1 END) > 0
ORDER BY total_turnover DESC;

-- ============================================================
-- VIEWS ADICIONAIS PARA POWER BI
-- ============================================================

-- View para análise de matriz de risco vs engajamento
CREATE OR REPLACE VIEW matriz_risco_engajamento AS
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
    ROUND(AVG(tempo_casa_anos), 1) as tempo_casa_medio
FROM funcionarios 
WHERE status = 'Ativo'
GROUP BY 1, 2
ORDER BY 1, 2;

-- View para análise de retenção por coorte de contratação
CREATE OR REPLACE VIEW analise_coorte_contratacao AS
SELECT 
    EXTRACT(YEAR FROM data_admissao) as ano_contratacao,
    COUNT(*) as funcionarios_contratados,
    SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END) as ainda_ativos,
    SUM(CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END) as ja_saíram,
    ROUND((SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 1) as taxa_retencao,
    ROUND(AVG(CASE WHEN status = 'Ativo' THEN score_engajamento END), 1) as engajamento_medio_ativos
FROM funcionarios
WHERE data_admissao >= '2015-01-01'  -- Últimos anos apenas
GROUP BY 1
ORDER BY 1 DESC;