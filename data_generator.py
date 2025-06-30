import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

# Configure Faker for Brazilian Portuguese
fake = Faker('pt_BR')

def generate_employee_data(num_employees=800):
    """
    Generate realistic employee dataset for Brazilian company
    """
    
    # Brazilian company departments
    departments = [
        'Tecnologia', 'Recursos Humanos', 'Vendas', 'Marketing', 
        'Financeiro', 'Operações', 'Jurídico', 'Compras',
        'Atendimento ao Cliente', 'Qualidade', 'Logística'
    ]
    
    # Position levels
    position_levels = ['Estagiário', 'Júnior', 'Pleno', 'Sênior', 'Coordenador', 'Gerente', 'Diretor']
    
    # Generations with birth year ranges
    generations = {
        'Geração Z': (1997, 2012),
        'Millennial': (1981, 1996),
        'Geração X': (1965, 1980),
        'Baby Boomer': (1946, 1964)
    }
    
    # Salary bands by position level (in BRL)
    salary_bands = {
        'Estagiário': (1500, 2500),
        'Júnior': (3000, 5000),
        'Pleno': (5500, 8500),
        'Sênior': (9000, 15000),
        'Coordenador': (12000, 20000),
        'Gerente': (18000, 35000),
        'Diretor': (35000, 80000)
    }
    
    employees = []
    
    for i in range(num_employees):
        # Basic info
        employee_id = f"EMP{str(i+1).zfill(4)}"
        name = fake.name()
        department = random.choice(departments)
        position_level = random.choice(position_levels)
        
        # Generation and age calculation
        generation = random.choice(list(generations.keys()))
        birth_year_range = generations[generation]
        birth_year = random.randint(birth_year_range[0], birth_year_range[1])
        current_year = datetime.now().year
        age = current_year - birth_year
        
        # Hire date (tenure calculation)
        max_tenure_years = max(0, min(age - 18, 25))  # Started working at least at 18
        tenure_years = random.randint(0, max(0, max_tenure_years))
        hire_date = datetime.now() - timedelta(days=tenure_years * 365 + random.randint(0, 365))
        
        # Salary based on position level
        salary_range = salary_bands[position_level]
        salary = random.randint(salary_range[0], salary_range[1])
        
        # Engagement scores (1-10 scale)
        # Create some correlation with department and position level
        base_engagement = random.uniform(4, 9)
        
        # Adjust by department (some departments typically have different engagement)
        dept_adjustments = {
            'Tecnologia': 0.3,
            'Marketing': 0.2,
            'Vendas': -0.1,
            'Recursos Humanos': 0.1,
            'Operações': -0.2,
            'Atendimento ao Cliente': -0.3
        }
        
        engagement_adjustment = dept_adjustments.get(department, 0)
        engagement_score = max(1, min(10, base_engagement + engagement_adjustment + random.uniform(-0.5, 0.5)))
        
        # Performance rating (1-5 scale)
        # Correlate with engagement
        performance_base = 2 + (engagement_score / 10) * 3
        performance_rating = max(1, min(5, performance_base + random.uniform(-0.5, 0.5)))
        
        # Turnover status and risk factors
        # Higher risk for lower engagement, newer employees, certain departments
        turnover_risk_score = 0
        
        # Engagement factor (lower engagement = higher risk)
        turnover_risk_score += (10 - engagement_score) * 10
        
        # Tenure factor (very new or very long tenure = higher risk)
        if tenure_years < 1:
            turnover_risk_score += 20
        elif tenure_years > 15:
            turnover_risk_score += 10
        
        # Department factor
        high_turnover_depts = ['Vendas', 'Atendimento ao Cliente', 'Operações']
        if department in high_turnover_depts:
            turnover_risk_score += 15
        
        # Performance factor
        if performance_rating < 3:
            turnover_risk_score += 25
        
        # Generation factor (Gen Z typically has higher turnover)
        if generation == 'Geração Z':
            turnover_risk_score += 10
        
        # Add some randomness
        turnover_risk_score += random.uniform(-10, 10)
        turnover_risk_score = max(0, min(100, turnover_risk_score))
        
        # Determine actual turnover status
        has_left = random.random() < (turnover_risk_score / 150)  # Probability based on risk
        
        if has_left:
            # Determine if voluntary or involuntary
            is_voluntary = random.random() < 0.7  # 70% voluntary
            separation_type = 'Voluntário' if is_voluntary else 'Involuntário'
            # Calculate separation date ensuring it's after hire date but before now
            max_days = max(30, int(tenure_years * 365)) if tenure_years > 0 else 30
            separation_date = hire_date + timedelta(days=random.randint(30, max_days))
            status = 'Desligado'
        else:
            separation_type = None
            separation_date = None
            status = 'Ativo'
        
        # Recent engagement trend (last 3 months vs previous)
        engagement_trend = random.choice(['Melhorando', 'Estável', 'Declinando'])
        if engagement_score < 5:
            engagement_trend = random.choice(['Declinando', 'Estável'])  # Low engagement rarely improving
        elif engagement_score > 8:
            engagement_trend = random.choice(['Melhorando', 'Estável'])  # High engagement rarely declining
        
        employee = {
            'ID_Funcionario': employee_id,
            'Nome': name,
            'Departamento': department,
            'Nivel_Cargo': position_level,
            'Geracao': generation,
            'Idade': age,
            'Data_Admissao': hire_date.strftime('%Y-%m-%d'),
            'Tempo_Casa_Anos': round(tenure_years + random.uniform(0, 1), 1),
            'Salario': salary,
            'Score_Engajamento': round(engagement_score, 1),
            'Avaliacao_Performance': round(performance_rating, 1),
            'Status': status,
            'Tipo_Separacao': separation_type,
            'Data_Separacao': separation_date.strftime('%Y-%m-%d') if separation_date else None,
            'Score_Risco_Turnover': round(turnover_risk_score, 1),
            'Tendencia_Engajamento': engagement_trend
        }
        
        employees.append(employee)
    
    return pd.DataFrame(employees)

def calculate_additional_metrics(df):
    """
    Calculate additional analytics metrics
    """
    # Turnover rate by department
    turnover_by_dept = df.groupby('Departamento').agg({
        'Status': [
            lambda x: (x == 'Desligado').sum(),  # Count of separations
            'count'  # Total count
        ]
    }).round(2)
    
    turnover_by_dept.columns = ['Desligamentos', 'Total_Funcionarios']
    turnover_by_dept['Taxa_Turnover'] = (turnover_by_dept['Desligamentos'] / turnover_by_dept['Total_Funcionarios'] * 100).round(1)
    
    return turnover_by_dept

if __name__ == "__main__":
    # Generate sample data for testing
    df = generate_employee_data(800)
    print("Sample employee data generated:")
    print(df.head())
    print(f"\nDataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
