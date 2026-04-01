"""
Smart Solar AI Dashboard - Production Ready
Enterprise-Grade Solar Analytics Platform
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

# Import modules
from config import *
from database import *
from auth import *
from utils import *

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title=APP_NAME,
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM CSS ============
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
    }
    .success-box { background: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 8px; }
    .warning-box { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; }
    .danger-box { background: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ============ INITIALIZATION ============
init_database()
initialize_session()

# ============ MAIN LOGIC ============
def main():
    if not is_authenticated():
        show_login_page()
    else:
        show_dashboard()

# ============ DASHBOARD UI ============
def show_dashboard():
    """Main dashboard interface"""
    
    # Sidebar
    with st.sidebar:
        user = get_current_user()
        st.markdown("### 👤 User Profile")
        st.markdown(f"**{user['full_name']}**")
        st.markdown(f"Role: {user['role'].upper()}")
        st.markdown(f"Industry: {user['industry'].title()}")
        st.divider()
        
        # Navigation
        st.markdown("### 📚 Navigation")
        page = st.radio(
            "Select Page",
            ["📊 Dashboard", "📤 Upload Files", "📈 Analytics", "💬 AI Chat", "📄 Reports", "⚙️ Settings", "🚪 Logout"],
            label_visibility="collapsed"
        )
        
        st.divider()
        st.caption(f"v{APP_VERSION}")
    
    # Page routing
    if page == "📊 Dashboard":
        page_dashboard()
    elif page == "📤 Upload Files":
        page_upload()
    elif page == "📈 Analytics":
        page_analytics()
    elif page == "💬 AI Chat":
        page_ai_chat()
    elif page == "📄 Reports":
        page_reports()
    elif page == "⚙️ Settings":
        page_settings()
    elif page == "🚪 Logout":
        logout()

# ============ PAGE: DASHBOARD ============
def page_dashboard():
    st.title("📊 Dashboard")
    
    user = get_current_user()
    user_id = get_current_user_id()
    
    # Get user's files
    files = get_user_files(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Files Uploaded", len(files))
    with col2:
        st.metric("Last Activity", "Today")
    with col3:
        st.metric("Industry", user['industry'].title())
    with col4:
        st.metric("Role", user['role'].upper())
    
    st.divider()
    
    if files:
        st.subheader("📂 Your Files")
        for file in files[:5]:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"📄 **{file['original_filename']}**")
                st.caption(f"Rows: {file['row_count']} | Cols: {file['column_count']} | {file['upload_date']}")
            with col2:
                if st.button("📊", key=f"analyze_{file['file_id']}", help="Analyze"):
                    st.session_state.current_file_id = file['file_id']
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"delete_{file['file_id']}", help="Delete"):
                    delete_file(file['file_id'], user_id)
                    st.rerun()
    else:
        st.info("📤 Start by uploading a file in the 'Upload Files' section!")
    
    st.divider()
    st.markdown("### ✨ Quick Start Guide")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**1️⃣ Upload File**\nGo to Upload Files → Select CSV/Excel")
    with col2:
        st.markdown("**2️⃣ Analyze Data**\nClick Analyze to see insights and KPIs")
    with col3:
        st.markdown("**3️⃣ Generate Report**\nExport PDF or Excel with recommendations")

# ============ PAGE: UPLOAD FILES ============
def page_upload():
    st.title("📤 Smart File Upload & Management")
    
    user_id = get_current_user_id()
    
    st.markdown("Upload CSV or Excel files • Auto-cleaning • Multi-file support")
    
    # Multi-file upload
    uploaded_files = st.file_uploader(
        "Choose files (CSV/Excel, max 50MB each)",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        success_count = 0
        for uploaded_file in uploaded_files:
            try:
                # Validate file
                file_size_mb = uploaded_file.size / (1024 * 1024)
                if file_size_mb > MAX_FILE_SIZE_MB:
                    st.error(f"❌ {uploaded_file.name}: File too large (max {MAX_FILE_SIZE_MB}MB)")
                    continue
                
                # Read file
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    # Validate
                    valid, msg = validate_file_data(df)
                    if not valid:
                        st.error(f"❌ {uploaded_file.name}: {msg}")
                        continue
                    
                    # Clean data
                    df_cleaned, clean_stats = clean_data(df)
                    
                    # Save to database
                    file_id = save_file_upload(
                        user_id,
                        f"{uploaded_file.name}_{datetime.now().timestamp()}",
                        uploaded_file.name,
                        uploaded_file.size,
                        uploaded_file.type,
                        len(df_cleaned),
                        len(df_cleaned.columns),
                        list(df_cleaned.columns)
                    )
                    
                    if file_id:
                        save_file_data(file_id, df_cleaned.to_json())
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Rows", clean_stats['cleaned_rows'])
                        with col2:
                            st.metric("Columns", clean_stats['final_cols'])
                        with col3:
                            st.metric("Cleaned", f"{clean_stats['rows_removed']} removed")
                        
                        st.success(f"✅ {uploaded_file.name} processed and saved!")
                        log_activity(user_id, 'FILE_UPLOAD', f"Uploaded {uploaded_file.name}")
                        success_count += 1
            
            except Exception as e:
                st.error(f"❌ {uploaded_file.name}: {str(e)}")
        
        if success_count > 0:
            st.info(f"✅ Successfully processed {success_count}/{len(uploaded_files)} file(s)")

# ============ PAGE: ANALYTICS ============
def page_analytics():
    st.title("📈 Advanced Analytics")
    
    user_id = get_current_user_id()
    files = get_user_files(user_id)
    
    if not files:
        st.warning("📤 No files uploaded yet")
        return
    
    # Select file
    file_options = {f['original_filename']: f['file_id'] for f in files}
    selected_file_name = st.selectbox("Select File", list(file_options.keys()))
    file_id = file_options[selected_file_name]
    
    # Load data
    df = pd.read_json(get_file_data(file_id))
    
    st.markdown(f"**File:** {selected_file_name} | **Rows:** {len(df)} | **Columns:** {len(df.columns)}")
    st.divider()
    
    tab1, tab2, tab3, tab4 = st.tabs(["KPIs", "Anomalies", "Forecast", "Insights"])
    
    with tab1:
        st.subheader("📊 Key Performance Indicators")
        kpis = calculate_solar_kpis(df)
        
        cols = st.columns(len(kpis) if kpis else 1)
        for i, (key, value) in enumerate(kpis.items()):
            with cols[i]:
                st.metric(key.title(), f"{value:.2f}")
    
    with tab2:
        st.subheader("🔍 Anomaly Detection")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            col = st.selectbox("Select Column", numeric_cols)
            anomalies_df, _, count = detect_anomalies(df, col)
            
            if count > 0:
                st.warning(f"⚠️ Found {count} anomalies")
                st.dataframe(anomalies_df, use_container_width=True)
            else:
                st.success("✅ No anomalies detected")
    
    with tab3:
        st.subheader("📈 Trend Forecast")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            col = st.selectbox("Select Column", numeric_cols, key="forecast_col")
            forecast_df, slope = forecast_trend(df, col, periods=6)
            
            if forecast_df is not None:
                st.dataframe(forecast_df, use_container_width=True)
                st.info(f"Trend: {'Increasing' if slope > 0 else 'Decreasing'} ({slope:.2f}/period)")
    
    with tab4:
        st.subheader("✨ AI-Generated Insights")
        insights = generate_solar_insights(df)
        for insight in insights:
            st.markdown(f"• {insight}")

# ============ PAGE: AI CHAT ============
def page_ai_chat():
    st.title("💬 AI Chat Assistant")
    
    user_id = get_current_user_id()
    
    # Get Claude API key
    claude_key = get_user_api_key(user_id, 'claude')
    
    if not claude_key:
        st.warning("⚠️ Claude API key not configured. Go to Settings to configure it.")
        return
    
    # Chat interface
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Ask about your data..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            st.write("🤖 Processing...")  # Placeholder
            
            # In real implementation, call Claude API here
            response = f"Thank you for your question: {prompt}\n\n[AI response would go here with Claude API integration]"
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()

# ============ PAGE: REPORTS ============
def page_reports():
    st.title("📄 Report Generation")
    
    user_id = get_current_user_id()
    files = get_user_files(user_id)
    
    if not files:
        st.warning("📤 No files available for reporting")
        return
    
    file_options = {f['original_filename']: f['file_id'] for f in files}
    selected_file = st.selectbox("Select File", list(file_options.keys()))
    file_id = file_options[selected_file]
    
    df = pd.read_json(get_file_data(file_id))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export as CSV", use_container_width=True):
            csv = prepare_csv_export(df)
            st.download_button(
                "Download CSV",
                csv,
                f"{selected_file.replace(' ', '_')}.csv",
                "text/csv"
            )
            log_activity(user_id, 'EXPORT', f'Exported {selected_file} as CSV')
    
    with col2:
        if st.button("📥 Export as JSON", use_container_width=True):
            json_data = prepare_json_export(df.to_dict())
            st.download_button(
                "Download JSON",
                json_data,
                f"{selected_file.replace(' ', '_')}.json",
                "application/json"
            )
            log_activity(user_id, 'EXPORT', f'Exported {selected_file} as JSON')
    
    st.divider()
    
    kpis = calculate_solar_kpis(df)
    recommendations = generate_recommendations(df, kpis)
    
    st.subheader("📋 Recommendations")
    for rec in recommendations:
        st.markdown(f"""
        **{rec['priority']} {rec['action']}**
        - Reason: {rec['reason']}
        - Potential: {rec['savings']}
        """)

# ============ PAGE: SETTINGS ============
def page_settings():
    st.title("⚙️ Settings & Configuration")
    
    tab1, tab2, tab3 = st.tabs(["API Keys", "Profile", "Activity"])
    
    with tab1:
        show_api_key_settings()
    
    with tab2:
        st.subheader("👤 Profile Information")
        user = get_current_user()
        st.text_input("Username", value=user['username'], disabled=True)
        st.text_input("Email", value=user['email'], disabled=True)
        st.text_input("Full Name", value=user['full_name'], disabled=True)
        st.text_input("Industry", value=user['industry'], disabled=True)
    
    with tab3:
        st.subheader("📋 Activity History")
        user_id = get_current_user_id()
        activities = get_user_activity(user_id, limit=50)
        
        if activities:
            activities_df = pd.DataFrame([
                {
                    'Action': a['action'],
                    'Details': a['details'],
                    'Time': a['timestamp'],
                    'Status': a['status']
                }
                for a in activities
            ])
            st.dataframe(activities_df, use_container_width=True)
        else:
            st.info("No activity recorded yet")

# ============ RUN APP ============
if __name__ == "__main__":
    main()
