from datetime import datetime, timedelta
import random

def fetch_email_metadata(user_id: str):
    """Enhanced Gmail metadata with realistic email patterns"""
    base_time = datetime.now() - timedelta(days=7)
    
    emails = []
    subjects = [
        {"subject": "Weekly Team Sync Notes", "category": "meetings", "priority": "medium"},
        {"subject": "Code Review Request - Auth Service", "category": "work", "priority": "high"},
        {"subject": "Monthly Performance Report", "category": "reports", "priority": "high"},
        {"subject": "Lunch plans for tomorrow?", "category": "personal", "priority": "low"},
        {"subject": "Budget Approval Needed", "category": "admin", "priority": "high"},
        {"subject": "Conference Registration Reminder", "category": "events", "priority": "medium"},
        {"subject": "Project Timeline Update", "category": "work", "priority": "high"},
        {"subject": "Happy Birthday!", "category": "personal", "priority": "low"},
        {"subject": "System Maintenance Scheduled", "category": "notifications", "priority": "medium"},
        {"subject": "Invoice #12345 - Payment Due", "category": "finance", "priority": "high"},
        {"subject": "New Documentation Available", "category": "work", "priority": "low"},
        {"subject": "Meeting Room Booking Confirmed", "category": "logistics", "priority": "low"}
    ]
    
    # Generate 20-35 emails over the past week
    for i in range(random.randint(20, 35)):
        email_time = base_time + timedelta(
            days=random.randint(0, 6),
            hours=random.randint(8, 19),
            minutes=random.randint(0, 59)
        )
        
        email_data = random.choice(subjects)
        
        email = {
            "subject": email_data["subject"],
            "timestamp": email_time.strftime("%Y-%m-%d %H:%M:%S"),
            "day_of_week": email_time.strftime("%A"),
            "category": email_data["category"],
            "priority": email_data["priority"],
            "is_sent": random.choice([True, False]),
            "thread_count": random.randint(1, 5),
            "has_attachments": random.choice([True, False]) if email_data["category"] == "work" else False
        }
        emails.append(email)
    
    return sorted(emails, key=lambda x: x["timestamp"], reverse=True)
