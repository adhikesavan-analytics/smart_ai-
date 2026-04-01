"""
Enterprise Database Module - Admin-Controlled System
Handles users, roles, data, KPIs, activity logging, and analytics
"""

import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import streamlit as st
from app_config import DATABASE_NAME, DATABASE_TIMEOUT

# ============ DATABASE CONNECTION ============
@st.cache_resource
def get_db():
    """Get cached database connection"""
    conn = sqlite3.connect(DATABASE_NAME, timeout=DATABASE_TIMEOUT, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ============ INITIALIZATION ============
def init_enterprise_db():
    """Initialize enterprise database with all tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table with role-based access
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
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        FOREIGN KEY(created_by) REFERENCES users(user_id)
    )
    ''')
    
    # API Keys
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_keys (
        key_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        provider TEXT,
        api_key TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_used TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # File uploads
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
        data_preview TEXT,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # File data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS file_data (
        data_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL,
        data_json LONGTEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(file_id) REFERENCES file_uploads(file_id)
    )
    ''')
    
    # Custom KPI configurations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_kpis (
        kpi_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        kpi_name TEXT NOT NULL,
        description TEXT,
        metric_column TEXT,
        calculation_type TEXT,
        industry TEXT,
        target_value REAL,
        threshold_value REAL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Analysis results
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_cache (
        analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL,
        analysis_type TEXT,
        results_json LONGTEXT,
        anomaly_count INTEGER,
        insights TEXT,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(file_id) REFERENCES file_uploads(file_id)
    )
    ''')
    
    # Predictions/Forecasts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        pred_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        column_name TEXT,
        forecast_data TEXT,
        confidence_score REAL,
        periods INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(file_id) REFERENCES file_uploads(file_id),
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Activity logs (audit trail)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        resource_type TEXT,
        resource_id INTEGER,
        details TEXT,
        status TEXT DEFAULT 'success',
        ip_address TEXT,
        user_agent TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Admin actions log
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_actions (
        action_id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        action_type TEXT,
        target_user_id INTEGER,
        description TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(admin_id) REFERENCES users(user_id),
        FOREIGN KEY(target_user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Recommendations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        recommendation TEXT,
        priority TEXT,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(file_id) REFERENCES file_uploads(file_id),
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    # Create default admin
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, role)
        VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@smartbi.com', admin_hash, 'System Administrator', 'admin'))
    
    conn.commit()

# ============ USER MANAGEMENT ============
def hash_password(password: str) -> str:
    """Hash password"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username: str, password: str) -> Optional[Dict]:
    """Verify user credentials"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
    user = cursor.fetchone()
    
    if user and user['password_hash'] == hash_password(password):
        # Update last login
        cursor.execute('UPDATE users SET last_login = ? WHERE user_id = ?', 
                      (datetime.now(), user['user_id']))
        conn.commit()
        return dict(user)
    return None

def create_user_by_admin(username: str, email: str, password: str, full_name: str, 
                        industry: str, role: str, admin_id: int) -> Tuple[bool, str]:
    """Create user (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        pwd_hash = hash_password(password)
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, industry, role, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, pwd_hash, full_name, industry, role, admin_id))
        conn.commit()
        
        # Log admin action
        new_user_id = cursor.lastrowid
        log_admin_action(admin_id, 'CREATE_USER', new_user_id, f'Created user {username}')
        
        return True, f"✅ User {username} created successfully"
    except sqlite3.IntegrityError:
        return False, "❌ Username or email already exists"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def delete_user_by_admin(user_id: int, admin_id: int) -> Tuple[bool, str]:
    """Delete user (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET is_active = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
        
        log_admin_action(admin_id, 'DELETE_USER', user_id, f'Deleted user ID {user_id}')
        
        return True, "✅ User deleted successfully"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def reset_user_password(user_id: int, new_password: str, admin_id: int) -> Tuple[bool, str]:
    """Reset user password (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        pwd_hash = hash_password(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE user_id = ?', 
                      (pwd_hash, user_id))
        conn.commit()
        
        log_admin_action(admin_id, 'RESET_PASSWORD', user_id, f'Reset password for user ID {user_id}')
        
        return True, "✅ Password reset successfully"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def get_all_users() -> List[Dict]:
    """Get all users"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, email, full_name, role, is_active, created_at, last_login FROM users ORDER BY created_at DESC')
    return [dict(row) for row in cursor.fetchall()]

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    return dict(user) if user else None

# ============ API KEY MANAGEMENT ============
def save_api_key(user_id: int, provider: str, api_key: str) -> bool:
    """Save API key"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM api_keys WHERE user_id = ? AND provider = ?', 
                      (user_id, provider))
        cursor.execute('''
        INSERT INTO api_keys (user_id, provider, api_key)
        VALUES (?, ?, ?)
        ''', (user_id, provider, api_key))
        conn.commit()
        log_activity(user_id, 'SAVE_API_KEY', 'api_keys', 0, f'Saved {provider} API key')
        return True
    except Exception as e:
        return False

def get_api_key(user_id: int, provider: str) -> Optional[str]:
    """Get API key"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT api_key FROM api_keys WHERE user_id = ? AND provider = ? AND is_active = 1', 
                  (user_id, provider))
    result = cursor.fetchone()
    if result:
        cursor.execute('UPDATE api_keys SET last_used = ? WHERE user_id = ? AND provider = ?',
                      (datetime.now(), user_id, provider))
        conn.commit()
    return result['api_key'] if result else None

# ============ FILE OPERATIONS ============
def save_file(user_id: int, filename: str, original_filename: str, file_size: int, 
              file_type: str, row_count: int, column_count: int, columns_list: List, 
              data_preview: str) -> int:
    """Save file upload"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO file_uploads (user_id, filename, original_filename, file_size, file_type, 
                                 row_count, column_count, columns_list, data_preview)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, filename, original_filename, file_size, file_type, row_count, 
              column_count, json.dumps(columns_list), data_preview))
        conn.commit()
        
        file_id = cursor.lastrowid
        log_activity(user_id, 'FILE_UPLOAD', 'file_uploads', file_id, f'Uploaded {original_filename}')
        
        return file_id
    except Exception as e:
        return None

def save_file_data(file_id: int, data_json: str) -> bool:
    """Save file data"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO file_data (file_id, data_json) VALUES (?, ?)',
                      (file_id, data_json))
        conn.commit()
        return True
    except:
        return False

def get_user_files(user_id: int) -> List[Dict]:
    """Get user's files"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM file_uploads WHERE user_id = ? AND is_active = 1
    ORDER BY upload_date DESC
    ''', (user_id,))
    return [dict(row) for row in cursor.fetchall()]

def get_file_data(file_id: int) -> Optional[str]:
    """Get file data"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT data_json FROM file_data WHERE file_id = ? ORDER BY created_at DESC LIMIT 1', 
                  (file_id,))
    result = cursor.fetchone()
    return result['data_json'] if result else None

def delete_file(file_id: int, user_id: int) -> bool:
    """Delete file (soft delete)"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE file_uploads SET is_active = 0 WHERE file_id = ? AND user_id = ?',
                      (file_id, user_id))
        conn.commit()
        log_activity(user_id, 'FILE_DELETE', 'file_uploads', file_id, 'Deleted file')
        return True
    except:
        return False

# ============ KPI MANAGEMENT ============
def save_custom_kpi(user_id: int, kpi_name: str, description: str, metric_column: str,
                   calculation_type: str, industry: str, target: float = None) -> bool:
    """Save custom KPI"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO custom_kpis (user_id, kpi_name, description, metric_column, 
                               calculation_type, industry, target_value)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, kpi_name, description, metric_column, calculation_type, industry, target))
        conn.commit()
        log_activity(user_id, 'CREATE_KPI', 'custom_kpis', 0, f'Created KPI: {kpi_name}')
        return True
    except Exception as e:
        return False

def get_user_kpis(user_id: int, industry: str = None) -> List[Dict]:
    """Get user's KPIs"""
    conn = get_db()
    cursor = conn.cursor()
    if industry:
        cursor.execute('''
        SELECT * FROM custom_kpis WHERE user_id = ? AND industry = ? AND is_active = 1
        ''', (user_id, industry))
    else:
        cursor.execute('''
        SELECT * FROM custom_kpis WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
    return [dict(row) for row in cursor.fetchall()]

# ============ ACTIVITY LOGGING ============
def log_activity(user_id: int, action: str, resource_type: str, resource_id: int, 
                details: str, status: str = 'success') -> None:
    """Log user activity"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO activity_logs (user_id, action, resource_type, resource_id, details, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, action, resource_type, resource_id, details, status))
        conn.commit()
    except:
        pass

def log_admin_action(admin_id: int, action_type: str, target_user_id: int = None, 
                    description: str = "") -> None:
    """Log admin action"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO admin_actions (admin_id, action_type, target_user_id, description)
        VALUES (?, ?, ?, ?)
        ''', (admin_id, action_type, target_user_id, description))
        conn.commit()
    except:
        pass

def get_user_activity(user_id: int, limit: int = 100) -> List[Dict]:
    """Get user's activity log"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM activity_logs WHERE user_id = ?
    ORDER BY timestamp DESC LIMIT ?
    ''', (user_id, limit))
    return [dict(row) for row in cursor.fetchall()]

def get_all_activity_logs(limit: int = 500) -> List[Dict]:
    """Get all activity logs (admin view)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT l.*, u.username FROM activity_logs l
    LEFT JOIN users u ON l.user_id = u.user_id
    ORDER BY l.timestamp DESC LIMIT ?
    ''', (limit,))
    return [dict(row) for row in cursor.fetchall()]

# ============ RECOMMENDATIONS ============
def save_recommendations(file_id: int, user_id: int, recommendations: List[Dict]) -> bool:
    """Save AI recommendations"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        for rec in recommendations:
            cursor.execute('''
            INSERT INTO recommendations (file_id, user_id, recommendation, priority, category)
            VALUES (?, ?, ?, ?, ?)
            ''', (file_id, user_id, rec.get('text'), rec.get('priority'), rec.get('category')))
        conn.commit()
        return True
    except:
        return False

def get_recommendations(file_id: int) -> List[Dict]:
    """Get recommendations for a file"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM recommendations WHERE file_id = ?
    ORDER BY created_at DESC
    ''', (file_id,))
    return [dict(row) for row in cursor.fetchall()]
