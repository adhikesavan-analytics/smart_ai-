"""
Database Module for Smart Solar AI Dashboard
Handles all database operations and schema management
"""

import sqlite3
import hashlib
import json
from datetime import datetime
from config import DATABASE_NAME, DATABASE_TIMEOUT
import streamlit as st

# ============ DATABASE CONNECTION ============
@st.cache_resource
def get_db_connection():
    """Get cached database connection"""
    conn = sqlite3.connect(DATABASE_NAME, timeout=DATABASE_TIMEOUT, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ============ SCHEMA INITIALIZATION ============
def init_database():
    """Initialize all database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        industry TEXT DEFAULT 'solar',
        role TEXT DEFAULT 'user',
        is_active BOOLEAN DEFAULT 1,
        api_key_claude TEXT,
        api_key_openai TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Companies table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL UNIQUE,
        company_email TEXT,
        industry TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # File uploads table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS file_uploads (
        file_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        original_filename TEXT,
        file_size INTEGER,
        file_type TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        row_count INTEGER,
        column_count INTEGER,
        columns_list TEXT,
        is_active BOOLEAN DEFAULT 1,
        version INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # File data storage table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS file_data (
        data_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL,
        data_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(file_id) REFERENCES file_uploads(file_id)
    )
    ''')
    
    # KPI Configuration
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kpi_config (
        kpi_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file_id INTEGER,
        kpi_name TEXT,
        metric_column TEXT,
        calculation_type TEXT,
        threshold_value REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(file_id) REFERENCES file_uploads(file_id)
    )
    ''')
    
    # Analysis Results
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_results (
        analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        analysis_type TEXT,
        results_json TEXT,
        confidence_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(file_id) REFERENCES file_uploads(file_id),
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Predictions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        pred_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        prediction_type TEXT,
        target_variable TEXT,
        forecast_data TEXT,
        accuracy_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(file_id) REFERENCES file_uploads(file_id),
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Anomalies
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anomalies (
        anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        anomaly_type TEXT,
        description TEXT,
        severity TEXT,
        value REAL,
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(file_id) REFERENCES file_uploads(file_id),
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Chat history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file_id INTEGER,
        message TEXT,
        response TEXT,
        ai_provider TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(file_id) REFERENCES file_uploads(file_id)
    )
    ''')
    
    # Activity logs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        action TEXT,
        details TEXT,
        status TEXT DEFAULT 'success',
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
    
    # Add demo users
    cursor.execute("SELECT * FROM users WHERE username = 'demo1'")
    if not cursor.fetchone():
        demo_hash = hashlib.sha256('password123'.encode()).hexdigest()
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, role, industry)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('demo1', 'demo1@smartsolar.com', demo_hash, 'Demo User', 'user', 'solar'))
    
    conn.commit()

# ============ USER OPERATIONS ============
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    """Verify user credentials"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
    user = cursor.fetchone()
    
    if user and user['password_hash'] == hash_password(password):
        return dict(user)
    return None

def register_user(username, email, password, full_name, industry='solar'):
    """Register new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        pwd_hash = hash_password(password)
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, industry)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, email, pwd_hash, full_name, industry))
        conn.commit()
        return True, "✅ Account created! Please login."
    except sqlite3.IntegrityError as e:
        return False, f"❌ Error: {str(e)}"

def update_user_api_keys(user_id, claude_key=None, openai_key=None):
    """Update user's API keys"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if claude_key:
            cursor.execute('UPDATE users SET api_key_claude = ? WHERE user_id = ?', (claude_key, user_id))
        if openai_key:
            cursor.execute('UPDATE users SET api_key_openai = ? WHERE user_id = ?', (openai_key, user_id))
        cursor.execute('UPDATE users SET updated_at = ? WHERE user_id = ?', (datetime.now(), user_id))
        conn.commit()
        return True
    except Exception as e:
        return False

def get_user_api_key(user_id, provider='claude'):
    """Get user's API key for specific provider"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT api_key_claude, api_key_openai FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        if provider.lower() == 'claude':
            return user['api_key_claude']
        elif provider.lower() == 'openai':
            return user['api_key_openai']
    return None

# ============ FILE UPLOAD OPERATIONS ============
def save_file_upload(user_id, filename, original_filename, file_size, file_type, row_count, column_count, columns_list):
    """Save file upload metadata"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO file_uploads (user_id, filename, original_filename, file_size, file_type, row_count, column_count, columns_list)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, filename, original_filename, file_size, file_type, row_count, column_count, json.dumps(columns_list)))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        return None

def save_file_data(file_id, data_json):
    """Save file data to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO file_data (file_id, data_json)
        VALUES (?, ?)
        ''', (file_id, data_json))
        conn.commit()
        return True
    except Exception as e:
        return False

def get_user_files(user_id):
    """Get all files uploaded by user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM file_uploads 
    WHERE user_id = ? AND is_active = 1
    ORDER BY upload_date DESC
    ''', (user_id,))
    return cursor.fetchall()

def get_file_data(file_id):
    """Get file data from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT data_json FROM file_data WHERE file_id = ? ORDER BY created_at DESC LIMIT 1', (file_id,))
    result = cursor.fetchone()
    if result:
        return json.loads(result['data_json'])
    return None

def delete_file(file_id, user_id):
    """Soft delete a file"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE file_uploads SET is_active = 0 WHERE file_id = ? AND user_id = ?', (file_id, user_id))
    conn.commit()

# ============ ANALYSIS OPERATIONS ============
def save_analysis_result(file_id, user_id, analysis_type, results_json, confidence_score=None):
    """Save analysis results"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO analysis_results (file_id, user_id, analysis_type, results_json, confidence_score)
        VALUES (?, ?, ?, ?, ?)
        ''', (file_id, user_id, analysis_type, results_json, confidence_score))
        conn.commit()
        return True
    except Exception as e:
        return False

def get_analysis_results(file_id, analysis_type=None):
    """Get analysis results for a file"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if analysis_type:
        cursor.execute('''
        SELECT * FROM analysis_results 
        WHERE file_id = ? AND analysis_type = ?
        ORDER BY created_at DESC
        ''', (file_id, analysis_type))
    else:
        cursor.execute('''
        SELECT * FROM analysis_results 
        WHERE file_id = ?
        ORDER BY created_at DESC
        ''', (file_id,))
    return cursor.fetchall()

# ============ ACTIVITY LOGGING ============
def log_activity(user_id, action, details="", status="success"):
    """Log user activity"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO activity_logs (user_id, action, details, status)
        VALUES (?, ?, ?, ?)
        ''', (user_id, action, details, status))
        conn.commit()
    except Exception as e:
        pass

def get_user_activity(user_id, limit=100):
    """Get user activity history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM activity_logs 
    WHERE user_id = ?
    ORDER BY timestamp DESC
    LIMIT ?
    ''', (user_id, limit))
    return cursor.fetchall()
