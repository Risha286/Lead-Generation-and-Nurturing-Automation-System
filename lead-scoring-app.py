import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import json
import logging
from pathlib import Path

class LeadScoringSystem:
    def __init__(self, db_path='leads.db'):
        self.db_path = db_path
        self.model = None
        self.scaler = StandardScaler()
        self.setup_logging()
        self.setup_database()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='lead_system.log',
            level=logging.INFO,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                lead_id INTEGER PRIMARY KEY,
                company_name TEXT,
                industry TEXT,
                company_size INTEGER,
                country TEXT,
                website_visits INTEGER,
                email_opens INTEGER,
                content_downloads INTEGER,
                lead_score FLOAT,
                conversion_status INTEGER,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                interaction_id INTEGER PRIMARY KEY,
                lead_id INTEGER,
                interaction_type TEXT,
                interaction_date TIMESTAMP,
                details TEXT,
                FOREIGN KEY (lead_id) REFERENCES leads (lead_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def load_and_preprocess_data(self, data_path):
        """
        Load data from HubSpot dataset
        Dataset source: https://www.kaggle.com/datasets/ashydv/leads-dataset
        """
        self.df = pd.read_csv(data_path)
        logging.info(f"Loaded {len(self.df)} leads from {data_path}")
        return self.df
    
    def calculate_lead_score(self, lead_data):
        """Calculate lead score based on various parameters"""
        weights = {
            'company_size': 0.3,
            'website_visits': 0.2,
            'email_opens': 0.25,
            'content_downloads': 0.25
        }
        
        score = sum(lead_data[feature] * weight 
                   for feature, weight in weights.items())
        return min(100, max(0, score))
    
    def train_model(self, X, y):
        """Train Random Forest model for lead scoring"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        score = self.model.score(X_test, y_test)
        logging.info(f"Model trained with accuracy: {score}")
        return score
    
    def send_automated_email(self, lead_id, email_type):
        """Send automated emails based on lead interactions"""
        with open('email_templates.json', 'r') as f:
            templates = json.load(f)
        
        # Get lead data from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE lead_id = ?", (lead_id,))
        lead_data = cursor.fetchone()
        conn.close()
        
        if lead_data and email_type in templates:
            template = templates[email_type]
            # Personalize email content
            email_content = template['content'].format(
                company_name=lead_data[1]
            )
            
            # Log email sending attempt
            logging.info(f"Sending {email_type} email to lead {lead_id}")
            return self._send_email(lead_data[1], template['subject'], email_content)
    
    def _send_email(self, to_email, subject, content):
        """Helper method to send emails"""
        # Implementation would connect to email service
        # This is a placeholder for demonstration
        logging.info(f"Email would be sent to {to_email}: {subject}")
        return True
    
    def update_lead_status(self, lead_id, interaction_type, details=None):
        """Update lead status and record interaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Record interaction
        cursor.execute('''
            INSERT INTO interactions (lead_id, interaction_type, interaction_date, details)
            VALUES (?, ?, ?, ?)
        ''', (lead_id, interaction_type, datetime.now(), details))
        
        # Update lead score
        cursor.execute("""
            UPDATE leads 
            SET updated_at = ?
            WHERE lead_id = ?
        """, (datetime.now(), lead_id))
        
        conn.commit()
        conn.close()
        logging.info(f"Updated status for lead {lead_id}: {interaction_type}")

    def generate_reports(self):
        """Generate performance reports"""
        conn = sqlite3.connect(self.db_path)
        
        # Basic reporting queries
        reports = {
            'conversion_rate': pd.read_sql_query("""
                SELECT 
                    COUNT(CASE WHEN conversion_status = 1 THEN 1 END) * 100.0 / COUNT(*) as conversion_rate
                FROM leads
                """, conn),
            'leads_by_industry': pd.read_sql_query("""
                SELECT industry, COUNT(*) as count
                FROM leads
                GROUP BY industry
                ORDER BY count DESC
                """, conn),
            'interaction_summary': pd.read_sql_query("""
                SELECT interaction_type, COUNT(*) as count
                FROM interactions
                GROUP BY interaction_type
                ORDER BY count DESC
                """, conn)
        }
        
        conn.close()
        return reports

if __name__ == "__main__":
    # Initialize system
    lead_system = LeadScoringSystem()
    
    # Load and process data
    df = lead_system.load_and_preprocess_data('leads_data.csv')
    
    # Example usage
    lead_system.train_model(
        df[['company_size', 'website_visits', 'email_opens', 'content_downloads']],
        df['conversion_status']
    )
    
    # Generate reports
    reports = lead_system.generate_reports()
    logging.info("System initialization complete")
