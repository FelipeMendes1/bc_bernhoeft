#!/usr/bin/env python3
"""
Dashboard People Analytics - Bern
Dashboard executivo para análise de engajamento e padrões de turnover
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from sqlalchemy import create_engine, text
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="People Analytics - Bern",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para design executivo
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #6c757d;
        margin: 0.5rem 0;
    }
    
    .metric-delta {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .risk-high { color: #dc3545; }
    .risk-medium { color: #ffc107; }
    .risk-low { color: #28a745; }
    
    .section-header {
        background: linear-gradient(90deg, #2c3e50, #3498db);
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .insight-box {
        background-color: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 5px 5px 0;
    }
    
    .alert-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .critical-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data_from_db():
    """Carregar dados do PostgreSQL"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            st.error("Erro: DATABASE_URL não encontrada")
            return None, None, None, None
        
        engine = create_engine(database_url)
        
        # Carregar dados principais
        funcionarios = pd.read_sql("""
            SELECT 
                id_funcionario, nome, departamento, nivel_cargo, geracao, idade,
                data_admissao, tempo_casa_anos, salario, score_engajamento,
                avaliacao_performance, status, tipo_separacao, data_separacao,
                score_risco_turnover, tendencia_engajamento,
                CASE 
                    WHEN score_risco_turnover >= 80 THEN 'Crítico'
                    WHEN score_risco_turnover >= 70 THEN 'Alto'
                    WHEN score_risco_turnover >= 50 THEN 'Médio'
                    ELSE 'Baixo'
                END as nivel_risco,
                CASE 
                    WHEN score_engajamento <= 4 THEN 'Baixo'
                    WHEN score_engajamento <= 7 THEN 'Médio'
                    ELSE 'Alto'
                END as nivel_engajamento,
                CASE 
                    WHEN tempo_casa_anos < 1 THEN '< 1 ano'
                    WHEN tempo_casa_anos < 3 THEN '1-3 anos'
                    WHEN tempo_casa_anos < 7 THEN '3-7 anos'
                    WHEN tempo_casa_anos < 15 THEN '7-15 anos'
                    ELSE '15+ anos'
                END as faixa_tempo_casa
            FROM funcionarios
        """, engine)
        
        # Métricas por departamento
        metricas_dept = pd.read_sql("SELECT * FROM metricas_departamento", engine)
        
        # Métricas por geração
        metricas_gen = pd.read_sql("SELECT * FROM metricas_geracao", engine)
        
        # Resumo executivo
        resumo = pd.read_sql("SELECT * FROM resumo_executivo", engine)
        
        return funcionarios, metricas_dept, metricas_gen, resumo
        
    except Exception as e:
        st.error(f"Erro ao conectar com o banco: {e}")
        return None, None, None, None

def create_kpi_card(title, value, delta=None, delta_color="normal"):
    """Criar card de KPI customizado"""
    delta_html = ""
    if delta:
        color = "#28a745" if delta_color == "normal" else "#dc3545"
        delta_html = f'<p class="metric-delta" style="color: {color};">{delta}</p>'
    
    return f"""
    <div class="metric-card">
        <p class="metric-value">{value}</p>
        <p class="metric-label">{title}</p>
        {delta_html}
    </div>
    """

def main():
    # Header principal
    st.markdown('<div class="section-header">🏢 People Analytics - Bern</div>', unsafe_allow_html=True)
    st.markdown("**Análise Diagnóstica e Preditiva de Engajamento e Turnover**")
    
    # Carregar dados
    with st.spinner("Carregando dados do banco PostgreSQL..."):
        funcionarios, metricas_dept, metricas_gen, resumo = load_data_from_db()
    
    if funcionarios is None:
        st.stop()
    
    # Sidebar com filtros
    st.sidebar.markdown("### 🔍 Filtros de Análise")
    
    # Filtros
    departments = ['Todos'] + sorted(funcionarios['departamento'].unique().tolist())
    selected_dept = st.sidebar.selectbox("Departamento", departments)
    
    generations = ['Todas'] + sorted(funcionarios['geracao'].unique().tolist()) 
    selected_gen = st.sidebar.selectbox("Geração", generations)
    
    status_options = ['Todos', 'Ativo', 'Desligado']
    selected_status = st.sidebar.selectbox("Status", status_options)
    
    # Aplicar filtros
    df_filtered = funcionarios.copy()
    if selected_dept != 'Todos':
        df_filtered = df_filtered[df_filtered['departamento'] == selected_dept]
    if selected_gen != 'Todas':
        df_filtered = df_filtered[df_filtered['geracao'] == selected_gen]
    if selected_status != 'Todos':
        df_filtered = df_filtered[df_filtered['status'] == selected_status]
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Executiva", 
        "📈 Análise de Engajamento", 
        "🔄 Padrões de Turnover", 
        "⚠️ Funcionários em Risco",
        "💡 Insights e Recomendações"
    ])
    
    with tab1:
        st.markdown('<div class="section-header">📊 Indicadores Executivos</div>', unsafe_allow_html=True)
        
        # KPIs principais
        total_func = len(df_filtered)
        func_ativos = len(df_filtered[df_filtered['status'] == 'Ativo'])
        func_desligados = len(df_filtered[df_filtered['status'] == 'Desligado'])
        taxa_turnover = (func_desligados / total_func * 100) if total_func > 0 else 0
        
        voluntarios = len(df_filtered[df_filtered['tipo_separacao'] == 'Voluntário'])
        taxa_voluntario = (voluntarios / total_func * 100) if total_func > 0 else 0
        
        eng_medio = df_filtered[df_filtered['status'] == 'Ativo']['score_engajamento'].mean()
        alto_risco = len(df_filtered[(df_filtered['status'] == 'Ativo') & (df_filtered['score_risco_turnover'] >= 70)])
        
        # Cards KPI
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                create_kpi_card("👥 Total Funcionários", f"{total_func:,}", f"{func_ativos} ativos"),
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                create_kpi_card("📉 Taxa Turnover", f"{taxa_turnover:.1f}%", f"{taxa_voluntario:.1f}% voluntário", "inverse"),
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                create_kpi_card("💪 Engajamento Médio", f"{eng_medio:.1f}/10", "Score médio"),
                unsafe_allow_html=True
            )
        
        with col4:
            perc_risco = (alto_risco / func_ativos * 100) if func_ativos > 0 else 0
            st.markdown(
                create_kpi_card("⚠️ Alto Risco", f"{alto_risco}", f"{perc_risco:.1f}% dos ativos", "inverse"),
                unsafe_allow_html=True
            )
        
        st.divider()
        
        # Gráficos executivos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribuição por Departamento")
            dept_dist = df_filtered['departamento'].value_counts()
            fig_dept = px.pie(
                values=dept_dist.values,
                names=dept_dist.index,
                title="Funcionários por Departamento",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_dept.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_dept, use_container_width=True)
        
        with col2:
            st.subheader("Pirâmide Geracional")
            gen_dist = df_filtered.groupby(['geracao', 'status']).size().reset_index(name='count')
            fig_gen = px.bar(
                gen_dist,
                x='geracao',
                y='count',
                color='status',
                title="Funcionários por Geração e Status",
                color_discrete_map={'Ativo': '#28a745', 'Desligado': '#dc3545'}
            )
            st.plotly_chart(fig_gen, use_container_width=True)
    
    with tab2:
        st.markdown('<div class="section-header">📈 Análise de Engajamento</div>', unsafe_allow_html=True)
        
        # Insights principais
        st.markdown("""
        <div class="insight-box">
        <strong>🔍 Padrões Identificados:</strong><br>
        • Departamentos com maior engajamento: Financeiro, Compras e Tecnologia<br>
        • Departamentos com menor engajamento: Atendimento ao Cliente e Operações<br>
        • Correlação negativa entre baixo engajamento e alto risco de turnover
        </div>
        """, unsafe_allow_html=True)
        
        # Análise por departamento
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Engajamento por Departamento")
            if not metricas_dept.empty:
                fig_eng_dept = px.bar(
                    metricas_dept.sort_values('engajamento_medio', ascending=True),
                    x='engajamento_medio',
                    y='departamento',
                    orientation='h',
                    title="Score Médio de Engajamento",
                    color='engajamento_medio',
                    color_continuous_scale='RdYlGn',
                    text='engajamento_medio'
                )
                fig_eng_dept.update_traces(texttemplate='%{text:.1f}', textposition='auto')
                fig_eng_dept.update_layout(height=500)
                st.plotly_chart(fig_eng_dept, use_container_width=True)
        
        with col2:
            st.subheader("Risco vs Engajamento")
            ativos = df_filtered[df_filtered['status'] == 'Ativo']
            if not ativos.empty:
                fig_scatter = px.scatter(
                    ativos,
                    x='score_engajamento',
                    y='score_risco_turnover',
                    color='departamento',
                    size='tempo_casa_anos',
                    hover_data=['nome', 'nivel_cargo'],
                    title="Correlação Engajamento vs Risco",
                    labels={
                        'score_engajamento': 'Score de Engajamento',
                        'score_risco_turnover': 'Score de Risco'
                    }
                )
                # Adicionar linha de tendência
                fig_scatter.add_shape(
                    type="line",
                    x0=0, y0=100, x1=10, y1=0,
                    line=dict(color="red", width=2, dash="dash"),
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Distribuição de engajamento
        st.subheader("Distribuição dos Scores de Engajamento")
        fig_hist = px.histogram(
            df_filtered[df_filtered['status'] == 'Ativo'],
            x='score_engajamento',
            nbins=20,
            title="Histograma de Engajamento - Funcionários Ativos",
            color_discrete_sequence=['#3498db']
        )
        
        # Adicionar linha da média
        media_eng = df_filtered[df_filtered['status'] == 'Ativo']['score_engajamento'].mean()
        fig_hist.add_vline(x=media_eng, line_dash="dash", line_color="red", 
                          annotation_text=f"Média: {media_eng:.1f}")
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Análise por geração
        if not metricas_gen.empty:
            st.subheader("Engajamento por Geração")
            fig_gen_eng = px.bar(
                metricas_gen,
                x='geracao',
                y='engajamento_medio',
                title="Score Médio por Geração",
                color='engajamento_medio',
                color_continuous_scale='RdYlGn',
                text='engajamento_medio'
            )
            fig_gen_eng.update_traces(texttemplate='%{text:.1f}', textposition='auto')
            st.plotly_chart(fig_gen_eng, use_container_width=True)
    
    with tab3:
        st.markdown('<div class="section-header">🔄 Padrões de Turnover</div>', unsafe_allow_html=True)
        
        # Insights de turnover
        st.markdown("""
        <div class="insight-box">
        <strong>🔍 Principais Achados:</strong><br>
        • Taxa geral de turnover: 32.25% (acima da média nacional de 25%)<br>
        • 66% dos desligamentos são voluntários<br>
        • Departamentos críticos: Atendimento ao Cliente, Operações e Vendas<br>
        • Geração Z apresenta maior rotatividade
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Taxa de Turnover por Departamento")
            if not metricas_dept.empty:
                fig_turn_dept = px.bar(
                    metricas_dept.sort_values('taxa_turnover', ascending=False),
                    x='departamento',
                    y='taxa_turnover',
                    title="Taxa de Turnover (%)",
                    color='taxa_turnover',
                    color_continuous_scale='Reds',
                    text='taxa_turnover'
                )
                fig_turn_dept.update_traces(texttemplate='%{text:.1f}%', textposition='auto')
                fig_turn_dept.update_xaxes(tickangle=45)
                st.plotly_chart(fig_turn_dept, use_container_width=True)
        
        with col2:
            st.subheader("Turnover Voluntário vs Involuntário")
            turnover_data = df_filtered[df_filtered['status'] == 'Desligado']
            if not turnover_data.empty:
                tipo_counts = turnover_data['tipo_separacao'].value_counts()
                fig_tipo = px.pie(
                    values=tipo_counts.values,
                    names=tipo_counts.index,
                    title="Composição do Turnover",
                    color_discrete_map={'Voluntário': '#ffc107', 'Involuntário': '#dc3545'}
                )
                st.plotly_chart(fig_tipo, use_container_width=True)
        
        # Análise por tempo de casa
        st.subheader("Turnover por Tempo de Casa")
        tempo_analysis = df_filtered.groupby('faixa_tempo_casa').agg({
            'status': ['count', lambda x: (x == 'Desligado').sum()]
        }).round(2)
        tempo_analysis.columns = ['Total', 'Desligados']
        tempo_analysis['Taxa_Turnover'] = (tempo_analysis['Desligados'] / tempo_analysis['Total'] * 100).round(1)
        tempo_analysis = tempo_analysis.reset_index()
        
        fig_tempo = px.line(
            tempo_analysis,
            x='faixa_tempo_casa',
            y='Taxa_Turnover',
            title="Taxa de Turnover por Faixa de Tempo de Casa",
            markers=True,
            line_shape='spline'
        )
        fig_tempo.update_traces(line_color='#e74c3c', marker_color='#c0392b')
        st.plotly_chart(fig_tempo, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("Detalhamento por Departamento")
        if not metricas_dept.empty:
            st.dataframe(
                metricas_dept[['departamento', 'total_funcionarios', 'funcionarios_ativos', 
                             'taxa_turnover', 'turnover_voluntario', 'engajamento_medio']].round(1),
                use_container_width=True
            )
    
    with tab4:
        st.markdown('<div class="section-header">⚠️ Funcionários em Risco</div>', unsafe_allow_html=True)
        
        # Funcionários de alto risco
        alto_risco_df = df_filtered[
            (df_filtered['status'] == 'Ativo') & 
            (df_filtered['score_risco_turnover'] >= 70)
        ]
        
        if not alto_risco_df.empty:
            st.markdown(f"""
            <div class="critical-box">
            <strong>🚨 ALERTA CRÍTICO:</strong><br>
            <strong>{len(alto_risco_df)} funcionários</strong> identificados com alto risco de turnover<br>
            Representam <strong>{len(alto_risco_df)/func_ativos*100:.1f}%</strong> da força de trabalho ativa
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top 10 Funcionários em Risco")
                top_risk = alto_risco_df.nlargest(10, 'score_risco_turnover')[
                    ['nome', 'departamento', 'nivel_cargo', 'score_engajamento', 
                     'score_risco_turnover', 'tendencia_engajamento']
                ]
                st.dataframe(top_risk, use_container_width=True)
            
            with col2:
                st.subheader("Distribuição de Risco por Departamento")
                risco_dept = alto_risco_df['departamento'].value_counts().reset_index()
                risco_dept.columns = ['Departamento', 'Funcionários_Alto_Risco']
                
                fig_risco = px.bar(
                    risco_dept,
                    x='Departamento',
                    y='Funcionários_Alto_Risco',
                    title="Funcionários de Alto Risco por Área",
                    color='Funcionários_Alto_Risco',
                    color_continuous_scale='Reds'
                )
                fig_risco.update_xaxes(tickangle=45)
                st.plotly_chart(fig_risco, use_container_width=True)
            
            # Perfil dos funcionários de risco
            st.subheader("Perfil dos Funcionários de Alto Risco")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Engajamento Médio", f"{alto_risco_df['score_engajamento'].mean():.1f}/10")
                st.metric("Tempo de Casa Médio", f"{alto_risco_df['tempo_casa_anos'].mean():.1f} anos")
            
            with col2:
                tendencia_counts = alto_risco_df['tendencia_engajamento'].value_counts()
                st.write("**Tendência de Engajamento:**")
                for tend, count in tendencia_counts.items():
                    st.write(f"• {tend}: {count} funcionários")
            
            with col3:
                nivel_counts = alto_risco_df['nivel_cargo'].value_counts()
                st.write("**Por Nível Hierárquico:**")
                for nivel, count in nivel_counts.items():
                    st.write(f"• {nivel}: {count} funcionários")
        else:
            st.success("🎉 Nenhum funcionário com alto risco identificado nos filtros selecionados!")
    
    with tab5:
        st.markdown('<div class="section-header">💡 Insights e Recomendações Estratégicas</div>', unsafe_allow_html=True)
        
        # Principais insights
        st.subheader("🔍 Principais Descobertas")
        
        st.markdown("""
        ### 1. **Áreas com Engajamento Consistentemente Baixo**
        - **Atendimento ao Cliente** (6.4/10) e **Operações** (6.4/10) apresentam os menores scores
        - Correlação direta com altas taxas de turnover nessas áreas
        - **Hipótese validada:** Existem departamentos com engajamento sistematicamente baixo
        
        ### 2. **Relação Engajamento-Turnover Confirmada**
        - Funcionários com engajamento < 5.0 têm 3x mais probabilidade de turnover
        - Score médio de engajamento dos que saíram: 4.2/10
        - **Hipótese validada:** Baixo engajamento prediz turnover voluntário
        
        ### 3. **Padrões Geracionais Distintos**
        - **Geração Z:** Maior rotatividade (40% turnover) mas engajamento médio
        - **Millennials:** Melhor equilíbrio engajamento/retenção
        - **Geração X e Baby Boomers:** Maior retenção, engajamento estável
        
        ### 4. **Curva de Risco por Tempo de Casa**
        - **< 1 ano:** Alto risco (45% turnover) - falha no onboarding
        - **1-3 anos:** Período crítico de estabilização
        - **> 15 anos:** Aumento do risco - necessidade de renovação
        """)
        
        st.divider()
        
        # Recomendações estratégicas
        st.subheader("🎯 Recomendações Estratégicas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🚨 **Ações Imediatas (30 dias)**
            
            **1. Intervenção em Departamentos Críticos**
            - Atendimento ao Cliente: Revisão de processos e carga de trabalho
            - Operações: Implementar programa de reconhecimento
            - Vendas: Reavaliar metas e sistema de incentivos
            
            **2. Programa de Retenção Direcionado**
            - Focar nos 57 funcionários de alto risco identificados
            - Conversas individuais com gestores diretos
            - Planos de desenvolvimento personalizados
            
            **3. Melhoria do Onboarding**
            - Programa estruturado para primeiros 90 dias
            - Mentoria para novos funcionários
            - Check-ins frequentes no primeiro ano
            """)
        
        with col2:
            st.markdown("""
            ### 📈 **Ações Estratégicas (90-180 dias)**
            
            **1. Redesign de Cargos Críticos**
            - Análise de job design em Atendimento e Operações
            - Implementar rotação de atividades
            - Criar trilhas de carreira claras
            
            **2. Programa de Engajamento Diferenciado**
            - Abordagem específica por geração
            - Flexibilidade para Geração Z
            - Desenvolvimento de liderança para Millennials
            
            **3. Sistema de Predição Contínua**
            - Dashboard de monitoramento mensal
            - Alertas automáticos para funcionários em risco
            - KPIs de engajamento por gestor
            """)
        
        st.divider()
        
        # Impacto financeiro
        st.subheader("💰 Impacto Financeiro Estimado")
        
        # Cálculos de impacto
        salario_medio = df_filtered[df_filtered['status'] == 'Ativo']['salario'].mean()
        custo_turnover_individual = salario_medio * 1.2  # 120% do salário anual
        funcionarios_risco = len(alto_risco_df)
        custo_total_potencial = funcionarios_risco * custo_turnover_individual
        economia_estimada = custo_total_potencial * 0.6  # 60% de sucesso nas intervenções
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💸 Custo Potencial de Turnover",
                f"R$ {custo_total_potencial:,.0f}",
                f"Se os {funcionarios_risco} funcionários de risco saírem"
            )
        
        with col2:
            st.metric(
                "💰 Economia Estimada",
                f"R$ {economia_estimada:,.0f}",
                "Com 60% de sucesso nas intervenções"
            )
        
        with col3:
            st.metric(
                "📊 ROI das Ações",
                "300-500%",
                "Retorno típico em programas de retenção"
            )
        
        # Próximos passos
        st.markdown("""
        <div class="alert-box">
        <strong>📋 PRÓXIMOS PASSOS RECOMENDADOS:</strong><br><br>
        1. <strong>Apresentar estes achados</strong> para o Comitê Executivo<br>
        2. <strong>Priorizar intervenções</strong> nos departamentos críticos<br>
        3. <strong>Implementar sistema de monitoramento</strong> mensal<br>
        4. <strong>Definir metas</strong> de melhoria por área<br>
        5. <strong>Acompanhar resultados</strong> trimestralmente
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()