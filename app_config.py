"""
Smart Solar AI - Enterprise Configuration
Complete feature set and industry definitions
"""

# ============ APP IDENTITY ============
APP_NAME = "🚀 Smart BI Analytics"
APP_SUBTITLE = "AI-Driven Business Intelligence Platform"
APP_VERSION = "3.0 Enterprise Edition"
APP_TAGLINE = "Industry-Agnostic AI BI • Predictive Analytics • Real-Time Insights"

# ============ INDUSTRIES ============
INDUSTRIES = {
    'solar': {
        'name': '☀️ Solar Energy',
        'icon': '☀️',
        'default_kpis': ['efficiency', 'power_generation', 'irradiance', 'temperature', 'performance_ratio'],
        'visualization_types': ['time_series', 'gauge', 'heatmap', 'scatter'],
        'anomaly_threshold': 2.5,
        'forecast_periods': 6,
        'description': 'Solar panel performance monitoring and optimization'
    },
    'manufacturing': {
        'name': '🏭 Manufacturing',
        'icon': '🏭',
        'default_kpis': ['oee', 'defect_rate', 'production_volume', 'machine_efficiency', 'downtime_hours'],
        'visualization_types': ['bar_chart', 'line_chart', 'heatmap', 'gauge'],
        'anomaly_threshold': 2.0,
        'forecast_periods': 8,
        'description': 'Production optimization and quality control'
    },
    'logistics': {
        'name': '🚚 Logistics',
        'icon': '🚚',
        'default_kpis': ['on_time_delivery', 'cost_per_unit', 'vehicle_utilization', 'average_delivery_time', 'fuel_efficiency'],
        'visualization_types': ['map', 'line_chart', 'bar_chart', 'gauge'],
        'anomaly_threshold': 2.5,
        'forecast_periods': 10,
        'description': 'Fleet management and delivery optimization'
    },
    'retail': {
        'name': '🛍️ Retail',
        'icon': '🛍️',
        'default_kpis': ['sales_revenue', 'conversion_rate', 'avg_transaction_value', 'inventory_turnover', 'customer_retention'],
        'visualization_types': ['bar_chart', 'pie_chart', 'line_chart', 'gauge'],
        'anomaly_threshold': 2.0,
        'forecast_periods': 6,
        'description': 'Sales and inventory optimization'
    },
    'healthcare': {
        'name': '⚕️ Healthcare',
        'icon': '⚕️',
        'default_kpis': ['patient_wait_time', 'bed_occupancy', 'staff_efficiency', 'patient_satisfaction', 'readmission_rate'],
        'visualization_types': ['gauge', 'line_chart', 'bar_chart', 'heatmap'],
        'anomaly_threshold': 2.0,
        'forecast_periods': 8,
        'description': 'Patient care and operational efficiency'
    },
    'finance': {
        'name': '💰 Finance',
        'icon': '💰',
        'default_kpis': ['revenue', 'expenses', 'profit_margin', 'cash_flow', 'debt_ratio'],
        'visualization_types': ['line_chart', 'bar_chart', 'waterfall', 'gauge'],
        'anomaly_threshold': 2.5,
        'forecast_periods': 6,
        'description': 'Financial analysis and forecasting'
    }
}

# ============ USER ROLES ============
ROLES = {
    'admin': {
        'name': 'Administrator',
        'permissions': [
            'view_dashboard',
            'upload_data',
            'create_users',
            'delete_users',
            'manage_kpis',
            'view_logs',
            'export_reports',
            'configure_settings',
            'manage_roles',
            'system_settings'
        ],
        'color': '🔴'
    },
    'user': {
        'name': 'User',
        'permissions': [
            'view_dashboard',
            'upload_data',
            'create_kpis',
            'export_reports',
            'view_analytics'
        ],
        'color': '🟢'
    },
    'analyst': {
        'name': 'Data Analyst',
        'permissions': [
            'view_dashboard',
            'upload_data',
            'create_kpis',
            'export_reports',
            'view_analytics',
            'view_logs'
        ],
        'color': '🟡'
    }
}

# ============ KPI TYPES ============
KPI_TYPES = {
    'sum': {'name': 'Sum', 'description': 'Total of values'},
    'average': {'name': 'Average', 'description': 'Mean value'},
    'count': {'name': 'Count', 'description': 'Number of records'},
    'max': {'name': 'Maximum', 'description': 'Highest value'},
    'min': {'name': 'Minimum', 'description': 'Lowest value'},
    'std': {'name': 'Std Dev', 'description': 'Standard deviation'},
    'growth': {'name': 'Growth %', 'description': 'Period-over-period change'}
}

# ============ ANOMALY DETECTION ============
ANOMALY_METHODS = {
    'zscore': {'name': 'Z-Score', 'description': 'Statistical outlier detection'},
    'iqr': {'name': 'IQR', 'description': 'Interquartile range method'},
    'mad': {'name': 'MAD', 'description': 'Median Absolute Deviation'},
    'isolation': {'name': 'Isolation Forest', 'description': 'Ensemble method'}
}

# ============ VISUALIZATION COLORS ============
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#3b82f6',
    'dark': '#1f2937',
    'light': '#f3f4f6'
}

# ============ CHART TYPES ============
CHART_TYPES = {
    'line': 'Line Chart',
    'bar': 'Bar Chart',
    'area': 'Area Chart',
    'scatter': 'Scatter Plot',
    'pie': 'Pie Chart',
    'gauge': 'Gauge Chart',
    'heatmap': 'Heatmap',
    'box': 'Box Plot',
    'histogram': 'Histogram',
    'waterfall': 'Waterfall'
}

# ============ FEATURES ============
FEATURES = {
    'real_time_dashboard': {
        'name': 'Real-Time Dashboard',
        'icon': '⚡',
        'description': 'Live data updates and monitoring',
        'enabled': True
    },
    'predictive_analytics': {
        'name': 'Predictive Analytics',
        'icon': '🔮',
        'description': 'Forecast future trends and patterns',
        'enabled': True
    },
    'anomaly_detection': {
        'name': 'Anomaly Detection',
        'icon': '🔍',
        'description': 'Identify unusual patterns automatically',
        'enabled': True
    },
    'custom_kpi_builder': {
        'name': 'Custom KPI Builder',
        'icon': '⚙️',
        'description': 'Create industry-specific metrics',
        'enabled': True
    },
    'ai_recommendations': {
        'name': 'AI Recommendations',
        'icon': '💡',
        'description': 'AI-driven decision support',
        'enabled': True
    },
    'downloadable_reports': {
        'name': 'Downloadable Reports',
        'icon': '📄',
        'description': 'PDF and Excel exports',
        'enabled': True
    },
    'multi_industry': {
        'name': 'Multi-Industry Support',
        'icon': '🌍',
        'description': 'Adapt to any industry automatically',
        'enabled': True
    },
    'activity_tracking': {
        'name': 'Activity Tracking',
        'icon': '📋',
        'description': 'Complete audit trail',
        'enabled': True
    }
}

# ============ DATABASE ============
DATABASE_NAME = 'smart_bi_enterprise.db'
DATABASE_TIMEOUT = 30

# ============ FILE UPLOAD ============
MAX_FILE_SIZE_MB = 100
MAX_TOTAL_STORAGE_GB = 10
ALLOWED_EXTENSIONS = ['csv', 'xlsx', 'xls', 'json']

# ============ AI CONFIGURATION ============
AI_PROVIDERS = {
    'claude': {
        'name': 'Claude 3 (Anthropic)',
        'model': 'claude-opus-4-1-20250805',
        'max_tokens': 4000
    },
    'chatgpt': {
        'name': 'GPT-4 (OpenAI)',
        'model': 'gpt-4',
        'max_tokens': 8000
    }
}

# ============ INSIGHTS PROMPTS ============
INDUSTRY_PROMPTS = {
    'solar': """Analyze this solar energy data and provide:
1. Efficiency assessment
2. Performance trends
3. Maintenance recommendations
4. Optimization suggestions
Format as bullet points with actionable insights.""",
    
    'manufacturing': """Analyze this manufacturing data and provide:
1. OEE (Overall Equipment Effectiveness) assessment
2. Quality issues identified
3. Efficiency improvements
4. Cost reduction opportunities
Format as bullet points with actionable insights.""",
    
    'logistics': """Analyze this logistics data and provide:
1. Delivery performance assessment
2. Route optimization opportunities
3. Cost saving possibilities
4. Fleet utilization insights
Format as bullet points with actionable insights.""",
    
    'retail': """Analyze this retail data and provide:
1. Sales performance assessment
2. Conversion optimization
3. Inventory management suggestions
4. Customer engagement recommendations
Format as bullet points with actionable insights."""
}

# ============ THEME ============
THEME_MODE = 'light'  # or 'dark'
SIDEBAR_WIDTH = 280
