import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Import custom modules
from data_generator import generate_employee_data, calculate_additional_metrics
from analytics import PeopleAnalytics
from predictive_model import TurnoverPredictor

# Page configuration
st.set_page_config(
    page_title="Dashboard People Analytics - Bern",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .highlight-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .risk-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the employee data"""
    return generate_employee_data(800)

@st.cache_data
def get_analytics_data(df):
    """Get analytics data and cache it"""
    analytics = PeopleAnalytics(df)
    return analytics

def main():
    # Header
    st.title("🏢 Dashboard People Analytics - Bern")
    st.markdown("**Análise de Engajamento e Padrões de Turnover com Insights Preditivos**")
    
    # Load data
    with st.spinner("Carregando dados dos funcionários..."):
        df = load_data()
        analytics = get_analytics_data(df)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filtros")
    
    # Department filter
    departments = ['Todos'] + sorted(df['Departamento'].unique().tolist())
    selected_dept = st.sidebar.selectbox("Departamento", departments)
    
    # Generation filter
    generations = ['Todas'] + sorted(df['Geracao'].unique().tolist())
    selected_gen = st.sidebar.selectbox("Geração", generations)
    
    # Status filter
    status_options = ['Todos', 'Ativo', 'Desligado']
    selected_status = st.sidebar.selectbox("Status", status_options)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_dept != 'Todos':
        filtered_df = filtered_df[filtered_df['Departamento'] == selected_dept]
    if selected_gen != 'Todas':
        filtered_df = filtered_df[filtered_df['Geracao'] == selected_gen]
    if selected_status != 'Todos':
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    
    # Update analytics with filtered data
    filtered_analytics = PeopleAnalytics(filtered_df)
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral", 
        "📈 Análise de Engajamento", 
        "🔄 Análise de Turnover", 
        "🎯 Predição de Risco", 
        "💡 Recomendações"
    ])
    
    with tab1:
        st.header("📊 Indicadores Principais")
        
        # Key metrics
        metrics = filtered_analytics.get_key_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👥 Total de Funcionários",
                value=metrics['total_funcionarios'],
                delta=f"{metrics['funcionarios_ativos']} ativos"
            )
        
        with col2:
            st.metric(
                label="📉 Taxa de Turnover",
                value=f"{metrics['taxa_turnover']}%",
                delta=f"{metrics['taxa_turnover_voluntario']}% voluntário",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                label="💪 Engajamento Médio",
                value=f"{metrics['engajamento_medio']}/10",
                delta="Score médio"
            )
        
        with col4:
            st.metric(
                label="⚠️ Funcionários Alto Risco",
                value=metrics['funcionarios_alto_risco'],
                delta=f"{(metrics['funcionarios_alto_risco']/metrics['funcionarios_ativos']*100):.1f}% do total",
                delta_color="inverse"
            )
        
        st.divider()
        
        # Overview charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribuição por Departamento")
            dept_dist = filtered_df['Departamento'].value_counts()
            fig_dept = px.pie(
                values=dept_dist.values,
                names=dept_dist.index,
                title="Distribuição de Funcionários por Departamento"
            )
            st.plotly_chart(fig_dept, use_container_width=True)
        
        with col2:
            st.subheader("Distribuição por Geração")
            gen_dist = filtered_df['Geracao'].value_counts()
            fig_gen = px.bar(
                x=gen_dist.index,
                y=gen_dist.values,
                title="Funcionários por Geração",
                labels={'x': 'Geração', 'y': 'Número de Funcionários'}
            )
            st.plotly_chart(fig_gen, use_container_width=True)
    
    with tab2:
        st.header("📈 Análise de Engajamento")
        
        # Engagement distribution
        st.subheader("Distribuição dos Scores de Engajamento")
        fig_eng_dist = filtered_analytics.create_engagement_distribution_chart()
        st.plotly_chart(fig_eng_dist, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Engajamento por Departamento")
            dept_engagement = filtered_analytics.engagement_by_department()
            fig_dept_eng = px.bar(
                dept_engagement,
                x='Departamento',
                y='Engajamento_Medio',
                color='Engajamento_Medio',
                title="Score Médio de Engajamento por Departamento",
                color_continuous_scale='RdYlGn'
            )
            fig_dept_eng.update_xaxis(tickangle=45)
            st.plotly_chart(fig_dept_eng, use_container_width=True)
            
            # Show table
            st.dataframe(dept_engagement, use_container_width=True)
        
        with col2:
            st.subheader("Engajamento por Geração")
            gen_engagement = filtered_analytics.engagement_by_generation()
            fig_gen_eng = px.bar(
                gen_engagement,
                x='Geracao',
                y='Engajamento_Medio',
                color='Engajamento_Medio',
                title="Score Médio de Engajamento por Geração",
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_gen_eng, use_container_width=True)
            
            # Show table
            st.dataframe(gen_engagement, use_container_width=True)
        
        # Tenure analysis
        st.subheader("Engajamento por Tempo de Casa")
        tenure_engagement = filtered_analytics.tenure_engagement_analysis()
        fig_tenure = px.line(
            tenure_engagement,
            x='Grupo_Tempo_Casa',
            y='Engajamento_Medio',
            title="Engajamento por Tempo de Casa",
            markers=True
        )
        st.plotly_chart(fig_tenure, use_container_width=True)
        
        # Correlation analysis
        st.subheader("Análise de Correlações")
        corr_matrix = filtered_analytics.correlation_analysis()
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="Matriz de Correlação - Variáveis Principais",
            color_continuous_scale='RdBu'
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    with tab3:
        st.header("🔄 Análise de Turnover")
        
        # Turnover analysis
        turnover_data = filtered_analytics.turnover_analysis()
        
        if not turnover_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Taxa de Turnover por Departamento")
                fig_turnover = px.bar(
                    turnover_data,
                    x='Departamento',
                    y='Taxa_Turnover',
                    color='Taxa_Turnover',
                    title="Taxa de Turnover (%)",
                    color_continuous_scale='Reds'
                )
                fig_turnover.update_xaxis(tickangle=45)
                st.plotly_chart(fig_turnover, use_container_width=True)
            
            with col2:
                st.subheader("Percentual de Turnover Voluntário")
                fig_voluntary = px.bar(
                    turnover_data,
                    x='Departamento',
                    y='Perc_Voluntario',
                    color='Perc_Voluntario',
                    title="% Turnover Voluntário",
                    color_continuous_scale='Oranges'
                )
                fig_voluntary.update_xaxis(tickangle=45)
                st.plotly_chart(fig_voluntary, use_container_width=True)
            
            # Turnover table
            st.subheader("Detalhamento por Departamento")
            st.dataframe(turnover_data, use_container_width=True)
        else:
            st.info("Nenhum dado de turnover encontrado para os filtros selecionados.")
        
        # Turnover by generation
            
        separated_df = filtered_df[filtered_df['Status'] == 'Desligado']
        if not separated_df.empty:
            st.subheader("Turnover por Geração")
            gen_turnover = separated_df.groupby('Geracao').size().reset_index(name='Desligamentos')
            total_by_gen = filtered_df.groupby('Geracao').size().reset_index(name='Total')
            gen_turnover = gen_turnover.merge(total_by_gen, on='Geracao')
            gen_turnover['Taxa_Turnover'] = (gen_turnover['Desligamentos'] / gen_turnover['Total'] * 100).round(1)
            
            fig_gen_turnover = px.bar(
                gen_turnover,
                x='Geracao',
                y='Taxa_Turnover',
                title="Taxa de Turnover por Geração (%)"
            )
            st.plotly_chart(fig_gen_turnover, use_container_width=True)
    
    with tab4:
        st.header("🎯 Predição de Risco de Turnover")
        
        # Train predictive model
        with st.spinner("Treinando modelo preditivo..."):
            predictor = TurnoverPredictor(df)
            model_performance = predictor.train_model()
        
        # Model performance
        st.subheader("Performance do Modelo")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "AUC Score",
                f"{model_performance['auc_score']:.3f}",
                "Score de qualidade do modelo"
            )
        
        with col2:
            precision = model_performance['classification_report']['1']['precision']
            st.metric(
                "Precisão",
                f"{precision:.3f}",
                "Acurácia das predições positivas"
            )
        
        with col3:
            recall = model_performance['classification_report']['1']['recall']
            st.metric(
                "Recall",
                f"{recall:.3f}",
                "Capacidade de detectar turnover"
            )
        
        # Feature importance
        st.subheader("Importância dos Fatores")
        feature_importance = predictor.get_feature_importance()
        
        # Translate feature names to Portuguese
        feature_translations = {
            'Score_Engajamento': 'Score de Engajamento',
            'Avaliacao_Performance': 'Avaliação de Performance',
            'Tempo_Casa_Anos': 'Tempo de Casa (Anos)',
            'Idade': 'Idade',
            'Salario': 'Salário',
            'Departamento': 'Departamento',
            'Nivel_Cargo': 'Nível do Cargo',
            'Geracao': 'Geração'
        }
        
        feature_importance['feature_pt'] = feature_importance['feature'].map(
            lambda x: feature_translations.get(x, x)
        )
        
        fig_importance = px.bar(
            feature_importance.head(8),
            x='importance',
            y='feature_pt',
            orientation='h',
            title="Fatores Mais Importantes para Predição de Turnover"
        )
        fig_importance.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_importance, use_container_width=True)
        
        # Risk vs Engagement scatter
        st.subheader("Relação Risco vs Engajamento")
        fig_scatter = filtered_analytics.create_risk_vs_engagement_scatter()
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # High risk employees
        st.subheader("⚠️ Funcionários de Alto Risco")
        high_risk_employees = filtered_analytics.get_high_risk_employees(risk_threshold=70)
        
        if not high_risk_employees.empty:
            st.markdown(f"**{len(high_risk_employees)} funcionários** com score de risco > 70")
            
            # Show top 10 highest risk
            st.dataframe(
                high_risk_employees.head(10)[
                    ['Nome', 'Departamento', 'Nivel_Cargo', 'Score_Engajamento', 
                     'Score_Risco_Turnover', 'Tendencia_Engajamento']
                ],
                use_container_width=True
            )
            
            # Risk distribution
            st.subheader("Distribuição de Risco por Departamento")
            risk_by_dept = high_risk_employees.groupby('Departamento').size().reset_index(name='Funcionarios_Alto_Risco')
            fig_risk_dist = px.bar(
                risk_by_dept,
                x='Departamento',
                y='Funcionarios_Alto_Risco',
                title="Número de Funcionários de Alto Risco por Departamento"
            )
            fig_risk_dist.update_xaxis(tickangle=45)
            st.plotly_chart(fig_risk_dist, use_container_width=True)
        else:
            st.success("🎉 Nenhum funcionário com alto risco de turnover identificado!")
    
    with tab5:
        st.header("💡 Recomendações Estratégicas")
        
        # Calculate retention impact
        predictor = TurnoverPredictor(df)
        predictor.train_model()
        retention_impact = predictor.calculate_retention_impact()
        
        # Impact metrics
        st.subheader("💰 Impacto Financeiro Potencial")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Funcionários Alto Risco",
                retention_impact['funcionarios_alto_risco'],
                "Requerem atenção imediata"
            )
        
        with col2:
            st.metric(
                "Economia Potencial",
                f"R$ {retention_impact['economia_estimada_intervencoes']:,.0f}",
                f"Com {retention_impact['taxa_sucesso_estimada']:.0f}% de sucesso"
            )
        
        with col3:
            st.metric(
                "Custo Médio Turnover",
                f"R$ {retention_impact['custo_medio_turnover']:,.0f}",
                "Por funcionário perdido"
            )
        
        # Generate recommendations
        high_risk_employees = analytics.get_high_risk_employees(risk_threshold=70)
        recommendations = predictor.generate_retention_recommendations(high_risk_employees)
        
        if recommendations:
            st.subheader("🎯 Recomendações por Departamento")
            
            for rec in recommendations:
                with st.expander(f"📋 {rec['departamento']} - {rec['funcionarios_risco']} funcionários em risco"):
                    st.markdown(f"**Ação Principal:** {rec.get('acao_principal', 'Ações gerais de retenção')}")
                    st.markdown(f"**Engajamento Médio:** {rec['engajamento_medio']:.1f}/10")
                    st.markdown(f"**Tempo de Casa Médio:** {rec['tempo_casa_medio']:.1f} anos")
                    
                    if 'acoes_especificas' in rec:
                        st.markdown("**Ações Específicas Recomendadas:**")
                        for acao in rec['acoes_especificas']:
                            st.markdown(f"• {acao}")
        
        # General recommendations
        st.subheader("📋 Recomendações Gerais")
        
        # Analyze patterns for general recommendations
        active_employees = df[df['Status'] == 'Ativo']
        
        st.markdown("### 🔍 Principais Insights e Ações")
        
        # Low engagement departments
        dept_engagement = analytics.engagement_by_department()
        low_engagement_depts = dept_engagement[dept_engagement['Engajamento_Medio'] < 6.5]
        
        if not low_engagement_depts.empty:
            st.markdown("#### ⚠️ Departamentos com Baixo Engajamento")
            for _, dept in low_engagement_depts.iterrows():
                st.markdown(
                    f"• **{dept['Departamento']}**: Engajamento {dept['Engajamento_Medio']:.1f}/10 "
                    f"({dept['Funcionarios']} funcionários)"
                )
        
        # Generation insights
        gen_analysis = analytics.engagement_by_generation()
        st.markdown("#### 👥 Insights por Geração")
        
        for _, gen in gen_analysis.iterrows():
            if gen['Risco_Medio'] > 50:
                st.markdown(
                    f"• **{gen['Geracao']}**: Risco médio elevado ({gen['Risco_Medio']:.1f}), "
                    f"Engajamento {gen['Engajamento_Medio']:.1f}/10"
                )
        
        # Action plan
        st.markdown("### 📋 Plano de Ação Sugerido")
        
        st.markdown("""
        **Curto Prazo (1-3 meses):**
        • Implementar conversas individuais com funcionários de alto risco
        • Revisar e melhorar processos nos departamentos com maior turnover
        • Iniciar pesquisa de clima organizacional detalhada
        
        **Médio Prazo (3-6 meses):**
        • Desenvolver programas de engajamento específicos por departamento
        • Implementar programas de mentoria e desenvolvimento
        • Revisar políticas de remuneração e benefícios
        
        **Longo Prazo (6-12 meses):**
        • Criar trilhas de carreira claras para todas as posições
        • Implementar sistema contínuo de feedback e reconhecimento
        • Desenvolver programa de mobilidade interna
        """)
        
        # Export recommendations
        if st.button("📊 Exportar Relatório de Recomendações"):
            # Create summary report
            report_data = {
                'Departamento': [],
                'Funcionarios_Risco': [],
                'Engajamento_Medio': [],
                'Acao_Principal': []
            }
            
            for rec in recommendations:
                report_data['Departamento'].append(rec['departamento'])
                report_data['Funcionarios_Risco'].append(rec['funcionarios_risco'])
                report_data['Engajamento_Medio'].append(rec['engajamento_medio'])
                report_data['Acao_Principal'].append(rec.get('acao_principal', 'Ações gerais'))
            
            if report_data['Departamento']:
                report_df = pd.DataFrame(report_data)
                csv = report_df.to_csv(index=False, encoding='utf-8')
                st.download_button(
                    label="📥 Baixar Relatório CSV",
                    data=csv,
                    file_name=f"relatorio_recomendacoes_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
