"""
Utility Functions for Smart Solar AI Dashboard
Data processing, analysis, and insights generation
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import streamlit as st

# ============ DATA VALIDATION ============
def validate_solar_data(df):
    """Validate if data contains solar-related columns"""
    solar_columns = [
        'efficiency', 'irradiance', 'temperature', 'power', 'voltage', 
        'current', 'performance', 'generation', 'output', 'capacity'
    ]
    found_cols = [col for col in df.columns if any(solar in col.lower() for solar in solar_columns)]
    return len(found_cols) > 0, found_cols

def validate_file_data(df):
    """Validate uploaded file data"""
    if df is None or len(df) == 0:
        return False, "❌ File is empty!"
    
    if len(df.columns) == 0:
        return False, "❌ No columns found in file!"
    
    if len(df) > 1000000:
        return False, "❌ File too large (max 1M rows)!"
    
    return True, "✅ File validated successfully!"

# ============ DATA CLEANING ============
def clean_data(df):
    """Auto-clean and prepare data"""
    original_rows = len(df)
    original_cols = len(df.columns)
    
    # Remove duplicates
    df = df.drop_duplicates()
    duplicates_removed = original_rows - len(df)
    
    # Handle missing values
    missing_before = df.isnull().sum().sum()
    
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
            df[col].fillna(df[col].median(), inplace=True)
        elif df[col].dtype == 'object':
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col].fillna(mode_val[0], inplace=True)
            else:
                df[col].fillna('Unknown', inplace=True)
    
    missing_after = df.isnull().sum().sum()
    
    # Standardize column names
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '_')
    
    # Remove all-NaN rows
    df = df.dropna(how='all')
    
    return df, {
        'original_rows': original_rows,
        'cleaned_rows': len(df),
        'rows_removed': duplicates_removed,
        'missing_filled': missing_before - missing_after,
        'original_cols': original_cols,
        'final_cols': len(df.columns)
    }

# ============ DATA ANALYSIS ============
def detect_anomalies(df, column, method='zscore', threshold=2.5):
    """Detect anomalies in data"""
    try:
        if column not in df.columns:
            return None, None, 0
        
        data = df[[column]].dropna().values.flatten()
        if len(data) < 10:
            return None, None, 0
        
        mean = np.mean(data)
        std = np.std(data)
        
        if method == 'zscore':
            anomalies_mask = np.abs(data - mean) > (threshold * std)
        elif method == 'iqr':
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            anomalies_mask = (data < (q1 - 1.5 * iqr)) | (data > (q3 + 1.5 * iqr))
        
        anomalies_df = df[anomalies_mask]
        return anomalies_df, anomalies_mask, len(anomalies_df)
    except Exception as e:
        return None, None, 0

def forecast_trend(df, value_col, periods=6):
    """Forecast future values using linear regression"""
    try:
        if value_col not in df.columns:
            return None
        
        df_sorted = df.dropna(subset=[value_col]).copy()
        if len(df_sorted) < 3:
            return None
        
        y = df_sorted[value_col].values
        X = np.arange(len(y))
        
        # Linear regression using numpy
        z = np.polyfit(X, y, 1)
        slope, intercept = z[0], z[1]
        
        # Generate forecast
        future_X = np.arange(len(y), len(y) + periods)
        predictions = slope * future_X + intercept
        
        forecast_df = pd.DataFrame({
            'Period': [f'T+{i+1}' for i in range(periods)],
            'Forecast': predictions,
            'Trend': 'Increasing' if slope > 0 else 'Decreasing'
        })
        
        return forecast_df, slope
    except Exception as e:
        return None, None

def calculate_solar_kpis(df):
    """Calculate solar industry KPIs"""
    kpis = {}
    
    try:
        # Total energy generated
        if 'power' in df.columns or 'generation' in df.columns:
            power_col = 'power' if 'power' in df.columns else 'generation'
            kpis['total_energy'] = df[power_col].sum()
            kpis['avg_power'] = df[power_col].mean()
            kpis['max_power'] = df[power_col].max()
        
        # Efficiency
        if 'efficiency' in df.columns:
            kpis['avg_efficiency'] = df['efficiency'].mean()
            kpis['min_efficiency'] = df['efficiency'].min()
            kpis['max_efficiency'] = df['efficiency'].max()
        
        # Irradiance
        if 'irradiance' in df.columns:
            kpis['avg_irradiance'] = df['irradiance'].mean()
            kpis['total_irradiance'] = df['irradiance'].sum()
        
        # Temperature
        if 'temperature' in df.columns:
            kpis['avg_temperature'] = df['temperature'].mean()
        
        # Performance ratio
        if 'performance' in df.columns:
            kpis['avg_performance'] = df['performance'].mean()
        
        return kpis
    except Exception as e:
        return {}

# ============ AI INSIGHTS ============
def generate_solar_insights(df):
    """Generate insights for solar data"""
    insights = []
    
    try:
        # Data quality
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_pct > 10:
            insights.append(f"⚠️ Data Quality: {missing_pct:.1f}% missing values")
        else:
            insights.append(f"✅ Data Quality: Good ({100-missing_pct:.1f}% complete)")
        
        # Efficiency analysis
        if 'efficiency' in df.columns:
            avg_eff = df['efficiency'].mean()
            if avg_eff < 75:
                insights.append(f"🔴 Low Efficiency: {avg_eff:.1f}% (Below 75% threshold)")
            elif avg_eff < 85:
                insights.append(f"🟡 Moderate Efficiency: {avg_eff:.1f}% (Needs attention)")
            else:
                insights.append(f"🟢 Good Efficiency: {avg_eff:.1f}%")
        
        # Performance trend
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_cols[:3]:
            trend = df[col].diff().mean()
            if trend < 0:
                insights.append(f"📉 {col.title()} Declining: {trend:.2f}/period")
            else:
                insights.append(f"📈 {col.title()} Improving: {trend:.2f}/period")
        
        # Anomalies
        for col in numeric_cols[:2]:
            anomalies_df, _, count = detect_anomalies(df, col)
            if count > 0:
                insights.append(f"🔍 {count} Anomalies Detected in {col.title()}")
        
        return insights if insights else ["✅ Data appears normal"]
    except Exception as e:
        return [f"⚠️ Unable to generate insights: {str(e)}"]

# ============ RECOMMENDATIONS ============
def generate_recommendations(df, kpis=None):
    """Generate actionable recommendations"""
    recommendations = []
    
    try:
        if kpis is None:
            kpis = calculate_solar_kpis(df)
        
        # Efficiency recommendations
        if 'avg_efficiency' in kpis:
            eff = kpis['avg_efficiency']
            if eff < 70:
                recommendations.append({
                    'priority': '🔴 High',
                    'action': 'Schedule Immediate Maintenance',
                    'reason': f'Efficiency {eff:.1f}% is critically low',
                    'savings': 'Potential 15-20% improvement'
                })
            elif eff < 80:
                recommendations.append({
                    'priority': '🟡 Medium',
                    'action': 'Panel Cleaning Recommended',
                    'reason': f'Efficiency {eff:.1f}% could be better',
                    'savings': 'Potential 5-10% improvement'
                })
        
        # Temperature monitoring
        if 'avg_temperature' in kpis:
            temp = kpis['avg_temperature']
            if temp > 60:
                recommendations.append({
                    'priority': '🟡 Medium',
                    'action': 'Improve Cooling System',
                    'reason': f'High temperature {temp:.1f}°C reduces efficiency',
                    'savings': 'Potential 3-5% improvement'
                })
        
        # Performance optimization
        if 'avg_performance' in kpis:
            perf = kpis['avg_performance']
            if perf < 80:
                recommendations.append({
                    'priority': '🟡 Medium',
                    'action': 'Optimize Inverter Settings',
                    'reason': f'Performance ratio {perf:.1f}% below optimal',
                    'savings': 'Potential 2-4% improvement'
                })
        
        # Default recommendations
        if not recommendations:
            recommendations.append({
                'priority': '🟢 Low',
                'action': 'Continue Monitoring',
                'reason': 'System performing within normal parameters',
                'savings': 'Maintain current efficiency'
            })
        
        return recommendations
    except Exception as e:
        return [{'priority': 'ℹ️', 'action': 'Unable to generate recommendations', 'reason': str(e), 'savings': '-'}]

# ============ REPORT GENERATION ============
def prepare_report_data(df, file_metadata, analysis_results=None, recommendations=None):
    """Prepare data for PDF/Excel report"""
    report_data = {
        'metadata': {
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'filename': file_metadata.get('original_filename', 'Unknown'),
            'rows': file_metadata.get('row_count', len(df)),
            'columns': file_metadata.get('column_count', len(df.columns)),
            'upload_date': file_metadata.get('upload_date', 'Unknown')
        },
        'summary': {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'column_names': list(df.columns)
        },
        'statistics': df.describe().to_dict(),
        'analysis': analysis_results or {},
        'recommendations': recommendations or [],
        'data_sample': df.head(10).to_dict()
    }
    return report_data

# ============ DATA EXPORT ============
def prepare_csv_export(df):
    """Prepare CSV export"""
    return df.to_csv(index=False)

def prepare_json_export(data):
    """Prepare JSON export"""
    return json.dumps(data, indent=2, default=str)

# ============ INDUSTRY VALIDATION ============
def get_industry_requirements(industry):
    """Get column requirements by industry"""
    requirements = {
        'solar': {
            'preferred': ['efficiency', 'irradiance', 'power', 'temperature'],
            'optional': ['voltage', 'current', 'performance', 'generation'],
            'kpis': ['efficiency', 'capacity_factor', 'performance_ratio']
        },
        'manufacturing': {
            'preferred': ['production', 'output', 'defects', 'efficiency'],
            'optional': ['cost', 'time', 'quality'],
            'kpis': ['oee', 'defect_rate', 'throughput']
        },
        'logistics': {
            'preferred': ['delivery_time', 'distance', 'cost', 'status'],
            'optional': ['vehicle', 'driver', 'fuel'],
            'kpis': ['on_time_delivery', 'cost_efficiency']
        }
    }
    return requirements.get(industry.lower(), requirements['solar'])
