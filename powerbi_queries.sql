-- ===============================================================
-- CONSULTAS SQL PARA POWER BI - PEOPLE ANALYTICS BERN
-- Queries otimizadas para análise de engajamento e turnover
-- ===============================================================

-- 1. OVERVIEW EXECUTIVO - KPIs PRINCIPAIS
-- ===============================================================
-- Consulta para cards de KPI no dashboard principal
SELECT 
    metrica,
    valor,
    unidade,
    CASE metrica
        WHEN 'Taxa de Turnover' THEN 
            CASE WHEN valor::numeric > 30 THEN 'Alto' 
                 WHEN valor::numeric > 20 THEN 'Médio' 
                 ELSE 'Baixo' END
        WHEN 'Engajamento Médio' THEN
            CASE WHEN valor::numeric >= 7.5 THEN 'Alto'
                 WHEN valor::numeric >= 6.0 THEN 'Médio'
                 ELSE 'Baixo' END
        ELSE 'Normal'
    END as status_indicador
FROM resumo_executivo
ORDER BY 
    CASE metrica
        WHEN 'Total Funcionários' THEN 1
        WHEN 'Funcionários Ativos' THEN 2  
        WHEN 'Taxa de Turnover' THEN 3
        WHEN 'Funcionários Alto Risco' THEN 4
        WHEN 'Engajamento Médio' THEN 5
        ELSE 6
    END;

-- 2. ANÁLISE DE TURNOVER POR DEPARTAMENTO
-- ===============================================================
-- Ranking de departamentos por risco de turnover
SELECT 
    departamento,
    total_funcionarios,
    funcionarios_ativos,
    taxa_turnover,
    engajamento_medio,
    turnover_voluntario,
    turnover_involuntario,
    risco_medio,
    categoria_turnover,
    categoria_engajamento,
    -- Calcular índice de risco combinado
    ROUND(
        (taxa_turnover * 0.6) + 
        ((10 - engajamento_medio) * 10 * 0.4), 
        1
    ) as indice_risco_combinado,
    -- Classificar prioridade de intervenção
    CASE 
        WHEN taxa_turnover > 35 AND engajamento_medio < 6.5 THEN 'Crítico'
        WHEN taxa_turnover > 30 OR engajamento_medio < 6.0 THEN 'Alto'
        WHEN taxa_turnover > 25 OR engajamento_medio < 7.0 THEN 'Médio'
        ELSE 'Baixo'
    END as prioridade_intervencao
FROM metricas_departamento
ORDER BY taxa_turnover DESC;

-- 3. ANÁLISE GERACIONAL DE ENGAJAMENTO
-- ===============================================================
-- Padrões de comportamento por geração
SELECT 
    geracao,
    total_funcionarios,
    funcionarios_ativos,
    taxa_turnover,
    engajamento_medio,
    tempo_casa_medio,
    salario_medio,
    -- Benchmarking geracional
    ROUND(taxa_turnover - (SELECT AVG(taxa_turnover) FROM metricas_geracao), 1) as delta_turnover_vs_media,
    ROUND(engajamento_medio - (SELECT AVG(engajamento_medio) FROM metricas_geracao), 1) as delta_engajamento_vs_media,
    -- Perfil geracional
    CASE 
        WHEN geracao = 'Geração Z' THEN 'Digital Natives - Alta mobilidade'
        WHEN geracao = 'Millennial' THEN 'Propósito-driven - Equilibrio vida/trabalho'
        WHEN geracao = 'Geração X' THEN 'Estabilidade - Crescimento vertical'
        WHEN geracao = 'Baby Boomer' THEN 'Experiência - Mentoria'
    END as perfil_comportamental
FROM metricas_geracao
ORDER BY taxa_turnover DESC;

-- 4. FUNCIONÁRIOS DE ALTO RISCO - ANÁLISE DETALHADA
-- ===============================================================
-- Lista prioritária para intervenção de RH
SELECT 
    id_funcionario,
    nome,
    departamento,
    nivel_cargo,
    geracao,
    idade,
    tempo_casa_anos,
    score_engajamento,
    score_risco_turnover,
    avaliacao_performance,
    nivel_risco,
    acao_recomendada,
    salario,
    -- Fatores de risco identificados
    CASE 
        WHEN score_engajamento < 4 THEN 'Engajamento Crítico'
        WHEN tempo_casa_anos < 1 THEN 'Novo Funcionário'
        WHEN tempo_casa_anos > 15 THEN 'Possível Burnout'
        WHEN avaliacao_performance < 3 THEN 'Performance Baixa'
        ELSE 'Múltiplos Fatores'
    END as principal_fator_risco,
    -- ROI estimado de retenção (baseado no salário)
    ROUND(salario * 1.5) as custo_estimado_substituicao
FROM funcionarios_alto_risco
ORDER BY score_risco_turnover DESC, score_engajamento ASC;

-- 5. CORRELAÇÃO ENGAJAMENTO VS PERFORMANCE
-- ===============================================================
-- Análise para identificar funcionários desengajados com alta performance
SELECT 
    f.departamento,
    f.nivel_cargo,
    COUNT(*) as total_funcionarios,
    ROUND(AVG(f.score_engajamento), 1) as engajamento_medio,
    ROUND(AVG(f.avaliacao_performance), 1) as performance_media,
    -- Identificar perfis específicos
    COUNT(CASE WHEN f.score_engajamento < 6 AND f.avaliacao_performance >= 4 THEN 1 END) as alto_performer_desengajado,
    COUNT(CASE WHEN f.score_engajamento >= 8 AND f.avaliacao_performance < 3 THEN 1 END) as engajado_baixa_performance,
    -- Calcular correlação por grupo
    ROUND(CORR(f.score_engajamento, f.avaliacao_performance)::numeric, 2) as correlacao_eng_perf
FROM funcionarios f
WHERE f.is_ativo = true
GROUP BY f.departamento, f.nivel_cargo
HAVING COUNT(*) >= 5  -- Mínimo de casos para análise
ORDER BY alto_performer_desengajado DESC;

-- 6. ANÁLISE TEMPORAL DE CONTRATAÇÃO E RETENÇÃO
-- ===============================================================
-- Coortes de contratação para identificar padrões temporais
SELECT 
    EXTRACT(YEAR FROM data_contratacao) as ano_contratacao,
    EXTRACT(QUARTER FROM data_contratacao) as trimestre_contratacao,
    COUNT(*) as total_contratados,
    COUNT(CASE WHEN is_ativo = true THEN 1 END) as ainda_ativos,
    ROUND(
        COUNT(CASE WHEN is_ativo = true THEN 1 END) * 100.0 / COUNT(*), 
        1
    ) as taxa_retencao,
    ROUND(AVG(score_engajamento), 1) as engajamento_medio_coorte,
    ROUND(AVG(tempo_casa_anos), 1) as tempo_casa_medio,
    -- Análise de sobrevivência
    COUNT(CASE WHEN is_ativo = false AND tempo_casa_anos < 1 THEN 1 END) as saida_primeiro_ano,
    COUNT(CASE WHEN is_ativo = false AND tempo_casa_anos BETWEEN 1 AND 3 THEN 1 END) as saida_segundo_terceiro_ano
FROM funcionarios
WHERE data_contratacao >= '2020-01-01'  -- Focar nos últimos 5 anos
GROUP BY 
    EXTRACT(YEAR FROM data_contratacao), 
    EXTRACT(QUARTER FROM data_contratacao)
ORDER BY ano_contratacao DESC, trimestre_contratacao DESC;

-- 7. MATRIZ DE RISCO VS ENGAJAMENTO
-- ===============================================================
-- Segmentação para estratégias diferenciadas
SELECT 
    CASE 
        WHEN score_engajamento >= 7.5 THEN 'Alto Engajamento'
        WHEN score_engajamento >= 6.0 THEN 'Médio Engajamento'  
        ELSE 'Baixo Engajamento'
    END as categoria_engajamento,
    CASE 
        WHEN score_risco_turnover >= 70 THEN 'Alto Risco'
        WHEN score_risco_turnover >= 40 THEN 'Médio Risco'
        ELSE 'Baixo Risco'  
    END as categoria_risco,
    COUNT(*) as quantidade_funcionarios,
    ROUND(AVG(salario)) as salario_medio_segmento,
    -- Estratégias recomendadas por quadrante
    CASE 
        WHEN score_engajamento >= 7.5 AND score_risco_turnover < 40 THEN 'Manter e Desenvolver'
        WHEN score_engajamento >= 7.5 AND score_risco_turnover >= 40 THEN 'Investigar Fatores Externos'
        WHEN score_engajamento < 6.0 AND score_risco_turnover >= 70 THEN 'Intervenção Urgente'
        WHEN score_engajamento < 6.0 AND score_risco_turnover < 40 THEN 'Melhorar Engajamento'
        ELSE 'Monitoramento Regular'
    END as estrategia_recomendada
FROM funcionarios
WHERE is_ativo = true
GROUP BY 
    CASE 
        WHEN score_engajamento >= 7.5 THEN 'Alto Engajamento'
        WHEN score_engajamento >= 6.0 THEN 'Médio Engajamento'  
        ELSE 'Baixo Engajamento'
    END,
    CASE 
        WHEN score_risco_turnover >= 70 THEN 'Alto Risco'
        WHEN score_risco_turnover >= 40 THEN 'Médio Risco'
        ELSE 'Baixo Risco'  
    END,
    CASE 
        WHEN score_engajamento >= 7.5 AND score_risco_turnover < 40 THEN 'Manter e Desenvolver'
        WHEN score_engajamento >= 7.5 AND score_risco_turnover >= 40 THEN 'Investigar Fatores Externos'
        WHEN score_engajamento < 6.0 AND score_risco_turnover >= 70 THEN 'Intervenção Urgente'
        WHEN score_engajamento < 6.0 AND score_risco_turnover < 40 THEN 'Melhorar Engajamento'
        ELSE 'Monitoramento Regular'
    END
ORDER BY quantidade_funcionarios DESC;

-- 8. ANÁLISE DE SALÁRIO E RETENÇÃO
-- ===============================================================
-- Investigar se questões salariais influenciam turnover
SELECT 
    departamento,
    nivel_cargo,
    COUNT(*) as total_funcionarios,
    ROUND(AVG(salario)) as salario_medio,
    ROUND(STDDEV(salario)) as desvio_salario,
    ROUND(AVG(CASE WHEN is_ativo = true THEN salario END)) as salario_medio_ativos,
    ROUND(AVG(CASE WHEN is_ativo = false THEN salario END)) as salario_medio_desligados,
    -- Teste de hipótese: salários baixos = maior turnover?
    ROUND(
        AVG(CASE WHEN is_ativo = true THEN salario END) - 
        AVG(CASE WHEN is_ativo = false THEN salario END)
    ) as diferenca_salarial,
    ROUND(
        COUNT(CASE WHEN is_ativo = false THEN 1 END) * 100.0 / COUNT(*), 
        1
    ) as taxa_turnover
FROM funcionarios
GROUP BY departamento, nivel_cargo
HAVING COUNT(*) >= 5
ORDER BY diferenca_salarial DESC;

-- 9. PREDIÇÃO DE RISCO - FATORES COMBINADOS
-- ===============================================================
-- Modelo simples de scoring para identificar padrões preditivos
SELECT 
    f.id_funcionario,
    f.nome,
    f.departamento,
    f.score_engajamento,
    f.tempo_casa_anos,
    f.avaliacao_performance,
    f.score_risco_turnover,
    -- Score preditivo combinado (0-100)
    ROUND(
        (CASE WHEN f.score_engajamento < 5 THEN 25 ELSE 0 END) +
        (CASE WHEN f.tempo_casa_anos < 1 THEN 20 ELSE 0 END) +
        (CASE WHEN f.tempo_casa_anos > 15 THEN 15 ELSE 0 END) +
        (CASE WHEN f.avaliacao_performance < 3 THEN 20 ELSE 0 END) +
        (CASE WHEN f.geracao = 'Geração Z' THEN 10 ELSE 0 END) +
        (CASE WHEN f.departamento IN ('Atendimento ao Cliente', 'Vendas', 'Operações') THEN 10 ELSE 0 END)
    ) as score_preditivo_simples,
    -- Recomendações baseadas no score
    CASE 
        WHEN score_risco_turnover >= 80 THEN '1. Conversa imediata com gestor'
        WHEN score_risco_turnover >= 60 THEN '2. Plano de desenvolvimento individual'
        WHEN score_risco_turnover >= 40 THEN '3. Acompanhamento trimestral'
        ELSE '4. Monitoramento padrão'
    END as acao_prioritaria
FROM funcionarios f
WHERE f.is_ativo = true
ORDER BY f.score_risco_turnover DESC;

-- 10. BENCHMARKING INTERNO - MELHORES PRÁTICAS
-- ===============================================================
-- Identificar departamentos/gestores de referência para replicar práticas
SELECT 
    d1.departamento,
    d1.engajamento_medio,
    d1.taxa_turnover,
    d1.funcionarios_ativos,
    -- Comparar com a média geral
    ROUND(d1.engajamento_medio - avg_geral.eng_medio, 1) as delta_engajamento,
    ROUND(d1.taxa_turnover - avg_geral.turn_medio, 1) as delta_turnover,
    -- Classificação de performance
    CASE 
        WHEN d1.engajamento_medio >= avg_geral.eng_medio AND d1.taxa_turnover <= avg_geral.turn_medio 
        THEN 'Benchmark Positivo'
        WHEN d1.engajamento_medio < avg_geral.eng_medio AND d1.taxa_turnover > avg_geral.turn_medio 
        THEN 'Necessita Melhoria'
        ELSE 'Performance Mista'
    END as classificacao_performance
FROM metricas_departamento d1
CROSS JOIN (
    SELECT 
        AVG(engajamento_medio) as eng_medio,
        AVG(taxa_turnover) as turn_medio
    FROM metricas_departamento
) avg_geral
ORDER BY 
    CASE 
        WHEN d1.engajamento_medio >= avg_geral.eng_medio AND d1.taxa_turnover <= avg_geral.turn_medio 
        THEN 1  -- Benchmark Positivo primeiro
        WHEN d1.engajamento_medio < avg_geral.eng_medio AND d1.taxa_turnover > avg_geral.turn_medio 
        THEN 3  -- Necessita Melhoria por último
        ELSE 2  -- Performance Mista no meio
    END,
    d1.engajamento_medio DESC;