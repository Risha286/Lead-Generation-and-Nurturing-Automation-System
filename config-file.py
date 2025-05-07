# Database Configuration
DATABASE_CONFIG = {
    'database': 'leads.db',
    'backup_path': 'backups/'
}

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-email@domain.com',
    'email_password': 'your-app-specific-password'
}

# Lead Scoring Weights
SCORING_WEIGHTS = {
    'company_size': 0.3,
    'website_visits': 0.2,
    'email_opens': 0.25,
    'content_downloads': 0.25
}

# Thresholds
THRESHOLDS = {
    'high_potential': 80,
    'medium_potential': 50,
    'low_potential': 30
}

# CRM Integration Settings
CRM_CONFIG = {
    'platform': 'hubspot',  # or 'salesforce'
    'api_key': 'your-api-key',
    'base_url': 'https://api.hubspot.com/crm/v3',
    'timeout': 30
}

# Email Template IDs
EMAIL_TEMPLATES = {
    'welcome': 'template_001',
    'follow_up': 'template_002',
    'nurture': 'template_003',
    'meeting_request': 'template_004'
}

# Logging Configuration
LOGGING_CONFIG = {
    'log_file': 'logs/lead_system.log',
    'level': 'INFO',
    'format': '%(asctime)s:%(levelname)s:%(message)s'
}
