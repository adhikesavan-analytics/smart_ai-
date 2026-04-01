"""
Smart BI Analytics - Enterprise Edition
Complete AI-driven Business Intelligence Platform
Multi-industry, admin-controlled, production-ready
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
from datetime import datetime
from io import BytesIO

# Import modules
from app_config import *
from enterprise_db import *
from analytics_engine import *
from ai_engine import *

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM CSS ============
st.markdown("""
<style>
    /* Main styling */
    [data-testid="stMetricValue"] { font-size: 28px; }
    [data-testid="stMetricLabel"] { font-size: 14px; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Success/Warning/Error boxes */
    .success-box { 
        background: #d4edda; 
        border-left: 4px solid #28a745; 
        padding: 15px; 
        border-radius: 8px;
    }
    .warning-box { 
        background: #fff3cd; 
        border-left: 4px solid #ffc107; 
        padding: 15px; 
        border-radius: 8px;
    }
    .danger-box { 
        background: #f8d7da; 
        border-left: 4px solid #dc3545; 
        padding: 15px; 
        border-radius: 8px;
    }
    
    /* Header */
    .header-title { 
        font-size: 32px; 
        font-weight: bold; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ============ INITIALIZATION ============
init_enterprise_db()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.current_file = None

# ============ MAIN APP ============
def main():
    if not st.session_state.authenticated:
        show_login()
    else:
        show_dashboard()

# ============ LOGIN PAGE ============
def show_login():
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.markdown(f"# {APP_NAME}")
        st.markdown(f"### {APP_SUBTITLE}")
        st.markdown("---")
        
        st.markdown("### ✨ Enterprise Features")
        features = [
            "⚡ Real-Time Analytics Dashboard",
            "🔮 Predictive Analytics & Forecasting",
            "🔍 Anomaly Detection Engine",
            "⚙️ Custom KPI Builder",
            "💡 AI Recommendations (Claude)",
            "📄 PDF/Excel Reports",
            "🌍 Multi-Industry Support",
            "🔐 Admin Controls & Activity Logs"
        ]
        for feature in features:
            st.markdown(f"- {feature}")
    
    with col2:
        st.markdown("### 🔐 Login")
        
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password", placeholder="admin123")
        
        if st.button("🔓 Login", use_container_width=True, key="login_btn"):
            user = verify_login(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = dict(user)
                log_activity(user['user_id'], 'LOGIN', 'auth', 0, f'User {username} logged in')
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
        
        st.divider()
        
        with st.expander("👤 Demo Credentials"):
            st.code("""
admin / admin123
demo1 / demo123
demo2 / demo123
""")

# ============ DASHBOARD ============
def show_dashboard():
    user = st.session_state.user
    user_id = user['user_id']
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {user['full_name']}")
        st.markdown(f"Role: **{user['role'].upper()}**")
        st.markdown(f"Industry: **{user['industry'].title()}**")
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📤 Upload Data", "📈 Analytics", "💬 AI Chat", 
             "📄 Reports", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        if user['role'] == 'admin':
            st.divider()
            st.markdown("### 🔴 Admin Panel")
            admin_page = st.radio(
                "Admin Tools",
                ["👥 Users", "📋 Activity Logs", "🔧 System Settings"],
                label_visibility="collapsed"
            )
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            log_activity(user_id, 'LOGOUT', 'auth', 0, 'User logged out')
            st.session_state.authenticated = False
            st.rerun()
    
    # Page routing
    if user['role'] == 'admin' and 'admin_page' in locals():
        if admin_page == "👥 Users":
            show_user_management(user_id)
        elif admin_page == "📋 Activity Logs":
            show_activity_logs()
        elif admin_page == "🔧 System Settings":
            show_system_settings()
    
    if page == "📊 Dashboard":
        show_home_dashboard(user_id, user['industry'])
    elif page == "📤 Upload Data":
        show_upload_page(user_id)
    elif page == "📈 Analytics":
        show_analytics_page(user_id, user['industry'])
    elif page == "💬 AI Chat":
        show_chat_page(user_id, user['industry'])
    elif page == "📄 Reports":
        show_reports_page(user_id)
    elif page == "⚙️ Settings":
        show_settings_page(user_id)

# ============ PAGE: HOME DASHBOARD ============
def show_home_dashboard(user_id: int, industry: str):
    st.title("📊 Analytics Dashboard")
    st.markdown(f"Welcome back! | Industry: **{industry.title()}** | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.divider()
    
    files = get_user_files(user_id)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Files Uploaded", len(files))
    with col2:
        st.metric("Active Analyses", "3")
    with col3:
        st.metric("KPIs Created", "7")
    with col4:
        st.metric("Insights Generated", "24")
    
    st.divider()
    
    if files:
        st.subheader("📂 Recent Files")
        for file in files[:3]:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"**{file['original_filename']}** | {file['row_count']} rows × {file['column_count']} cols")
            with col2:
                if st.button("📊", key=f"viz_{file['file_id']}"):
                    st.session_state.current_file = file['file_id']
                    st.rerun()
            with col3:
                if st.button("📈", key=f"ana_{file['file_id']}"):
                    st.session_state.current_file = file['file_id']
            with col4:
                if st.button("🗑️", key=f"del_{file['file_id']}"):
                    delete_file(file['file_id'], user_id)
                    st.rerun()
    else:
        st.info("📤 Upload data to get started!")

# ============ PAGE: UPLOAD ============
def show_upload_page(user_id: int):
    st.title("📤 Smart Data Upload")
    st.markdown("Upload multiple files • Auto-cleaning • Industry detection")
    
    uploaded_files = st.file_uploader(
        "Upload CSV/Excel files",
        type=['csv', 'xlsx'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        progress_bar = st.progress(0)
        for idx, file in enumerate(uploaded_files):
            try:
                # Read file
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # Validate
                if len(df) == 0:
                    st.error(f"❌ {file.name}: Empty file")
                    continue
                
                # Save
                file_id = save_file(
                    user_id, 
                    f"{file.name}_{datetime.now().timestamp()}",
                    file.name,
                    file.size,
                    file.type,
                    len(df),
                    len(df.columns),
                    list(df.columns),
                    df.head(5).to_json()
                )
                
                if file_id:
                    save_file_data(file_id, df.to_json())
                    st.success(f"✅ {file.name} uploaded ({len(df)} rows)")
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            except Exception as e:
                st.error(f"❌ {file.name}: {str(e)}")

# ============ PAGE: ANALYTICS ============
def show_analytics_page(user_id: int, industry: str):
    st.title("📈 Advanced Analytics")
    
    files = get_user_files(user_id)
    if not files:
        st.warning("📤 No files uploaded")
        return
    
    file_options = {f['original_filename']: f['file_id'] for f in files}
    selected_file = st.selectbox("Select File", list(file_options.keys()))
    file_id = file_options[selected_file]
    
    # Load data
    data_json = get_file_data(file_id)
    if not data_json:
        st.error("Unable to load file data")
        return
    
    df = pd.read_json(data_json)
    
    st.subheader(f"📊 {selected_file}")
    st.caption(f"{len(df)} records × {len(df.columns)} columns")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 KPIs", "🔍 Anomalies", "🔮 Forecast", "📋 Data", "✨ Insights"])
    
    with tab1:
        st.markdown("### Key Performance Indicators")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            col_selection = st.multiselect("Select columns for analysis", numeric_cols, default=numeric_cols[:3])
            
            kpi_cols = st.columns(len(col_selection) if col_selection else 1)
            for idx, col in enumerate(col_selection):
                with kpi_cols[idx]:
                    avg_val = calculate_kpi(df, col, 'average')
                    max_val = calculate_kpi(df, col, 'max')
                    
                    fig = create_gauge_chart(avg_val, max_val, col)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Time series if possible
            if 'date' in [c.lower() for c in df.columns] or 'time' in [c.lower() for c in df.columns]:
                st.markdown("### Trend Analysis")
                for col in col_selection[:2]:
                    fig = create_line_chart(df, df.columns[0], col, f"{col} Trend")
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Anomaly Detection")
        
        col = st.selectbox("Select column", numeric_cols)
        method = st.radio("Detection method", ["zscore", "iqr"], horizontal=True)
        threshold = st.slider("Threshold", 1.0, 4.0, 2.5)
        
        if st.button("🔍 Detect Anomalies"):
            anomalies_df, count = detect_anomalies(df, col, method, threshold)
            
            if count > 0:
                st.warning(f"⚠️ Found {count} anomalies ({count/len(df)*100:.1f}%)")
                st.dataframe(anomalies_df, use_container_width=True)
            else:
                st.success("✅ No anomalies detected")
    
    with tab3:
        st.markdown("### Predictive Forecasting")
        
        col = st.selectbox("Forecast column", numeric_cols, key="forecast_col")
        periods = st.slider("Periods to forecast", 3, 12, 6)
        method = st.radio("Method", ["linear", "exponential"], horizontal=True)
        
        if st.button("🔮 Generate Forecast"):
            forecast_df, slope = forecast_values(df, col, periods, method)
            
            if forecast_df is not None:
                st.dataframe(forecast_df, use_container_width=True)
                st.info(f"Trend: {'📈 Upward' if slope > 0 else '📉 Downward'} ({slope:.2f}/period)")
    
    with tab4:
        st.markdown("### Data Preview")
        st.dataframe(df, use_container_width=True)
    
    with tab5:
        st.markdown("### AI-Generated Insights")
        
        if st.button("✨ Generate Insights"):
            with st.spinner("Analyzing data with Claude..."):
                success, insights = analyze_with_claude(user_id, df, industry)
                
                if success:
                    st.markdown(insights)
                else:
                    st.error(insights)

# ============ PAGE: AI CHAT ============
def show_chat_page(user_id: int, industry: str):
    st.title("💬 AI Data Chat")
    
    files = get_user_files(user_id)
    if not files:
        st.warning("📤 No files to analyze")
        return
    
    file_options = {f['original_filename']: f['file_id'] for f in files}
    selected_file = st.selectbox("Select File", list(file_options.keys()))
    file_id = file_options[selected_file]
    
    # Check API key
    success, msg = check_api_connection(user_id)
    if not success:
        st.error(msg)
        st.info("👉 Go to Settings to add your Claude API key")
        return
    
    # Load data
    data_json = get_file_data(file_id)
    df = pd.read_json(data_json)
    
    # Chat interface
    st.markdown("Ask anything about your data...")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Ask about your data..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_with_data(user_id, df, prompt)
                st.write(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

# ============ PAGE: REPORTS ============
def show_reports_page(user_id: int):
    st.title("📄 Report Generation")
    
    files = get_user_files(user_id)
    if not files:
        st.warning("📤 No files available")
        return
    
    file_options = {f['original_filename']: f['file_id'] for f in files}
    selected_file = st.selectbox("Select File", list(file_options.keys()))
    file_id = file_options[selected_file]
    
    data_json = get_file_data(file_id)
    df = pd.read_json(data_json)
    
    st.markdown("### Download Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Download CSV", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button("Get CSV", csv, f"{selected_file}.csv", "text/csv")
    
    with col2:
        if st.button("📥 Download Excel", use_container_width=True):
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)
            st.download_button("Get Excel", buffer, f"{selected_file}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    with col3:
        if st.button("📥 Download JSON", use_container_width=True):
            json_str = df.to_json(indent=2)
            st.download_button("Get JSON", json_str, f"{selected_file}.json", "application/json")

# ============ PAGE: SETTINGS ============
def show_settings_page(user_id: int):
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["🔐 API Keys", "👤 Profile", "📋 Activity"])
    
    with tab1:
        st.markdown("### Configure AI Providers")
        
        claude_key = st.text_input("Claude API Key", type="password", placeholder="sk-ant-...")
        if st.button("💾 Save Claude Key"):
            if save_api_key(user_id, 'claude', claude_key):
                st.success("✅ Claude API key saved")
            else:
                st.error("❌ Failed to save")
        
        success, msg = check_api_connection(user_id)
        if success:
            st.success(msg)
        else:
            st.warning(msg)
    
    with tab2:
        st.markdown("### Profile Information")
        user = st.session_state.user
        st.text_input("Username", value=user['username'], disabled=True)
        st.text_input("Email", value=user['email'], disabled=True)
        st.text_input("Full Name", value=user['full_name'], disabled=True)
    
    with tab3:
        st.markdown("### Activity History")
        activities = get_user_activity(user_id, 50)
        
        if activities:
            activity_data = [{
                'Time': a['timestamp'],
                'Action': a['action'],
                'Details': a['details']
            } for a in activities]
            st.dataframe(pd.DataFrame(activity_data), use_container_width=True)

# ============ ADMIN: USER MANAGEMENT ============
def show_user_management(admin_id: int):
    st.title("👥 User Management")
    
    tab1, tab2 = st.tabs(["Create User", "Manage Users"])
    
    with tab1:
        st.markdown("### Create New User")
        
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        full_name = st.text_input("Full Name")
        industry = st.selectbox("Industry", list(INDUSTRIES.keys()))
        role = st.selectbox("Role", list(ROLES.keys()))
        
        if st.button("✅ Create User"):
            success, msg = create_user_by_admin(username, email, password, full_name, industry, role, admin_id)
            if success:
                st.success(msg)
            else:
                st.error(msg)
    
    with tab2:
        st.markdown("### All Users")
        users = get_all_users()
        
        for user in users:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"**{user['username']}** - {user['full_name']}")
                st.caption(f"{user['email']} | {user['role']}")
            with col2:
                if st.button("🔄", key=f"reset_{user['user_id']}", help="Reset password"):
                    new_pass = f"temp_{user['user_id']}"
                    reset_user_password(user['user_id'], new_pass, admin_id)
                    st.success(f"Temp password: {new_pass}")
            with col3:
                status = "✅" if user['is_active'] else "❌"
                st.write(status)
            with col4:
                if st.button("🗑️", key=f"delete_{user['user_id']}"):
                    delete_user_by_admin(user['user_id'], admin_id)
                    st.rerun()

# ============ ADMIN: ACTIVITY LOGS ============
def show_activity_logs():
    st.title("📋 Activity Logs")
    
    logs = get_all_activity_logs(500)
    
    if logs:
        log_df = pd.DataFrame([{
            'Time': l['timestamp'],
            'User': l['username'],
            'Action': l['action'],
            'Details': l['details'],
            'Status': l['status']
        } for l in logs])
        
        st.dataframe(log_df, use_container_width=True)

# ============ ADMIN: SYSTEM SETTINGS ============
def show_system_settings():
    st.title("🔧 System Settings")
    
    st.markdown("### About")
    st.markdown(f"""
    **App Name:** {APP_NAME}
    **Version:** {APP_VERSION}
    **Tagline:** {APP_TAGLINE}
    """)
    
    st.markdown("### Features")
    for feature_key, feature in FEATURES.items():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{feature['icon']} {feature['name']}** - {feature['description']}")
        with col2:
            status = "✅" if feature['enabled'] else "❌"
            st.write(status)

# ============ RUN APP ============
if __name__ == "__main__":
    main()
