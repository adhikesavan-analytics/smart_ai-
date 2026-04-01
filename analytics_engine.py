"""
Analytics Engine - Real-working analytics with visualizations
Handles data analysis, KPI calculation, forecasting, and anomaly detection
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import json
import streamlit as st

# ============ KPI CALCULATIONS ============
def calculate_kpi(df: pd.DataFrame, column: str, kpi_type: str, **kwargs) -> Any:
    """Calculate various KPIs from data"""
    
    if column not in df.columns:
        return None
    
    try:
        data = pd.to_numeric(df[column], errors='coerce').dropna()
        
        if kpi_type == 'sum':
            return data.sum()
        elif kpi_type == 'average':
            return data.mean()
        elif kpi_type == 'count':
            return len(data)
        elif kpi_type == 'max':
            return data.max()
        elif kpi_type == 'min':
            return data.min()
        elif kpi_type == 'std':
            return data.std()
        elif kpi_type == 'median':
            return data.median()
        elif kpi_type == 'growth':
            if len(data) < 2:
                return 0
            return ((data.iloc[-1] - data.iloc[0]) / data.iloc[0] * 100) if data.iloc[0] != 0 else 0
        elif kpi_type == 'percentage_change':
            period = kwargs.get('period', 7)
            if len(data) <= period:
                return 0
            recent = data.iloc[-period:].mean()
            previous = data.iloc[:-period].mean()
            return ((recent - previous) / previous * 100) if previous != 0 else 0
    except:
        return None
    
    return None

# ============ VISUALIZATIONS ============
def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "") -> go.Figure:
    """Create interactive line chart"""
    try:
        fig = px.line(df, x=x_col, y=y_col, 
                     title=title,
                     markers=True,
                     line_shape='spline')
        fig.update_traces(
            marker=dict(size=8, color='#667eea'),
            line=dict(color='#667eea', width=3)
        )
        fig.update_layout(
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        return fig
    except Exception as e:
        return None

def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "") -> go.Figure:
    """Create interactive bar chart"""
    try:
        fig = px.bar(df, x=x_col, y=y_col,
                    title=title,
                    color=y_col,
                    color_continuous_scale='Viridis')
        fig.update_layout(
            hovermode='x',
            template='plotly_white',
            height=400
        )
        return fig
    except Exception as e:
        return None

def create_area_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "") -> go.Figure:
    """Create interactive area chart"""
    try:
        fig = px.area(df, x=x_col, y=y_col,
                     title=title)
        fig.update_traces(
            fillcolor='rgba(102, 126, 234, 0.3)',
            line=dict(color='#667eea', width=2)
        )
        fig.update_layout(
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        return fig
    except Exception as e:
        return None

def create_gauge_chart(value: float, max_val: float = 100, title: str = "") -> go.Figure:
    """Create gauge chart for KPIs"""
    try:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': title},
            delta={'reference': max_val * 0.8},
            gauge={
                'axis': {'range': [0, max_val]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, max_val * 0.5], 'color': "#ff6b6b"},
                    {'range': [max_val * 0.5, max_val * 0.8], 'color': "#ffd93d"},
                    {'range': [max_val * 0.8, max_val], 'color': "#10b981"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_val * 0.9
                }
            }
        ))
        fig.update_layout(height=300)
        return fig
    except Exception as e:
        return None

def create_heatmap(df: pd.DataFrame, title: str = "") -> go.Figure:
    """Create heatmap for correlation"""
    try:
        numeric_df = df.select_dtypes(include=[np.number])
        corr_matrix = numeric_df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0
        ))
        fig.update_layout(title=title, height=500)
        return fig
    except Exception as e:
        return None

def create_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, title: str = "") -> go.Figure:
    """Create scatter plot"""
    try:
        fig = px.scatter(df, x=x_col, y=y_col,
                        title=title,
                        trendline="ols",
                        hover_data=[x_col, y_col])
        fig.update_traces(marker=dict(size=8, color='#667eea'))
        fig.update_layout(template='plotly_white', height=400)
        return fig
    except Exception as e:
        return None

# ============ ANOMALY DETECTION ============
def detect_anomalies(df: pd.DataFrame, column: str, method: str = 'zscore', threshold: float = 2.5) -> Tuple[pd.DataFrame, int]:
    """Detect anomalies in data"""
    try:
        data = pd.to_numeric(df[column], errors='coerce').dropna()
        
        if len(data) < 10:
            return pd.DataFrame(), 0
        
        if method == 'zscore':
            mean = data.mean()
            std = data.std()
            z_scores = np.abs((data - mean) / std)
            anomaly_mask = z_scores > threshold
            
        elif method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            anomaly_mask = (data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))
            
        elif method == 'mad':
            median = data.median()
            mad = np.median(np.abs(data - median))
            modified_z_scores = 0.6745 * (data - median) / mad if mad > 0 else np.zeros(len(data))
            anomaly_mask = np.abs(modified_z_scores) > threshold
        else:
            return pd.DataFrame(), 0
        
        anomalies_df = df[anomaly_mask].copy()
        
        return anomalies_df, len(anomalies_df)
    except Exception as e:
        return pd.DataFrame(), 0

# ============ FORECASTING ============
def forecast_values(df: pd.DataFrame, column: str, periods: int = 6, method: str = 'linear') -> Tuple[pd.DataFrame, float]:
    """Forecast future values"""
    try:
        data = pd.to_numeric(df[column], errors='coerce').dropna()
        
        if len(data) < 3:
            return None, 0
        
        if method == 'linear':
            # Linear regression
            X = np.arange(len(data))
            y = data.values
            z = np.polyfit(X, y, 1)
            slope = z[0]
            intercept = z[1]
            
            # Generate forecast
            future_X = np.arange(len(data), len(data) + periods)
            predictions = slope * future_X + intercept
            
            forecast_df = pd.DataFrame({
                'Period': [f'T+{i+1}' for i in range(periods)],
                'Forecast': predictions,
                'Confidence': [95 - (i * 2) for i in range(periods)]
            })
            
            return forecast_df, slope
        
        elif method == 'exponential':
            # Simple exponential smoothing
            alpha = 0.3
            result = [data.iloc[0]]
            for i in range(1, len(data)):
                result.append(alpha * data.iloc[i] + (1 - alpha) * result[-1])
            
            predictions = []
            last = result[-1]
            for i in range(periods):
                next_val = alpha * last + (1 - alpha) * last
                predictions.append(next_val)
                last = next_val
            
            forecast_df = pd.DataFrame({
                'Period': [f'T+{i+1}' for i in range(periods)],
                'Forecast': predictions,
                'Confidence': [90 - (i * 2) for i in range(periods)]
            })
            
            slope = (predictions[-1] - predictions[0]) / periods
            return forecast_df, slope
    
    except Exception as e:
        return None, 0

# ============ INDUSTRY-SPECIFIC ANALYSIS ============
def analyze_solar_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze solar energy data"""
    analysis = {}
    
    # Efficiency
    if 'efficiency' in df.columns:
        efficiency = calculate_kpi(df, 'efficiency', 'average')
        analysis['Efficiency %'] = round(efficiency, 2) if efficiency else 0
    
    # Power generation
    if 'power' in df.columns or 'generation' in df.columns:
        power_col = 'power' if 'power' in df.columns else 'generation'
        analysis['Total Power (W)'] = calculate_kpi(df, power_col, 'sum')
        analysis['Avg Power (W)'] = calculate_kpi(df, power_col, 'average')
    
    # Temperature
    if 'temperature' in df.columns:
        temp = calculate_kpi(df, 'temperature', 'average')
        analysis['Avg Temperature (°C)'] = round(temp, 1) if temp else 0
    
    # Irradiance
    if 'irradiance' in df.columns:
        irr = calculate_kpi(df, 'irradiance', 'average')
        analysis['Avg Irradiance (W/m²)'] = round(irr, 1) if irr else 0
    
    return analysis

def analyze_manufacturing_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze manufacturing data"""
    analysis = {}
    
    # OEE
    if 'oee' in df.columns:
        oee = calculate_kpi(df, 'oee', 'average')
        analysis['OEE %'] = round(oee, 2) if oee else 0
    
    # Production
    if 'production' in df.columns or 'volume' in df.columns:
        prod_col = 'production' if 'production' in df.columns else 'volume'
        analysis['Total Production'] = calculate_kpi(df, prod_col, 'sum')
    
    # Defects
    if 'defect_rate' in df.columns or 'defects' in df.columns:
        defect_col = 'defect_rate' if 'defect_rate' in df.columns else 'defects'
        analysis['Defect Rate %'] = round(calculate_kpi(df, defect_col, 'average'), 2) if calculate_kpi(df, defect_col, 'average') else 0
    
    # Downtime
    if 'downtime' in df.columns:
        downtime = calculate_kpi(df, 'downtime', 'sum')
        analysis['Total Downtime (hrs)'] = round(downtime, 1) if downtime else 0
    
    return analysis

def analyze_logistics_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze logistics data"""
    analysis = {}
    
    # On-time delivery
    if 'on_time' in df.columns or 'on_time_delivery' in df.columns:
        ontime_col = 'on_time_delivery' if 'on_time_delivery' in df.columns else 'on_time'
        ontime = calculate_kpi(df, ontime_col, 'average')
        analysis['On-Time Delivery %'] = round(ontime, 2) if ontime else 0
    
    # Cost per delivery
    if 'cost' in df.columns or 'delivery_cost' in df.columns:
        cost_col = 'delivery_cost' if 'delivery_cost' in df.columns else 'cost'
        cost = calculate_kpi(df, cost_col, 'average')
        analysis['Avg Cost per Delivery'] = round(cost, 2) if cost else 0
    
    # Utilization
    if 'utilization' in df.columns:
        util = calculate_kpi(df, 'utilization', 'average')
        analysis['Vehicle Utilization %'] = round(util, 2) if util else 0
    
    # Deliveries
    if 'deliveries' in df.columns or 'delivery_count' in df.columns:
        deliv_col = 'delivery_count' if 'delivery_count' in df.columns else 'deliveries'
        analysis['Total Deliveries'] = calculate_kpi(df, deliv_col, 'count')
    
    return analysis

# ============ DATA QUALITY ANALYSIS ============
def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data quality"""
    quality = {}
    
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    
    quality['Total Records'] = len(df)
    quality['Total Columns'] = len(df.columns)
    quality['Completeness %'] = round((1 - missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0
    quality['Missing Values'] = missing_cells
    quality['Duplicate Rows'] = df.duplicated().sum()
    
    return quality

# ============ SUMMARY STATISTICS ============
def get_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Get summary statistics for numeric columns"""
    try:
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.describe().round(2).T
    except:
        return pd.DataFrame()

# ============ INSIGHTS GENERATION ============
def generate_quick_insights(df: pd.DataFrame, industry: str = 'solar') -> List[str]:
    """Generate quick insights from data"""
    insights = []
    
    try:
        quality = analyze_data_quality(df)
        
        # Data completeness
        if quality['Completeness %'] < 80:
            insights.append(f"⚠️ Data Completeness Low: {quality['Completeness %']}%")
        else:
            insights.append(f"✅ Data Quality Good: {quality['Completeness %']}% complete")
        
        # Duplicates
        if quality['Duplicate Rows'] > 0:
            insights.append(f"🔍 Found {quality['Duplicate Rows']} duplicate records")
        
        # Numeric analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols[:3]:  # First 3 numeric columns
            try:
                data = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(data) > 1:
                    trend = data.diff().mean()
                    if trend > 0:
                        insights.append(f"📈 {col.title()} trending upward")
                    elif trend < 0:
                        insights.append(f"📉 {col.title()} trending downward")
                    
                    # Variability
                    cv = data.std() / data.mean() if data.mean() != 0 else 0
                    if cv > 0.5:
                        insights.append(f"⚡ High variability in {col.title()}")
            except:
                pass
        
        # Anomaly summary
        for col in numeric_cols[:2]:
            anomalies_df, count = detect_anomalies(df, col)
            if count > 0:
                insights.append(f"🚨 {count} anomalies detected in {col.title()}")
        
        return insights if insights else ["✅ Data looks normal"]
    
    except Exception as e:
        return [f"⚠️ Unable to generate insights: {str(e)}"]
