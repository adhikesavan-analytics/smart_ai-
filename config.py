"""
Configuration and Constants for Smart Solar AI Dashboard
"""

import os

# ============ APP CONFIG ============
APP_NAME = "☀️ Smart Solar AI Dashboard"
APP_VERSION = "2.0 - Production Ready"
APP_DESCRIPTION = "Enterprise-Grade Solar Analytics Platform"

# ============ DATABASE ============
DATABASE_NAME = "smart_solar_ai.db"
DATABASE_TIMEOUT = 20

# ============ FILE UPLOAD ============
ALLOWED_EXTENSIONS = ['csv', 'xlsx', 'xls']
MAX_FILE_SIZE_MB = 50  # Max 50MB per file
MAX_TOTAL_STORAGE_MB = 1000  # Max 1GB per user

# ============ SECURITY ============
PASSWORD_MIN_LENGTH = 8
SESSION_TIMEOUT_MINUTES = 480  # 8 hours
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

# ============ API KEYS ============
SUPPORTED_AI_PROVIDERS = ['Claude (Anthropic)', 'ChatGPT (OpenAI)']
DEFAULT_AI_MODEL = 'claude-opus-4-1-20250805'
CHATGPT_MODEL = 'gpt-4'

# ============ SOLAR INDUSTRY STANDARDS ============
SOLAR_KPI_TARGETS = {
    'efficiency': {'min': 0, 'max': 100, 'target': 85},
    'capacity_factor': {'min': 0, 'max': 100, 'target': 25},
    'availability': {'min': 0, 'max': 100, 'target': 95},
    'performance_ratio': {'min': 0, 'max': 100, 'target': 80},
}

# ============ LOGGING ============
LOG_LEVEL = "INFO"
LOG_FILE = "app_logs.txt"

# ============ UI CONFIG ============
SIDEBAR_WIDTH = 250
THEME_COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
}

# ============ ENVIRONMENT ============
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
DEBUG = ENVIRONMENT == 'development'
