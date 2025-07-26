from datetime import datetime, timedelta
import random

def fetch_events(user_id: str):
    """Enhanced Google Calendar with realistic meeting patterns"""
    base_time = datetime.now() - timedelta(days=7)
    
    events = []
    meeting_types = [
        {"summary": "Daily Standup", "duration": 30, "frequency": "daily", "attendees": 8},
        {"summary": "Sprint Planning", "duration": 120, "frequency": "weekly", "attendees": 6},
        {"summary": "Code Review Session", "duration": 60, "frequency": "regular", "attendees": 4},
        {"summary": "Client Demo", "duration": 45, "frequency": "weekly", "attendees": 12},
        {"summary": "One-on-One with Manager", "duration": 30, "frequency": "biweekly", "attendees": 2},
        {"summary": "Architecture Discussion", "duration": 90, "frequency": "regular", "attendees": 5},
        {"summary": "Team Retrospective", "duration": 60, "frequency": "biweekly", "attendees": 8},
        {"summary": "Product Strategy Meeting", "duration": 75, "frequency": "monthly", "attendees": 10},
        {"summary": "Technical Interview", "duration": 60, "frequency": "occasional", "attendees": 3},
        {"summary": "Lunch & Learn Session", "duration": 45, "frequency": "weekly", "attendees": 15}
    ]
    
    focus_blocks = [
        "Deep Work - Feature Development",
        "Focus Time - Bug Fixes",
        "Coding Session - New API",
        "Research & Documentation",
        "Testing & QA Review"
    ]
    
    # Generate meetings (12-18 over the week)
    for i in range(random.randint(12, 18)):
        meeting_time = base_time + timedelta(
            days=random.randint(0, 6),
            hours=random.randint(9, 17),
            minutes=random.choice([0, 15, 30, 45])
        )
        
        meeting = random.choice(meeting_types)
        end_time = meeting_time + timedelta(minutes=meeting["duration"])
        
        event = {
            "summary": meeting["summary"],
            "start": meeting_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": meeting["duration"],
            "attendees_count": meeting["attendees"],
            "event_type": "meeting",
            "day_of_week": meeting_time.strftime("%A"),
            "is_recurring": meeting["frequency"] in ["daily", "weekly", "biweekly"]
        }
        events.append(event)
    
    # Generate focus blocks (8-12 over the week)
    for i in range(random.randint(8, 12)):
        focus_time = base_time + timedelta(
            days=random.randint(0, 6),
            hours=random.randint(9, 17),
            minutes=0
        )
        
        duration = random.choice([60, 90, 120, 180])  # 1-3 hour blocks
        end_time = focus_time + timedelta(minutes=duration)
        
        event = {
            "summary": random.choice(focus_blocks),
            "start": focus_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": duration,
            "attendees_count": 1,
            "event_type": "focus_block",
            "day_of_week": focus_time.strftime("%A"),
            "is_recurring": False
        }
        events.append(event)
    
    return sorted(events, key=lambda x: x["start"])