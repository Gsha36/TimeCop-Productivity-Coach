from datetime import datetime, timedelta
import random

def fetch_activity(user_id: str):
    """Enhanced GitHub activity simulation with realistic data patterns"""
    base_time = datetime.now() - timedelta(days=7)
    
    activities = []
    repos = ["auth-service", "timecop-backend", "user-dashboard", "api-gateway", "ml-pipeline"]
    actions = [
        {"type": "commit", "weight": 40},
        {"type": "pull_request", "weight": 20},
        {"type": "code_review", "weight": 25},
        {"type": "issue_created", "weight": 10},
        {"type": "merge", "weight": 5}
    ]
    
    # Generate 15-25 activities over the past week
    for i in range(random.randint(15, 25)):
        activity_time = base_time + timedelta(
            days=random.randint(0, 6),
            hours=random.randint(9, 18),
            minutes=random.randint(0, 59)
        )
        
        action = random.choices(
            [a["type"] for a in actions],
            weights=[a["weight"] for a in actions]
        )[0]
        
        activity = {
            "repo": random.choice(repos),
            "action": action,
            "timestamp": activity_time.strftime("%Y-%m-%d %H:%M:%S"),
            "day_of_week": activity_time.strftime("%A"),
            "lines_changed": random.randint(5, 200) if action == "commit" else None,
            "files_modified": random.randint(1, 8) if action == "commit" else None,
            "commit_message": generate_commit_message() if action == "commit" else None
        }
        activities.append(activity)
    
    return sorted(activities, key=lambda x: x["timestamp"])

def generate_commit_message():
    messages = [
        "Fix authentication bug in user login",
        "Add error handling for API endpoints",
        "Update user profile validation",
        "Implement rate limiting middleware",
        "Refactor database connection logic",
        "Add unit tests for payment service",
        "Update documentation for API changes",
        "Fix memory leak in background jobs",
        "Optimize database queries for dashboard",
        "Add logging for debugging purposes"
    ]
    return random.choice(messages)