# Dashboard People Analytics - Bern

## Overview

This is a People Analytics dashboard built with Streamlit that provides comprehensive HR insights for Brazilian companies. The application features employee data visualization, predictive analytics for turnover risk, and interactive dashboards for HR professionals to make data-driven decisions.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Frontend**: Streamlit-based web application with interactive dashboards
- **Data Layer**: Generated synthetic employee data mimicking real Brazilian company structures
- **Analytics Engine**: Statistical analysis and visualization using Pandas, NumPy, and Plotly
- **Machine Learning**: Predictive modeling for turnover risk using scikit-learn
- **Visualization**: Interactive charts and graphs using Plotly Express and Graph Objects

## Key Components

### 1. Data Generation (`data_generator.py`)
- Generates realistic Brazilian employee datasets using Faker library
- Includes Brazilian-specific elements (departments, salary ranges, generations)
- Creates synthetic data with realistic correlations and patterns
- Supports customizable employee count and demographic distributions

### 2. Analytics Engine (`analytics.py`)
- **PeopleAnalytics Class**: Core analytics functionality
- Calculates key HR metrics (turnover rates, engagement scores, tenure)
- Provides department-wise analysis and demographic breakdowns
- Generates insights for active vs. separated employees

### 3. Predictive Modeling (`predictive_model.py`)
- **TurnoverPredictor Class**: Machine learning model for turnover prediction
- Uses Random Forest and Logistic Regression algorithms
- Features data preprocessing, encoding, and scaling
- Provides feature importance analysis and risk scoring

### 4. Main Application (`app.py`)
- Streamlit web interface with responsive design
- Interactive dashboard with multiple visualization types
- Custom CSS styling for professional appearance
- Real-time analytics and filtering capabilities

## Data Flow

1. **Data Generation**: Synthetic employee data is generated with realistic Brazilian company characteristics
2. **Data Processing**: Raw data is processed through the analytics engine to calculate metrics
3. **Visualization**: Processed data is rendered through Plotly visualizations
4. **Prediction**: Machine learning models analyze patterns to predict turnover risk
5. **Dashboard**: Interactive Streamlit interface presents insights to users

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Plotly**: Interactive visualization (Express and Graph Objects)
- **Scikit-learn**: Machine learning algorithms
- **SciPy**: Statistical analysis

### Data Generation
- **Faker**: Synthetic data generation with Brazilian localization
- **Random/Datetime**: Built-in Python libraries for data generation

### Styling
- Custom CSS for enhanced UI/UX
- Responsive design elements
- Professional dashboard styling

## Deployment Strategy

The application is designed for easy deployment on Replit:

- **Single Entry Point**: `app.py` serves as the main application file
- **Modular Structure**: Components are separated for maintainability
- **Dependency Management**: All required packages are standard Python libraries
- **Configuration**: Streamlit configuration is embedded in the application

To run the application:
1. Install dependencies: `pip install streamlit pandas numpy plotly scikit-learn faker scipy`
2. Run the application: `streamlit run app.py`
3. Access the dashboard through the provided URL

## Changelog

Changelog:
- June 30, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.