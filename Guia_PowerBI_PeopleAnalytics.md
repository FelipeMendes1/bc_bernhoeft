# 📊 Guia de Conexão Power BI - People Analytics Bern

## 🔗 Informações de Conexão PostgreSQL

Para conectar o Power BI ao banco de dados, use as seguintes informações:

- **Host:** ep-round-sound-a5mjdo64.us-east-2.aws.neon.tech
- **Port:** 5432
- **Database:** neondb
- **Username:** neondb_owner
- **Password:** npg_NsgmbIhUt1j6

## 📋 Estrutura do Banco de Dados

### Principais Tabelas

#### 1. `funcionarios` (Tabela Principal)
Contém todos os dados detalhados dos 800 funcionários:
- `id_funcionario`: Identificador único (EMP0001, EMP0002, etc.)
- `nome`: Nome completo do funcionário
- `departamento`: Departamento (Tecnologia, RH, Vendas, etc.)
- `nivel_cargo`: Nível hierárquico (Estagiário, Júnior, Pleno, Sênior, etc.)
- `geracao`: Geração (Geração Z, Millennial, Geração X, Baby Boomer)
- `idade`: Idade atual
- `data_admissao`: Data de contratação
- `tempo_casa_anos`: Tempo de casa em anos
- `salario`: Salário atual em reais
- `score_engajamento`: Score de engajamento (1-10)
- `avaliacao_performance`: Avaliação de performance (1-5)
- `status`: Status atual (Ativo/Desligado)
- `tipo_separacao`: Tipo de desligamento (Voluntário/Involuntário)
- `data_separacao`: Data do desligamento (se aplicável)
- `score_risco_turnover`: Score de risco de turnover (0-100)
- `tendencia_engajamento`: Tendência do engajamento (Melhorando/Estável/Declinando)

#### 2. `metricas_departamento`
Métricas agregadas por departamento:
- `departamento`: Nome do departamento
- `total_funcionarios`: Total de funcionários no departamento
- `funcionarios_ativos`: Funcionários ativos no departamento
- `engajamento_medio`: Score médio de engajamento
- `risco_medio`: Score médio de risco de turnover
- `taxa_turnover`: Taxa de turnover (%)
- `turnover_voluntario`: Número de turnover voluntário
- `turnover_involuntario`: Número de turnover involuntário
- `tempo_casa_medio`: Tempo médio de casa (anos)
- `salario_medio`: Salário médio

#### 3. `metricas_geracao`
Métricas agregadas por geração:
- `geracao`: Nome da geração
- `total_funcionarios`: Total de funcionários na geração
- `funcionarios_ativos`: Funcionários ativos na geração
- `engajamento_medio`: Score médio de engajamento
- `risco_medio`: Score médio de risco de turnover
- `taxa_turnover`: Taxa de turnover (%)
- `idade_media`: Idade média
- `tempo_casa_medio`: Tempo médio de casa
- `salario_medio`: Salário médio

#### 4. `resumo_executivo`
KPIs principais para dashboard executivo:
- `metrica`: Nome da métrica
- `valor`: Valor da métrica
- `descricao`: Descrição da métrica
- `categoria`: Categoria (Geral, Turnover, Engajamento, etc.)

#### 5. `funcionarios_alto_risco` (VIEW)
View com funcionários de alto risco de turnover:
- Todos os campos da tabela funcionários
- `nivel_risco`: Classificação do risco (Baixo/Médio/Alto/Crítico)
- Filtrada para funcionários ativos com score_risco_turnover >= 70

## 📈 KPIs Principais (Dados Atuais)

- **Total de Funcionários:** 800
- **Funcionários Ativos:** 542
- **Taxa de Turnover:** 32.25%
- **Taxa de Turnover Voluntário:** 21.25%
- **Engajamento Médio:** 6.8/10
- **Funcionários Alto Risco:** 57 (10.5% dos ativos)
- **Tempo de Casa Médio:** 9.9 anos
- **Salário Médio:** R$ 17.772

## 🎯 Análises Sugeridas para Power BI

### 1. Dashboard Executivo
**Objetivo:** Visão geral dos principais KPIs
- KPIs em cards destacados
- Gráfico de turnover por departamento
- Distribuição de funcionários por geração
- Evolução do engajamento (usar tendencia_engajamento)

### 2. Análise de Engajamento
**Objetivo:** Identificar padrões de engajamento
- Heatmap de engajamento por departamento vs geração
- Correlação engajamento vs performance
- Distribuição dos scores de engajamento
- Análise por tempo de casa

### 3. Análise de Turnover
**Objetivo:** Compreender os fatores de turnover
- Taxa de turnover por departamento
- Percentual voluntário vs involuntário
- Turnover por geração
- Análise temporal (por tempo de casa)

### 4. Análise Preditiva de Risco
**Objetivo:** Identificar funcionários em risco
- Scatter plot: Engajamento vs Risco de Turnover
- Lista dos funcionários de alto risco
- Distribuição de risco por departamento
- Análise de fatores de risco

### 5. Análise de Perfil Demográfico
**Objetivo:** Entender a composição da força de trabalho
- Pirâmide etária por departamento
- Distribuição salarial
- Análise por nível de cargo
- Tempo de casa vs engajamento

## 💡 Hipóteses para Investigação

### 1. Engajamento por Área
**Hipótese:** "Algumas áreas têm engajamento consistentemente mais baixo"
- **Como validar:** Compare scores médios de engajamento por departamento
- **Visualização:** Gráfico de barras ordenado + tabela com ranking

### 2. Relação Engajamento-Turnover
**Hipótese:** "Baixo engajamento está correlacionado com maior turnover"
- **Como validar:** Análise de correlação + scatter plot
- **Visualização:** Gráfico de dispersão com linha de tendência

### 3. Padrões Geracionais
**Hipótese:** "Diferentes gerações têm padrões distintos de engajamento e turnover"
- **Como validar:** Compare métricas por geração
- **Visualização:** Gráfico de barras agrupadas + heatmap

### 4. "Curva J" do Engajamento
**Hipótese:** "Funcionários muito novos (< 1 ano) e muito antigos (> 15 anos) têm maior risco"
- **Como validar:** Análise por faixas de tempo de casa
- **Visualização:** Gráfico de linha mostrando risco por tempo de casa

### 5. Impacto Salarial
**Hipótese:** "Funcionários com salário abaixo da média do cargo têm maior risco"
- **Como validar:** Compare salário vs média do nível do cargo
- **Visualização:** Box plot por nível de cargo

## 🛠️ Consultas SQL Úteis

### Funcionários de Alto Risco por Departamento
```sql
SELECT 
    departamento,
    COUNT(*) as funcionarios_alto_risco,
    ROUND(AVG(score_engajamento), 1) as engajamento_medio,
    ROUND(AVG(tempo_casa_anos), 1) as tempo_casa_medio
FROM funcionarios_alto_risco
GROUP BY departamento
ORDER BY funcionarios_alto_risco DESC;
```

### Correlação Engajamento vs Performance
```sql
SELECT 
    CASE 
        WHEN score_engajamento <= 4 THEN 'Baixo'
        WHEN score_engajamento <= 7 THEN 'Médio'
        ELSE 'Alto'
    END as nivel_engajamento,
    ROUND(AVG(avaliacao_performance), 2) as performance_media,
    COUNT(*) as funcionarios
FROM funcionarios 
WHERE status = 'Ativo'
GROUP BY 1
ORDER BY performance_media DESC;
```

### Turnover por Tempo de Casa
```sql
SELECT 
    CASE 
        WHEN tempo_casa_anos < 1 THEN '< 1 ano'
        WHEN tempo_casa_anos < 3 THEN '1-3 anos'
        WHEN tempo_casa_anos < 7 THEN '3-7 anos'
        WHEN tempo_casa_anos < 15 THEN '7-15 anos'
        ELSE '15+ anos'
    END as faixa_tempo_casa,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END) as desligados,
    ROUND(
        (SUM(CASE WHEN status = 'Desligado' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 
        1
    ) as taxa_turnover
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
```

## 🎨 Sugestões de Design para Power BI

### Paleta de Cores
- **Engajamento Alto:** Verde (#2E8B57)
- **Engajamento Médio:** Amarelo (#FFD700)
- **Engajamento Baixo:** Vermelho (#DC143C)
- **Risco Alto:** Vermelho intenso (#B22222)
- **Neutro:** Azul corporativo (#4682B4)

### Elementos Visuais
- Use ícones para representar KPIs (👥 📈 ⚠️ 💼)
- Implemente semáforos para indicadores de risco
- Use formatação condicional nas tabelas
- Crie tooltips informativos com contexto adicional

## 📋 Checklist de Implementação

### Preparação dos Dados
- [ ] Conectar Power BI ao PostgreSQL
- [ ] Importar todas as tabelas necessárias
- [ ] Configurar relacionamentos entre tabelas
- [ ] Criar medidas DAX personalizadas

### Dashboards Principais
- [ ] Dashboard Executivo (KPIs + visão geral)
- [ ] Dashboard de Engajamento (análise detalhada)
- [ ] Dashboard de Turnover (padrões e tendências)
- [ ] Dashboard de Risco (funcionários em risco)

### Validação e Testes
- [ ] Verificar consistência dos dados
- [ ] Testar filtros e drill-downs
- [ ] Validar cálculos e métricas
- [ ] Obter feedback dos stakeholders

## 📞 Próximos Passos

1. **Conectar ao Power BI** usando as credenciais fornecidas
2. **Explorar os dados** para entender a estrutura
3. **Criar visualizações** baseadas nas hipóteses sugeridas
4. **Desenvolver insights** sobre padrões de engajamento e turnover
5. **Propor ações** baseadas nos achados dos dados

---

## 📧 Suporte

Para dúvidas sobre a estrutura dos dados ou consultas SQL adicionais, consulte este documento ou analise diretamente as tabelas no banco de dados.

**Última atualização:** 30 de junho de 2025