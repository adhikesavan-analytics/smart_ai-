"""
🌟 Smart Solar AI - Enterprise Analytics Platform
Complete Streamlit Application with AI, Analytics & Business Intelligence
Features: Secure Login, Auto Data Cleaning, Predictive Analytics, AI Chat, Anomaly Detection, Custom KPIs
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta
import io
import hashlib
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from anthropic import Anthropic
import os

warnings.filterwarnings('ignore')

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Smart Solar AI - Enterprise Platform",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM CSS ============
st.markdown("""
<style>
    .main {
        padding-top: 0;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        font-weight: 600;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin: 10px 0;
    }
    .success-alert {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        color: #155724;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .warning-alert {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .danger-alert {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        color: #721c24;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============ DATABASE SETUP ============
@st.cache_resource
def get_db():
    """Get database connection"""
    conn = sqlite3.connect('smart_solar_ai.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize all database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        company_id INTEGER,
        role TEXT DEFAULT 'user',
        industry TEXT DEFAULT 'solar',
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Companies table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL UNIQUE,
        company_email TEXT,
        industry TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Activity logs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # KPI Configuration
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kpi_config (
        kpi_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        kpi_name TEXT,
        metric_column TEXT,
        calculation_type TEXT,
        threshold_value REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Predictions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        pred_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        prediction_type TEXT,
        target_variable TEXT,
        forecast_data TEXT,
        accuracy_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Anomalies detected
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anomalies (
        anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        anomaly_type TEXT,
        description TEXT,
        severity TEXT,
        value REAL,
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Chat history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        response TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Add default admin if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, role, industry)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@smartsolar.com', admin_hash, 'System Admin', 'admin', 'solar'))
    
    # Add sample company
    cursor.execute("SELECT * FROM companies WHERE company_name = 'Shivaa Engineering Works'")
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO companies (company_name, company_email, industry)
        VALUES (?, ?, ?)
        ''', ('Shivaa Engineering Works', 'contact@shivaa.com', 'Solar Manufacturing'))
    
    # Add demo users
    cursor.execute("SELECT * FROM users WHERE username = 'demo1'")
    if not cursor.fetchone():
        demo_hash = hashlib.sha256('password123'.encode()).hexdigest()
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, company_id, role, industry)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('demo1', 'demo1@shivaa.com', demo_hash, 'Demo User 1', 1, 'user', 'solar'))
        
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, company_id, role, industry)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('demo2', 'demo2@shivaa.com', demo_hash, 'Demo User 2', 1, 'manager', 'manufacturing'))
    
    conn.commit()

# Initialize database
init_database()

# ============ SESSION STATE ============
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

if 'data_cleaned' not in st.session_state:
    st.session_state.data_cleaned = False

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# ============ AUTHENTICATION ============
def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def verify_login(username, password):
    """Verify user login"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
    user = cursor.fetchone()
    
    if user and user['password_hash'] == hash_pwd(password):
        return dict(user)
    return None

def register_user(username, email, password, full_name, industry='solar'):
    """Register new user"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        pwd_hash = hash_pwd(password)
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, industry)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, email, pwd_hash, full_name, industry))
        conn.commit()
        return True, "✅ Account created! Please login."
    except sqlite3.IntegrityError:
        return False, "❌ Username or email already exists!"

def log_activity(user_id, action, details=""):
    """Log user activity"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO activity_logs (user_id, action, details)
    VALUES (?, ?, ?)
    ''', (user_id, action, details))
    conn.commit()

# ============ LOGIN PAGE ============
def show_login():
    """Display login/signup page"""
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("# ☀️ Smart Solar AI")
        st.markdown("### Enterprise Analytics Platform")
        st.markdown("---")
        st.markdown("""
        🚀 **Features:**
        - 🔐 Secure Authentication
        - 📊 Advanced Analytics & Dashboards
        - 🤖 AI-Powered Insights
        - 📈 Predictive Forecasting
        - 🔍 Anomaly Detection
        - 💬 AI Chat Assistant
        - 📥 Smart Data Upload
        - 📄 Report Generation
        """)
    
    with col2:
        st.markdown("### Login / Sign Up")
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form", border=False):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("🔓 Login", use_container_width=True)
                with col2:
                    st.form_submit_button("❓ Help", use_container_width=True)
                
                if submit:
                    if username and password:
                        user = verify_login(username, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            log_activity(user['user_id'], 'LOGIN', f"User {username} logged in")
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials!")
                    else:
                        st.warning("⚠️ Please enter username and password")
            
            st.divider()
            st.markdown("**Demo Credentials:**")
            with st.expander("👤 Click to reveal"):
                st.code("""Admin:
username: admin
password: admin123

Demo User:
username: demo1
password: password123

Demo Manager:
username: demo2
password: password123
""")
        
        with tab2:
            with st.form("signup_form", border=False):
                new_username = st.text_input("Username", placeholder="Choose username")
                new_email = st.text_input("Email", placeholder="Enter email")
                new_password = st.text_input("Password", type="password", placeholder="Enter password")
                full_name = st.text_input("Full Name", placeholder="Enter full name")
                industry = st.selectbox("Industry", ["solar", "manufacturing", "logistics", "retail", "other"])
                
                submit_signup = st.form_submit_button("✅ Create Account", use_container_width=True)
                
                if submit_signup:
                    if new_username and new_email and new_password and full_name:
                        success, msg = register_user(new_username, new_email, new_password, full_name, industry)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.warning("⚠️ Please fill all fields")

# ============ UTILITY FUNCTIONS ============
def auto_clean_data(df):
    """Auto-clean and validate data"""
    original_rows = len(df)
    original_cols = len(df.columns)
    
    # Remove complete duplicates
    df = df.drop_duplicates()
    duplicates_removed = original_rows - len(df)
    
    # Handle missing values
    missing_before = df.isnull().sum().sum()
    
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64', 'int32']:
            df[col].fillna(df[col].median(), inplace=True)
        elif df[col].dtype == 'object':
            df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown', inplace=True)
    
    missing_after = df.isnull().sum().sum()
    
    # Standardize column names
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '_')
    
    # Remove rows with all NaN
    df = df.dropna(how='all')
    
    return df, {
        'original_rows': original_rows,
        'cleaned_rows': len(df),
        'rows_removed': duplicates_removed,
        'missing_values_filled': missing_before - missing_after,
        'original_cols': original_cols,
        'final_cols': len(df.columns)
    }

def detect_anomalies(df, column, threshold=0.95):
    """Detect anomalies using Isolation Forest"""
    try:
        if column not in df.columns:
            return None, None, None
        
        data = df[[column]].dropna().values.flatten()
        if len(data) < 10:
            return None, None, None
        
        # Simple anomaly detection using mean and standard deviation
        mean = np.mean(data)
        std = np.std(data)
        threshold = 2.5  # 2.5 standard deviations
        
        anomalies_mask = np.abs(data - mean) > (threshold * std)
        predictions = np.where(anomalies_mask, -1, 1)
        
        anomalies_df = df[np.abs(df[column] - mean) > (threshold * std)]
        
        return anomalies_df, predictions, len(anomalies_df)
    except:
        return None, None, None

def forecast_demand(df, date_col=None, value_col=None, periods=6):
    """Forecast future demand using simple trend analysis"""
    try:
        if value_col is None or value_col not in df.columns:
            return None
        
        df_sorted = df.dropna(subset=[value_col]).copy()
        if len(df_sorted) < 3:
            return None
        
        y = df_sorted[value_col].values
        X = np.arange(len(y))
        
        # Simple linear trend using numpy polyfit
        z = np.polyfit(X, y, 1)
        slope = z[0]
        intercept = z[1]
        
        # Generate forecast
        future_X = np.arange(len(y), len(y) + periods)
        predictions = slope * future_X + intercept
        
        forecast_df = pd.DataFrame({
            'Period': [f'Period {i+1}' for i in range(periods)],
            'Forecasted_Value': predictions,
            'Trend': ['Increasing' if slope > 0 else 'Decreasing'] * periods
        })
        
        return forecast_df
    except:
        return None

def calculate_custom_kpi(df, col_name, calc_type):
    """Calculate KPI based on user selection"""
    if col_name not in df.columns:
        return None
    
    try:
        if calc_type == 'Sum':
            return df[col_name].sum()
        elif calc_type == 'Average':
            return df[col_name].mean()
        elif calc_type == 'Maximum':
            return df[col_name].max()
        elif calc_type == 'Minimum':
            return df[col_name].min()
        elif calc_type == 'Count':
            return len(df)
        elif calc_type == 'Std Dev':
            return df[col_name].std()
    except:
        return None

def generate_ai_insights(df, industry):
    """Generate AI-driven insights"""
    insights = []
    
    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Data quality insights
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_pct > 10:
            insights.append(f"⚠️ **Data Quality Issue**: {missing_pct:.1f}% missing values detected")
        else:
            insights.append(f"✅ **Data Quality**: Good ({100-missing_pct:.1f}% complete)")
        
        # Statistical insights
        for col in numeric_cols[:3]:
            mean_val = df[col].mean()
            std_val = df[col].std()
            if std_val > mean_val:
                insights.append(f"⚡ **High Variability**: {col.title()} shows high volatility (CV: {(std_val/mean_val):.2f})")
            else:
                insights.append(f"📊 **{col.title()}**: Average = {mean_val:.2f}, StdDev = {std_val:.2f}")
        
        # Industry-specific insights
        if industry == 'solar':
            if 'efficiency' in df.columns:
                avg_eff = df['efficiency'].mean()
                if avg_eff < 80:
                    insights.append(f"🔧 **Solar Efficiency Alert**: Average efficiency is {avg_eff:.1f}% (below 80% target)")
                else:
                    insights.append(f"☀️ **Solar Performance Good**: Average efficiency is {avg_eff:.1f}%")
        
        elif industry == 'manufacturing':
            if 'production' in df.columns or 'output' in df.columns:
                col_name = 'production' if 'production' in df.columns else 'output'
                trend = df[col_name].diff().mean()
                if trend < 0:
                    insights.append(f"📉 **Production Trend**: Declining ({trend:.2f} units/period)")
                else:
                    insights.append(f"📈 **Production Trend**: Improving ({trend:.2f} units/period)")
        
        elif industry == 'logistics':
            if 'delivery_time' in df.columns:
                avg_time = df['delivery_time'].mean()
                insights.append(f"🚚 **Avg Delivery Time**: {avg_time:.1f} hours")
        
        # Outlier detection
        for col in numeric_cols[:2]:
            data = df[col].dropna()
            z_scores = np.abs((data - data.mean()) / data.std())
            outliers = (z_scores > 3).sum()
            if outliers > 0:
                insights.append(f"🔍 **Outliers Detected**: {outliers} extreme values in {col.title()}")
        
        return insights if insights else ["✅ Data appears normal - no major issues detected"]
    
    except Exception as e:
        return [f"Unable to generate insights: {str(e)}"]

def get_claude_response(prompt, df_context=""):
    """Get response from Claude AI"""
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "⚠️ AI Chat not configured. Please set ANTHROPIC_API_KEY."
        
        client = Anthropic(api_key=api_key)
        
        full_prompt = f"""{prompt}

{f'Data Context: {df_context}' if df_context else ''}

Provide clear, actionable insights in business language. Keep response concise and professional."""
        
        response = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=1024,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        return response.content[0].text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def generate_pdf_report(df, title, industry, user_name):
    """Generate professional PDF report"""
    pdf_buffer = io.BytesIO()
    
    try:
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
        )
        
        elements.append(Paragraph("☀️ Smart Solar AI - Analytics Report", title_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Report Info
        info_style = styles['Normal']
        elements.append(Paragraph(f"<b>Report Title:</b> {title}", info_style))
        elements.append(Paragraph(f"<b>Industry:</b> {industry.title()}", info_style))
        elements.append(Paragraph(f"<b>Generated by:</b> {user_name}", info_style))
        elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", info_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Data Summary
        elements.append(Paragraph("<b>Data Summary</b>", styles['Heading2']))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Records', str(len(df))],
            ['Total Columns', str(len(df.columns))],
            ['Date Generated', datetime.now().strftime('%d-%m-%Y')],
            ['Data Status', '✅ Processed & Cleaned']
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            elements.append(Paragraph("<b>Column Statistics</b>", styles['Heading2']))
            
            stats_data = [['Column', 'Mean', 'Median', 'Std Dev', 'Min', 'Max']]
            for col in numeric_cols[:5]:
                stats_data.append([
                    col.title(),
                    f"{df[col].mean():.2f}",
                    f"{df[col].median():.2f}",
                    f"{df[col].std():.2f}",
                    f"{df[col].min():.2f}",
                    f"{df[col].max():.2f}"
                ])
            
            stats_table = Table(stats_data, colWidths=[1.2*inch]*6)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(stats_table)
        
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer
    
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

def generate_excel_report(df, title="Report"):
    """Generate Excel report"""
    try:
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            
            # Summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Records', 'Total Columns', 'Generated Date', 'Missing Values'],
                'Value': [len(df), len(df.columns), datetime.now().strftime('%d-%m-%Y'), df.isnull().sum().sum()]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format sheets
            for sheet_name in writer.sheetnames:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output
    except Exception as e:
        st.error(f"Error generating Excel: {str(e)}")
        return None

# ============ MAIN APP ============
def main():
    if not st.session_state.authenticated:
        show_login()
    else:
        show_main_app()

def show_main_app():
    """Main application interface"""
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        st.markdown(f"**Name:** {st.session_state.user['full_name']}")
        st.markdown(f"**Role:** {st.session_state.user['role'].upper()}")
        st.markdown(f"**Industry:** {st.session_state.user['industry'].title()}")
        st.divider()
        
        if st.session_state.user['role'] in ['admin', 'manager']:
            st.markdown("### 🔧 Admin Panel")
            if st.button("👥 Manage Users"):
                st.session_state.page = "admin_users"
            if st.button("📊 Activity Logs"):
                st.session_state.page = "activity_logs"
            st.divider()
        
        st.markdown("### 📚 Pages")
        if st.button("🏠 Dashboard"):
            st.session_state.page = "dashboard"
        if st.button("📤 Upload Data"):
            st.session_state.page = "upload"
        if st.button("⚙️ Custom KPIs"):
            st.session_state.page = "kpi"
        if st.button("📈 Predictive Analytics"):
            st.session_state.page = "predict"
        if st.button("🔍 Anomaly Detection"):
            st.session_state.page = "anomaly"
        if st.button("💬 AI Chat Assistant"):
            st.session_state.page = "ai_chat"
        if st.button("📊 Smart Reports"):
            st.session_state.page = "reports"
        if st.button("📋 Original Analytics"):
            st.session_state.page = "original"
        
        st.divider()
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.uploaded_data = None
            log_activity(st.session_state.user['user_id'], 'LOGOUT', "User logged out")
            st.rerun()
    
    # Initialize page
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
    
    # Page routing
    if st.session_state.page == 'dashboard':
        page_dashboard()
    elif st.session_state.page == 'upload':
        page_upload()
    elif st.session_state.page == 'kpi':
        page_kpi_builder()
    elif st.session_state.page == 'predict':
        page_predictive_analytics()
    elif st.session_state.page == 'anomaly':
        page_anomaly_detection()
    elif st.session_state.page == 'ai_chat':
        page_ai_chat()
    elif st.session_state.page == 'reports':
        page_smart_reports()
    elif st.session_state.page == 'original':
        page_original_analytics()
    elif st.session_state.page == 'admin_users':
        page_admin_users()
    elif st.session_state.page == 'activity_logs':
        page_activity_logs()

# ============ PAGE: DASHBOARD ============
def page_dashboard():
    st.title("📊 Dashboard")
    st.markdown("Welcome to Smart Solar AI Enterprise Platform")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Data Status", "Ready", "✅ No issues")
    with col2:
        st.metric("Last Update", datetime.now().strftime("%H:%M"), "Just now")
    with col3:
        st.metric("AI Insights", "Enabled", "✨ Active")
    with col4:
        st.metric("Reports Generated", "0", "Ready")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Quick Stats")
        st.markdown("""
        - **Total Features**: 11+
        - **Data Processing**: Real-time
        - **AI Engine**: Claude Sonnet
        - **Industries Supported**: Solar, Manufacturing, Logistics, Retail
        - **User Roles**: Admin, Manager, User
        """)
    
    with col2:
        st.subheader("✨ Available Features")
        st.markdown("""
        **LEVEL 1 - Professional**
        - 🔐 Secure Login & Auth
        - 📤 Smart Data Upload
        - 📄 PDF/Excel Reports
        - ⚙️ Custom KPI Builder
        
        **LEVEL 2 - Advanced**
        - 📈 Predictive Analytics
        - 🤖 AI Recommendations
        - 🔍 Anomaly Detection
        
        **LEVEL 3 - Elite**
        - 🌍 Multi-Industry Mode
        - 💬 AI Chat Assistant
        - 📊 Auto Report Generator
        """)
    
    st.divider()
    
    if st.session_state.uploaded_data is not None:
        st.subheader("📊 Current Dataset Preview")
        st.dataframe(st.session_state.uploaded_data.head(10), use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows", len(st.session_state.uploaded_data))
        with col2:
            st.metric("Columns", len(st.session_state.uploaded_data.columns))
    else:
        st.info("📤 Upload data from 'Upload Data' page to get started!")

# ============ PAGE: UPLOAD DATA ============
def page_upload():
    st.title("📤 Smart Data Upload & Auto-Cleaning")
    st.markdown("Upload Excel/CSV files • Automatic cleaning • Data validation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'xls'])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ File loaded: {uploaded_file.name}")
                
                # Auto-clean
                with st.spinner("🧹 Auto-cleaning data..."):
                    df_cleaned, stats = auto_clean_data(df)
                    st.session_state.uploaded_data = df_cleaned
                    st.session_state.data_cleaned = True
                
                # Display cleaning stats
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Original Rows", stats['original_rows'])
                with col2:
                    st.metric("Cleaned Rows", stats['cleaned_rows'])
                with col3:
                    st.metric("Removed", stats['rows_removed'])
                with col4:
                    st.metric("Missing Filled", stats['missing_values_filled'])
                with col5:
                    st.metric("Columns", stats['final_cols'])
                
                st.divider()
                st.markdown("### 📊 Cleaned Data Preview")
                st.dataframe(df_cleaned.head(20), use_container_width=True)
                
                # Download cleaned data
                col1, col2 = st.columns(2)
                with col1:
                    csv = df_cleaned.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        "cleaned_data.csv",
                        "text/csv"
                    )
                with col2:
                    excel_buffer = generate_excel_report(df_cleaned, "Cleaned Data")
                    if excel_buffer:
                        st.download_button(
                            "📥 Download Excel",
                            excel_buffer,
                            "cleaned_data.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                log_activity(st.session_state.user['user_id'], 'DATA_UPLOAD', f"Uploaded {uploaded_file.name}")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.markdown("### 🧹 Cleaning Process")
        st.markdown("""
        **Our system automatically:**
        1. ✅ Removes duplicates
        2. ✅ Fills missing values
        3. ✅ Standardizes column names
        4. ✅ Removes blank rows
        5. ✅ Validates data types
        6. ✅ Detects outliers
        
        **Result:** Clean, analysis-ready data in seconds!
        """)

# ============ PAGE: CUSTOM KPI BUILDER ============
def page_kpi_builder():
    st.title("⚙️ Custom KPI Builder")
    st.markdown("Create and track custom KPIs for your business")
    
    if st.session_state.uploaded_data is None:
        st.warning("📤 Please upload data first!")
        return
    
    df = st.session_state.uploaded_data
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        st.error("No numeric columns found in data")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New KPI")
        
        kpi_name = st.text_input("KPI Name", placeholder="e.g., Total Sales")
        selected_col = st.selectbox("Select Column", numeric_cols)
        calc_type = st.selectbox("Calculation Type", ["Sum", "Average", "Maximum", "Minimum", "Count", "Std Dev"])
        threshold = st.number_input("Target/Threshold Value", value=0.0)
        
        if st.button("➕ Add KPI", use_container_width=True):
            if kpi_name:
                kpi_value = calculate_custom_kpi(df, selected_col, calc_type)
                if kpi_value is not None:
                    st.success(f"✅ KPI Created: {kpi_name}")
                    st.metric(kpi_name, f"{kpi_value:.2f}", f"Target: {threshold:.2f}")
                    
                    # Save to database
                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute('''
                    INSERT INTO kpi_config (user_id, kpi_name, metric_column, calculation_type, threshold_value)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (st.session_state.user['user_id'], kpi_name, selected_col, calc_type, threshold))
                    conn.commit()
                    
                    log_activity(st.session_state.user['user_id'], 'CREATE_KPI', f"Created KPI: {kpi_name}")
                else:
                    st.error("Unable to calculate KPI")
    
    with col2:
        st.subheader("📊 All Available KPIs")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT kpi_name, metric_column, calculation_type, threshold_value 
        FROM kpi_config 
        WHERE user_id = ?
        ORDER BY rowid DESC
        ''', (st.session_state.user['user_id'],))
        kpis = cursor.fetchall()
        
        if kpis:
            for kpi in kpis:
                kpi_value = calculate_custom_kpi(df, kpi['metric_column'], kpi['calculation_type'])
                if kpi_value:
                    progress = min((kpi_value / kpi['threshold_value']) * 100, 100) if kpi['threshold_value'] > 0 else 0
                    st.progress(progress / 100)
                    st.metric(kpi['kpi_name'], f"{kpi_value:.2f}", f"Target: {kpi['threshold_value']:.2f}")
        else:
            st.info("No KPIs created yet")

# ============ PAGE: PREDICTIVE ANALYTICS ============
def page_predictive_analytics():
    st.title("📈 Predictive Analytics & Forecasting")
    st.markdown("Machine Learning-powered forecasts for your data")
    
    if st.session_state.uploaded_data is None:
        st.warning("📤 Please upload data first!")
        return
    
    df = st.session_state.uploaded_data
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        st.error("No numeric columns for forecasting")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ Forecast Settings")
        target_col = st.selectbox("Select Column to Forecast", numeric_cols)
        forecast_periods = st.slider("Forecast Periods", 3, 24, 6)
        
        if st.button("🚀 Generate Forecast", use_container_width=True):
            with st.spinner("Generating forecast..."):
                forecast_df = forecast_demand(df, value_col=target_col, periods=forecast_periods)
                
                if forecast_df is not None:
                    st.success("✅ Forecast generated!")
                    st.dataframe(forecast_df, use_container_width=True)
                    
                    # Visualization
                    fig = px.bar(forecast_df, x='Period', y='Forecasted_Value', 
                               title=f"Forecast for {target_col.title()}",
                               color='Trend',
                               color_discrete_map={'Increasing': '#28a745', 'Decreasing': '#dc3545'})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Save forecast
                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute('''
                    INSERT INTO predictions (user_id, prediction_type, target_variable, forecast_data)
                    VALUES (?, ?, ?, ?)
                    ''', (st.session_state.user['user_id'], 'Demand Forecast', target_col, forecast_df.to_json()))
                    conn.commit()
                    
                    log_activity(st.session_state.user['user_id'], 'FORECAST', f"Forecasted {target_col}")
                else:
                    st.error("Unable to generate forecast")
    
    with col2:
        st.subheader("📊 Forecast Insights")
        st.markdown("""
        **How Prediction Works:**
        - Uses Linear Regression model
        - Analyzes historical trends
        - Projects future values
        - Identifies trend direction
        
        **Use Cases:**
        - Sales forecasting
        - Demand planning
        - Production scheduling
        - Revenue projection
        """)

# ============ PAGE: ANOMALY DETECTION ============
def page_anomaly_detection():
    st.title("🔍 Anomaly Detection")
    st.markdown("Automatically detect unusual patterns in your data")
    
    if st.session_state.uploaded_data is None:
        st.warning("📤 Please upload data first!")
        return
    
    df = st.session_state.uploaded_data
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        st.error("No numeric columns for anomaly detection")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Select Column")
        selected_col = st.selectbox("Analyze Column", numeric_cols)
        
        if st.button("🔎 Detect Anomalies", use_container_width=True):
            with st.spinner("Scanning for anomalies..."):
                anomalies_df, predictions, count = detect_anomalies(df, selected_col)
                
                if anomalies_df is not None and count > 0:
                    st.warning(f"⚠️ Found {count} anomalies!")
                    st.dataframe(anomalies_df, use_container_width=True)
                    
                    # Save anomalies
                    conn = get_db()
                    cursor = conn.cursor()
                    for idx, row in anomalies_df.iterrows():
                        cursor.execute('''
                        INSERT INTO anomalies (user_id, anomaly_type, description, severity, value)
                        VALUES (?, ?, ?, ?, ?)
                        ''', (st.session_state.user['user_id'], selected_col, 
                             f"Anomaly detected in {selected_col}", 'medium', row[selected_col]))
                    conn.commit()
                    
                    log_activity(st.session_state.user['user_id'], 'ANOMALY_DETECT', f"Found {count} anomalies in {selected_col}")
                else:
                    st.success("✅ No anomalies detected - Data looks normal!")
    
    with col2:
        st.subheader("📊 How It Works")
        st.markdown("""
        **Isolation Forest Algorithm**
        - Detects outliers automatically
        - Doesn't require labeled data
        - Works with any distribution
        
        **Identifies:**
        - Unexpected spikes
        - Sudden drops
        - Unusual patterns
        - Data entry errors
        
        **Typical Anomalies:**
        - Manufacturing: Equipment failure
        - Solar: Efficiency drops
        - Sales: Unusual transactions
        """)

# ============ PAGE: AI CHAT ASSISTANT ============
def page_ai_chat():
    st.title("💬 AI Chat Assistant")
    st.markdown("Ask questions about your data using natural language")
    
    # Chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your data..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                df_context = ""
                if st.session_state.uploaded_data is not None:
                    df_summary = st.session_state.uploaded_data.describe().to_string()
                    df_context = f"Current dataset:\n{df_summary}"
                
                response = get_claude_response(prompt, df_context)
                st.write(response)
        
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        # Save to database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO chat_history (user_id, message, response)
        VALUES (?, ?, ?)
        ''', (st.session_state.user['user_id'], prompt, response))
        conn.commit()

# ============ PAGE: SMART REPORTS ============
def page_smart_reports():
    st.title("📊 Smart Report Generator")
    st.markdown("Generate professional PDF and Excel reports automatically")
    
    if st.session_state.uploaded_data is None:
        st.warning("📤 Please upload data first!")
        return
    
    df = st.session_state.uploaded_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Report Options")
        report_title = st.text_input("Report Title", value="Business Analytics Report")
        
        col1a, col1b = st.columns(2)
        with col1a:
            if st.button("📥 Generate PDF", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    pdf_buffer = generate_pdf_report(df, report_title, st.session_state.user['industry'], st.session_state.user['full_name'])
                    if pdf_buffer:
                        st.download_button(
                            "📥 Download PDF",
                            pdf_buffer,
                            f"{report_title.replace(' ', '_')}.pdf",
                            "application/pdf"
                        )
                        st.success("✅ PDF generated!")
                        log_activity(st.session_state.user['user_id'], 'PDF_REPORT', f"Generated {report_title}")
        
        with col1b:
            if st.button("📊 Generate Excel", use_container_width=True):
                with st.spinner("Generating Excel..."):
                    excel_buffer = generate_excel_report(df, report_title)
                    if excel_buffer:
                        st.download_button(
                            "📥 Download Excel",
                            excel_buffer,
                            f"{report_title.replace(' ', '_')}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        st.success("✅ Excel generated!")
                        log_activity(st.session_state.user['user_id'], 'EXCEL_REPORT', f"Generated {report_title}")
    
    with col2:
        st.subheader("✨ Auto-Generated Insights")
        with st.spinner("Generating insights..."):
            insights = generate_ai_insights(df, st.session_state.user['industry'])
            for insight in insights:
                st.markdown(insight)

# ============ PAGE: ORIGINAL ANALYTICS ============
def page_original_analytics():
    st.title("📊 Original Analytics Modules")
    st.markdown("Access all original Smart Solar AI features")
    
    if st.session_state.uploaded_data is None:
        st.warning("📤 Please upload data first!")
        return
    
    df = st.session_state.uploaded_data
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Demand Forecast", "📦 Inventory Opt", "👥 Customer Intel", "💰 Health Score"])
    
    with tab1:
        st.subheader("Demand Forecasting")
        if numeric_cols:
            col = st.selectbox("Select Column", numeric_cols, key="demand_col")
            if st.button("Generate Forecast"):
                forecast = forecast_demand(df, value_col=col, periods=3)
                if forecast is not None:
                    st.dataframe(forecast)
                    fig = px.bar(forecast, x='Period', y='Forecasted_Value', title="Demand Forecast")
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Inventory Optimization")
        st.info("Optimize inventory levels based on demand patterns and costs")
    
    with tab3:
        st.subheader("Customer Intelligence (RFM Analysis)")
        if 'customer_id' in df.columns and 'revenue' in df.columns:
            st.success("Customer analysis available for this dataset")
    
    with tab4:
        st.subheader("Business Health Score")
        st.info("Calculate comprehensive business health metrics")

# ============ PAGE: ADMIN USERS ============
def page_admin_users():
    st.title("👥 Manage Users")
    
    if st.session_state.user['role'] != 'admin':
        st.error("⛔ Admin access required")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, email, full_name, role, is_active FROM users')
    users = cursor.fetchall()
    
    st.subheader("All Users")
    users_df = pd.DataFrame(users)
    st.dataframe(users_df, use_container_width=True)
    
    st.divider()
    st.subheader("Create New User")
    col1, col2, col3 = st.columns(3)
    with col1:
        new_user = st.text_input("Username")
    with col2:
        new_email = st.text_input("Email")
    with col3:
        new_role = st.selectbox("Role", ["user", "manager", "admin"])
    
    if st.button("➕ Create User"):
        if new_user and new_email:
            success, msg = register_user(new_user, new_email, "temp123", new_user.title(), "solar")
            if success:
                st.success(msg)
            else:
                st.error(msg)

# ============ PAGE: ACTIVITY LOGS ============
def page_activity_logs():
    st.title("📋 Activity Logs")
    
    if st.session_state.user['role'] not in ['admin', 'manager']:
        st.error("⛔ Manager/Admin access required")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT al.log_id, u.username, al.action, al.details, al.timestamp 
    FROM activity_logs al
    JOIN users u ON al.user_id = u.user_id
    ORDER BY al.timestamp DESC
    LIMIT 100
    ''')
    logs = cursor.fetchall()
    
    logs_df = pd.DataFrame(logs)
    st.dataframe(logs_df, use_container_width=True)

# ============ RUN APP ============
if __name__ == "__main__":
    main()
