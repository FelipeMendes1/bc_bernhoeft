import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

class TurnoverPredictor:
    def __init__(self, df):
        self.df = df
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.feature_importance = None
        
    def prepare_data(self):
        """Prepare data for machine learning model"""
        # Create target variable (1 for separated, 0 for active)
        df_model = self.df.copy()
        df_model['Turnover'] = (df_model['Status'] == 'Desligado').astype(int)
        
        # Select features for modeling
        feature_columns = [
            'Score_Engajamento', 'Avaliacao_Performance', 'Tempo_Casa_Anos',
            'Idade', 'Salario', 'Departamento', 'Nivel_Cargo', 'Geracao'
        ]
        
        # Handle missing values
        df_model = df_model.dropna(subset=feature_columns + ['Turnover'])
        
        X = df_model[feature_columns].copy()
        y = df_model['Turnover']
        
        # Encode categorical variables
        categorical_cols = ['Departamento', 'Nivel_Cargo', 'Geracao']
        
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col])
            self.label_encoders[col] = le
        
        return X, y, df_model
    
    def train_model(self):
        """Train the turnover prediction model"""
        X, y, df_model = self.prepare_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale numerical features
        numerical_cols = ['Score_Engajamento', 'Avaliacao_Performance', 'Tempo_Casa_Anos', 'Idade', 'Salario']
        
        self.scaler = StandardScaler()
        X_train_scaled = X_train.copy()
        X_test_scaled = X_test.copy()
        
        X_train_scaled[numerical_cols] = self.scaler.fit_transform(X_train[numerical_cols])
        X_test_scaled[numerical_cols] = self.scaler.transform(X_test[numerical_cols])
        
        # Train Random Forest model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Store model performance
        self.model_performance = {
            'auc_score': auc_score,
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
        
        return self.model_performance
    
    def predict_turnover_probability(self, employee_data):
        """Predict turnover probability for given employees"""
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Prepare data same way as training
        X = employee_data.copy()
        
        # Encode categorical variables using fitted encoders
        for col, encoder in self.label_encoders.items():
            if col in X.columns:
                # Handle new categories by assigning them to the most frequent class
                X[col] = X[col].apply(lambda x: x if x in encoder.classes_ else encoder.classes_[0])
                X[col] = encoder.transform(X[col])
        
        # Scale numerical features
        numerical_cols = ['Score_Engajamento', 'Avaliacao_Performance', 'Tempo_Casa_Anos', 'Idade', 'Salario']
        existing_numerical_cols = [col for col in numerical_cols if col in X.columns]
        
        if existing_numerical_cols:
            X[existing_numerical_cols] = self.scaler.transform(X[existing_numerical_cols])
        
        # Make predictions
        probabilities = self.model.predict_proba(X)[:, 1]
        
        return probabilities
    
    def get_feature_importance(self):
        """Get feature importance from trained model"""
        if self.feature_importance is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        return self.feature_importance
    
    def generate_retention_recommendations(self, high_risk_employees):
        """Generate retention recommendations based on high-risk employee profiles"""
        if high_risk_employees.empty:
            return []
        
        recommendations = []
        
        # Analyze patterns in high-risk employees
        risk_patterns = high_risk_employees.groupby('Departamento').agg({
            'Score_Engajamento': 'mean',
            'Tempo_Casa_Anos': 'mean',
            'Nome': 'count'
        }).round(2)
        
        risk_patterns.columns = ['Engajamento_Medio', 'Tempo_Casa_Medio', 'Num_Funcionarios_Risco']
        risk_patterns = risk_patterns[risk_patterns['Num_Funcionarios_Risco'] >= 2]  # At least 2 employees
        
        for dept in risk_patterns.index:
            dept_data = risk_patterns.loc[dept]
            
            recommendation = {
                'departamento': dept,
                'funcionarios_risco': int(dept_data['Num_Funcionarios_Risco']),
                'engajamento_medio': dept_data['Engajamento_Medio'],
                'tempo_casa_medio': dept_data['Tempo_Casa_Medio']
            }
            
            # Generate specific recommendations based on patterns
            if dept_data['Engajamento_Medio'] < 6:
                recommendation['acao_principal'] = 'Foco em melhoria do engajamento'
                recommendation['acoes_especificas'] = [
                    'Implementar pesquisas de clima organizacional',
                    'Revisar processos e ferramentas de trabalho',
                    'Aumentar frequência de feedback e reconhecimento'
                ]
            
            if dept_data['Tempo_Casa_Medio'] < 2:
                recommendation['acao_principal'] = 'Melhoria do processo de onboarding'
                recommendation['acoes_especificas'] = [
                    'Revisar programa de integração',
                    'Implementar mentoria para novos funcionários',
                    'Aumentar suporte nos primeiros meses'
                ]
            
            if dept_data['Tempo_Casa_Medio'] > 10:
                recommendation['acao_principal'] = 'Renovação e desenvolvimento de carreira'
                recommendation['acoes_especificas'] = [
                    'Criar planos de desenvolvimento individual',
                    'Oferecer novas oportunidades e desafios',
                    'Implementar programas de mobilidade interna'
                ]
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def calculate_retention_impact(self):
        """Calculate potential impact of retention initiatives"""
        active_employees = self.df[self.df['Status'] == 'Ativo']
        high_risk_count = len(active_employees[active_employees['Score_Risco_Turnover'] > 70])
        
        # Estimate costs (these would be company-specific)
        avg_salary = active_employees['Salario'].mean()
        
        # Typical turnover cost is 50-200% of annual salary
        turnover_cost_per_employee = avg_salary * 1.2  # 120% of annual salary
        
        potential_cost_savings = high_risk_count * turnover_cost_per_employee
        
        # If we can retain 60% of high-risk employees through interventions
        retention_success_rate = 0.6
        estimated_savings = potential_cost_savings * retention_success_rate
        
        return {
            'funcionarios_alto_risco': high_risk_count,
            'custo_medio_turnover': turnover_cost_per_employee,
            'economia_potencial_total': potential_cost_savings,
            'economia_estimada_intervencoes': estimated_savings,
            'taxa_sucesso_estimada': retention_success_rate * 100
        }
