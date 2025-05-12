from datetime import datetime, timedelta
from collections import defaultdict

# === INPUTS ===

user_preferences = {
    "preferStudyTime": ["late morning", "afternoon", "night"],
    "optimalFocusDuration": 120,
    "minimumFocusDuration": 30,
    "breakDuration": 15,
    "revisionFrequency": "2-3 reviews per topic",
}

availability = {
    "12/02/2025": ["09:00-11:00", "14:00-16:00", "20:00-22:00"],
    "14/02/2025": ["10:00-12:00", "14:00-18:00"],
    "15/02/2025": ["08:00-11:00", "14:00-16:00"],
    "17/02/2025": ["10:00-12:00", "14:00-17:00"]
}

courses = [
    {
        "name": "Operating Systems",
        "examDate": "25/02/2025",
        "examTime": "09:00–11:00",
        "topics": [
            {"name": "CPU Scheduling", "difficulty": 3, "understanding": 2, "studyTime": 90},
            {"name": "Deadlocks", "difficulty": 4, "understanding": 3, "studyTime": 75},
            {"name": "Virtual Memory", "difficulty": 5, "understanding": 2, "studyTime": 120}
        ]
    },
    {
        "name": "Data Structures and Algorithms",
        "examDate": "22/02/2025",
        "examTime": "10:00–12:00",
        "topics": [
            {"name": "Trees & Graphs", "difficulty": 3, "understanding": 2, "studyTime": 80},
            {"name": "Sorting Algorithms", "difficulty": 2, "understanding": 4, "studyTime": 50},
            {"name": "Dynamic Programming", "difficulty": 5, "understanding": 2, "studyTime": 110}
        ]
    },
    {
        "name": "Machine Learning",
        "examDate": "23/02/2025",
        "examTime": "13:00–15:00",
        "topics": [
            {"name": "Regression Models", "difficulty": 3, "understanding": 3, "studyTime": 70},
            {"name": "Classification", "difficulty": 4, "understanding": 2, "studyTime": 90},
            {"name": "Neural Networks", "difficulty": 5, "understanding": 2, "studyTime": 130}
        ]
    },
    {
        "name": "Database Systems",
        "examDate": "27/02/2025",
        "examTime": "09:30–11:30",
        "topics": [
            {"name": "SQL Joins", "difficulty": 2, "understanding": 4, "studyTime": 40},
            {"name": "Normalization", "difficulty": 3, "understanding": 3, "studyTime": 60},
            {"name": "Indexing & Query Optimization", "difficulty": 4, "understanding": 2, "studyTime": 90}
        ]
    },
    {
        "name": "Computer Networks",
        "examDate": "25/02/2025",
        "examTime": "14:00–16:00",
        "topics": [
            {"name": "TCP/IP Model", "difficulty": 2, "understanding": 4, "studyTime": 50},
            {"name": "Routing Protocols", "difficulty": 4, "understanding": 2, "studyTime": 100},
            {"name": "Congestion Control", "difficulty": 3, "understanding": 3, "studyTime": 60}
        ]
    }
]

assignments = [
    {
        "course": "Information Retrieval",
        "title": "Midterm Essay",
        "associatedTopic": "Vector Space Model",
        "dueDate": "14/02/2025",
        "estimatedTime": 50 
    },
    {
        "course": "Software Architecture",
        "title": "Final Project",
        "dueDate": "17/02/2025",
        "estimatedTime": 180
    }
]


# === HELPERS ===

def get_preferred_time_periods(pref):
    time_periods = {
            "early morning": (4, 8),
            "late morning": (8, 12),
            "afternoon": (12, 18),
            "evening": (18, 22),
            "night": (22, 24),
            "late night": (0, 4)
        }
    return [time_periods[p] for p in pref if p in time_periods]

def estimate_study_time(difficulty, understanding, base_time=None):
    """
    Estimate adjusted study time based on difficulty and understanding.
    Rounds the result to the nearest 10 minutes.
    """
    if base_time is None:
        base_time = 60  # default if not provided

    adjustment = (difficulty - understanding) * 0.1
    adjusted_time = base_time * (1 + adjustment)

    # Clamp to minimum of 15 minutes, then round to nearest 10
    adjusted_time = max(15, adjusted_time)
    rounded_time = round(adjusted_time / 10) * 10

    return rounded_time

def estimate_sessions(adjusted_study_time, revision_freq):
    """
    Split the estimated study time into sessions based on revision strategy.
    Each session is rounded to the nearest 10 minutes.
    """
    def round10(x):
        return round(x / 10) * 10

    if revision_freq == "single deep review before exam":
        deep_time = round10(adjusted_study_time * 0.8)
        review_time = round10(adjusted_study_time * 0.2)
        return [deep_time, review_time]

    elif revision_freq == "2-3 reviews per topic":
        overview_time = round10(adjusted_study_time * 0.2)
        deep_time = round10(adjusted_study_time * 0.6)
        review_time = round10(adjusted_study_time * 0.2)
        return [overview_time, deep_time, review_time]

    elif revision_freq == "daily review sessions":
        num_sessions = 5
        per_session = round10(adjusted_study_time / num_sessions)
        return [per_session] * num_sessions

    else:
        return [round10(adjusted_study_time)]