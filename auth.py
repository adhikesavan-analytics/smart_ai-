"""
Authentication Module for Smart Solar AI Dashboard
User authentication, session management, and security
"""

import streamlit as st
from database import verify_login, register_user, hash_password, get_user_api_key, update_user_api_keys, log_activity
from config import PASSWORD_MIN_LENGTH, SUPPORTED_AI_PROVIDERS
import re

# ============ VALIDATION ============
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    
    return True, "✅ Password is strong"

def validate_username(username):
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscore, and hyphen"
    
    return True, "✅ Username is valid"

# ============ LOGIN PAGE ============
def show_login_page():
    """Display professional login/signup page"""
    
    # Custom CSS for login page
    st.markdown("""
    <style>
        .login-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 40px;
        }
        .login-form {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .feature-list {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.2, 1], gap="large")
    
    with col1:
        st.markdown("# ☀️ Smart Solar AI")
        st.markdown("### Enterprise Analytics Platform")
        st.markdown("---")
        st.markdown("""
        #### 🚀 Enterprise Features:
        - **🔐** Secure Multi-User Authentication
        - **📤** Multi-File Upload & Management
        - **📊** Advanced Analytics & Dashboards
        - **🤖** AI-Powered Insights (Claude/ChatGPT)
        - **📈** Predictive Forecasting
        - **🔍** Anomaly Detection Engine
        - **💬** Natural Language AI Chat
        - **📄** PDF/Excel Report Generation
        - **🌍** Multi-Industry Support
        - **🔄** Complete History Tracking
        
        #### 🏭 Supported Industries:
        Solar • Manufacturing • Logistics • Retail
        """)
    
    with col2:
        st.markdown("### Access Your Dashboard")
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            st.markdown("#### Existing Users")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_btn = st.form_submit_button("🔓 Login", use_container_width=True)
                with col2:
                    st.form_submit_button("❓ Help", use_container_width=True)
                
                if login_btn:
                    if not username or not password:
                        st.error("⚠️ Please enter both username and password")
                    else:
                        user = verify_login(username, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.user_id = user['user_id']
                            log_activity(user['user_id'], 'LOGIN', f"User {username} logged in successfully")
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password!")
            
            st.divider()
            st.markdown("**Demo Credentials:**")
            with st.expander("👤 Click to view"):
                st.code("""Admin Account:
username: admin
password: admin123

Demo User:
username: demo1
password: password123""")
        
        with tab2:
            st.markdown("#### Create New Account")
            with st.form("signup_form"):
                new_username = st.text_input("Username", placeholder="Choose username (3+ chars)")
                new_email = st.text_input("Email", placeholder="Enter email")
                new_password = st.text_input("Password", type="password", placeholder="Min 8 chars, 1 digit, 1 uppercase")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                full_name = st.text_input("Full Name", placeholder="Enter your name")
                industry = st.selectbox("Industry", ["solar", "manufacturing", "logistics", "retail", "other"])
                
                signup_btn = st.form_submit_button("✅ Create Account", use_container_width=True)
                
                if signup_btn:
                    # Validation
                    errors = []
                    
                    if not new_username:
                        errors.append("Username is required")
                    else:
                        valid, msg = validate_username(new_username)
                        if not valid:
                            errors.append(f"Username: {msg}")
                    
                    if not new_email:
                        errors.append("Email is required")
                    elif not validate_email(new_email):
                        errors.append("Email format invalid")
                    
                    if not new_password:
                        errors.append("Password is required")
                    else:
                        valid, msg = validate_password(new_password)
                        if not valid:
                            errors.append(f"Password: {msg}")
                    
                    if new_password != confirm_password:
                        errors.append("Passwords don't match")
                    
                    if not full_name:
                        errors.append("Full name is required")
                    
                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        success, msg = register_user(new_username, new_email, new_password, full_name, industry)
                        if success:
                            st.success(msg)
                            st.info("Please login with your new credentials")
                        else:
                            st.error(msg)

# ============ LOGOUT ============
def logout():
    """Logout current user"""
    if st.session_state.get('user'):
        log_activity(st.session_state.user['user_id'], 'LOGOUT', 'User logged out')
    
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.uploaded_data = None
    st.session_state.current_file = None
    st.rerun()

# ============ API KEY MANAGEMENT ============
def show_api_key_settings():
    """Display API key management interface"""
    st.markdown("### 🔐 AI Provider Configuration")
    st.markdown("Configure your API keys to use AI features")
    
    user_id = st.session_state.get('user_id')
    
    tab1, tab2 = st.tabs(["Claude (Anthropic)", "ChatGPT (OpenAI)"])
    
    with tab1:
        st.subheader("Claude API Setup")
        st.markdown("""
        **Get your API Key:**
        1. Go to [console.anthropic.com](https://console.anthropic.com)
        2. Create an account or login
        3. Navigate to API Keys section
        4. Create a new API key
        5. Copy and paste below
        """)
        
        current_claude_key = get_user_api_key(user_id, 'claude')
        claude_key = st.text_input(
            "Claude API Key",
            value=current_claude_key or "",
            type="password",
            placeholder="sk-ant-xxxxxxxxxxxxx"
        )
        
        if st.button("💾 Save Claude API Key", key="save_claude"):
            if claude_key:
                if update_user_api_keys(user_id, claude_key=claude_key):
                    st.success("✅ Claude API key saved successfully!")
                    log_activity(user_id, 'UPDATE_API_KEY', 'Updated Claude API key')
                else:
                    st.error("❌ Failed to save API key")
            else:
                st.warning("⚠️ Please enter an API key")
    
    with tab2:
        st.subheader("ChatGPT API Setup")
        st.markdown("""
        **Get your API Key:**
        1. Go to [platform.openai.com](https://platform.openai.com)
        2. Create an account or login
        3. Navigate to API Keys
        4. Create a new API key
        5. Copy and paste below
        """)
        
        current_openai_key = get_user_api_key(user_id, 'openai')
        openai_key = st.text_input(
            "OpenAI API Key",
            value=current_openai_key or "",
            type="password",
            placeholder="sk-xxxxxxxxxxxxx"
        )
        
        if st.button("💾 Save ChatGPT API Key", key="save_openai"):
            if openai_key:
                if update_user_api_keys(user_id, openai_key=openai_key):
                    st.success("✅ ChatGPT API key saved successfully!")
                    log_activity(user_id, 'UPDATE_API_KEY', 'Updated OpenAI API key')
                else:
                    st.error("❌ Failed to save API key")
            else:
                st.warning("⚠️ Please enter an API key")
    
    st.info("""
    💡 **Privacy Note:** Your API keys are stored securely in our database.
    We never share them with third parties.
    """)

# ============ SESSION MANAGEMENT ============
def initialize_session():
    """Initialize session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.user_id = None
    
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
    
    if 'current_file_id' not in st.session_state:
        st.session_state.current_file_id = None
    
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def get_current_user():
    """Get current authenticated user"""
    return st.session_state.get('user')

def get_current_user_id():
    """Get current user ID"""
    return st.session_state.get('user_id')
