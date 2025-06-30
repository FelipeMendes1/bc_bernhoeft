import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PeopleAnalytics:
    def __init__(self, df):
        self.df = df
        self.active_employees = df[df['Status'] == 'Ativo']
        self.separated_employees = df[df['Status'] == 'Desligado']
    
    def get_key_metrics(self):
        total_employees = len(self.df)
        active_employees = len(self.active_employees)
        separated_employees = len(self.separated_employees)
        
        # Turnover rate
        turnover_rate = (separated_employees / total_employees * 100)
        
        # Voluntary turnover rate
        voluntary_separations = len(self.separated_employees[
            self.separated_employees['Tipo_Separacao'] == 'Voluntário'
        ])
        voluntary_turnover_rate = (voluntary_separations / total_employees * 100)
        
        # Average engagement
        avg_engagement = self.active_employees['Score_Engajamento'].mean()
        
        # High risk employees (active with high turnover risk)
        high_risk_employees = len(self.active_employees[
            self.active_employees['Score_Risco_Turnover'] > 70
        ])
        
        # Average tenure
        avg_tenure = self.active_employees['Tempo_Casa_Anos'].mean()
        
        return {
            'total_funcionarios': total_employees,
            'funcionarios_ativos': active_employees,
            'taxa_turnover': round(turnover_rate, 1),
            'taxa_turnover_voluntario': round(voluntary_turnover_rate, 1),
            'engajamento_medio': round(avg_engagement, 1),
            'funcionarios_alto_risco': high_risk_employees,
            'tempo_casa_medio': round(avg_tenure, 1)
        }
    
    def engagement_by_department(self):
        """Analyze engagement by department"""
        dept_analysis = self.active_employees.groupby('Departamento').agg({
            'Score_Engajamento': ['mean', 'std', 'count'],
            'Score_Risco_Turnover': 'mean'
        }).round(2)
        
        dept_analysis.columns = ['Engajamento_Medio', 'Engajamento_DP', 'Funcionarios', 'Risco_Medio']
        dept_analysis = dept_analysis.sort_values('Engajamento_Medio', ascending=False)
        
        return dept_analysis.reset_index()
    
    def engagement_by_generation(self):
        """Analyze engagement by generation"""
        gen_analysis = self.active_employees.groupby('Geracao').agg({
            'Score_Engajamento': ['mean', 'count'],
            'Score_Risco_Turnover': 'mean',
            'Tempo_Casa_Anos': 'mean'
        }).round(2)
        
        gen_analysis.columns = ['Engajamento_Medio', 'Funcionarios', 'Risco_Medio', 'Tempo_Casa_Medio']
        
        return gen_analysis.reset_index()
    
    def turnover_analysis(self):
        """Detailed turnover analysis"""
        if len(self.separated_employees) == 0:
            return pd.DataFrame()
        
        turnover_by_dept = self.df.groupby('Departamento').agg({
            'Status': [
                lambda x: (x == 'Desligado').sum(),
                'count'
            ],
            'Tipo_Separacao': lambda x: (x == 'Voluntário').sum()
        }).round(2)
        
        turnover_by_dept.columns = ['Desligamentos', 'Total', 'Voluntarios']
        turnover_by_dept['Taxa_Turnover'] = (turnover_by_dept['Desligamentos'] / turnover_by_dept['Total'] * 100).round(1)
        turnover_by_dept['Perc_Voluntario'] = (turnover_by_dept['Voluntarios'] / turnover_by_dept['Desligamentos'] * 100).round(1)
        
        return turnover_by_dept.reset_index()
    
    def correlation_analysis(self):
        """Analyze correlations between key variables"""
        numeric_cols = ['Score_Engajamento', 'Avaliacao_Performance', 'Score_Risco_Turnover', 
                       'Tempo_Casa_Anos', 'Idade', 'Salario']
        
        corr_matrix = self.active_employees[numeric_cols].corr()
        
        return corr_matrix
    
    def tenure_engagement_analysis(self):
        """Analyze engagement by tenure groups"""
        # Create tenure groups
        self.active_employees_copy = self.active_employees.copy()
        self.active_employees_copy['Grupo_Tempo_Casa'] = pd.cut(
            self.active_employees_copy['Tempo_Casa_Anos'],
            bins=[0, 1, 3, 7, 15, 100],
            labels=['< 1 ano', '1-3 anos', '3-7 anos', '7-15 anos', '15+ anos']
        )
        
        tenure_analysis = self.active_employees_copy.groupby('Grupo_Tempo_Casa').agg({
            'Score_Engajamento': ['mean', 'count'],
            'Score_Risco_Turnover': 'mean'
        }).round(2)
        
        tenure_analysis.columns = ['Engajamento_Medio', 'Funcionarios', 'Risco_Medio']
        
        return tenure_analysis.reset_index()
    
    def create_engagement_distribution_chart(self):
        """Create engagement score distribution chart"""
        fig = px.histogram(
            self.active_employees,
            x='Score_Engajamento',
            nbins=20,
            title='Distribuição dos Scores de Engajamento',
            labels={'Score_Engajamento': 'Score de Engajamento', 'count': 'Número de Funcionários'}
        )
        
        # Add average line
        avg_engagement = self.active_employees['Score_Engajamento'].mean()
        fig.add_vline(x=avg_engagement, line_dash="dash", line_color="red", 
                     annotation_text=f"Média: {avg_engagement:.1f}")
        
        return fig
    
    def create_department_engagement_chart(self):
        """Create department engagement comparison chart"""
        dept_data = self.engagement_by_department()
        
        fig = px.bar(
            dept_data,
            x='Departamento',
            y='Engajamento_Medio',
            title='Engajamento Médio por Departamento',
            labels={'Engajamento_Medio': 'Score Médio de Engajamento', 'Departamento': 'Departamento'}
        )
        
        fig.update_xaxis(tickangle=45)
        
        return fig
    
    def create_generation_analysis_chart(self):
        """Create generation analysis chart"""
        gen_data = self.engagement_by_generation()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Engajamento por Geração', 'Risco de Turnover por Geração'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Engagement by generation
        fig.add_trace(
            go.Bar(x=gen_data['Geracao'], y=gen_data['Engajamento_Medio'], 
                   name='Engajamento Médio', marker_color='lightblue'),
            row=1, col=1
        )
        
        # Risk by generation
        fig.add_trace(
            go.Bar(x=gen_data['Geracao'], y=gen_data['Risco_Medio'], 
                   name='Risco Médio', marker_color='lightcoral'),
            row=1, col=2
        )
        
        fig.update_layout(title_text="Análise por Geração", showlegend=False)
        
        return fig
    
    def create_turnover_analysis_chart(self):
        """Create turnover analysis chart"""
        turnover_data = self.turnover_analysis()
        
        if turnover_data.empty:
            return go.Figure().add_annotation(text="Sem dados de turnover disponíveis")
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Taxa de Turnover por Departamento', 'Percentual de Turnover Voluntário'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Turnover rate by department
        fig.add_trace(
            go.Bar(x=turnover_data['Departamento'], y=turnover_data['Taxa_Turnover'], 
                   name='Taxa Turnover (%)', marker_color='orange'),
            row=1, col=1
        )
        
        # Voluntary turnover percentage
        fig.add_trace(
            go.Bar(x=turnover_data['Departamento'], y=turnover_data['Perc_Voluntario'], 
                   name='% Voluntário', marker_color='red'),
            row=1, col=2
        )
        
        fig.update_layout(title_text="Análise de Turnover", showlegend=False)
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    def create_risk_vs_engagement_scatter(self):
        """Create scatter plot of risk vs engagement"""
        fig = px.scatter(
            self.active_employees,
            x='Score_Engajamento',
            y='Score_Risco_Turnover',
            color='Departamento',
            size='Tempo_Casa_Anos',
            hover_data=['Nome', 'Nivel_Cargo'],
            title='Relação entre Engajamento e Risco de Turnover',
            labels={
                'Score_Engajamento': 'Score de Engajamento',
                'Score_Risco_Turnover': 'Score de Risco de Turnover',
                'Tempo_Casa_Anos': 'Tempo de Casa (Anos)'
            }
        )
        
        return fig
    
    def get_high_risk_employees(self, risk_threshold=70):
        """Get list of high-risk employees"""
        high_risk = self.active_employees[
            self.active_employees['Score_Risco_Turnover'] > risk_threshold
        ].copy()
        
        # Sort by risk score descending
        high_risk = high_risk.sort_values('Score_Risco_Turnover', ascending=False)
        
        # Select relevant columns
        columns = ['Nome', 'Departamento', 'Nivel_Cargo', 'Score_Engajamento', 
                  'Score_Risco_Turnover', 'Tempo_Casa_Anos', 'Tendencia_Engajamento']
        
        return high_risk[columns]
