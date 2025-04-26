from datetime import datetime, timedelta
from collections import defaultdict

# === INPUTS ===

user_preferences = {
    "optimalFocusDuration": "30–45 minutes",
    "breakDuration": 5,
    "userStudyStyle": "multiple_passes",  # "multiple_passes" or "one_pass_deep"
    "preferStudyTime": ["late morning", "afternoon", "night"]  # Study times: "morning", "afternoon", "evening", "night"
}

availability = {
    "12/02/2025": ["09:00-11:00", "14:00-16:00"],
    "14/02/2025": ["10:00-12:00", "14:00-18:00"],
    "15/02/2025": ["08:00-11:00", "14:00-16:00"],
    "17/02/2025": ["10:00-12:00", "14:00-17:00"]
}

courses = [
    {
        "name": "Information Retrieval",
        "topics": [
            {"name": "Vector Space Model", "difficulty": 3, "understanding": 5, "studyTime": 60},
            {"name": "BM25", "difficulty": 4, "understanding": 2, "studyTime": 90}
        ]
    },
    {
        "name": "Software Architecture",
        "topics": [
            {"name": "Introduction", "difficulty": 1, "understanding": 4, "studyTime": 45},
            {"name": "System Architecture", "difficulty": 4, "understanding": 1, "studyTime": 120}
        ]
    }
]

# === HELPERS ===

def get_focus_minutes(pref):
    """Return focus duration in minutes based on user preference."""
    mapping = {
        "~30 minutes": 30,
        "30–45 minutes": 45,
        "1–2 hours": 90,
        "Over 2 hours": 120
    }
    return mapping.get(pref, 30)

focus_minutes = get_focus_minutes(user_preferences["optimalFocusDuration"])

def estimate_sessions(difficulty, understanding, study_time, study_style):
    """Estimate sessions based on study style, difficulty, and understanding."""
    adjustment = (difficulty - understanding) * 0.1
    adjusted_study_time = study_time * (1 + adjustment)

    if study_style == "multiple_passes":
        overview_time = adjusted_study_time * 0.2
        deep_time = adjusted_study_time * 0.6
        review_time = adjusted_study_time * 0.2
        return [overview_time, deep_time, review_time]
    else:  # one_pass_deep
        return [adjusted_study_time]

def generate_time_slots(availability, focus_minutes, break_minutes):
    """Generate all possible time slots within availability."""
    slots = []
    for day, blocks in availability.items():
        for block in blocks:
            start_str, end_str = block.split("-")
            t_start = datetime.strptime(f"{day} {start_str}", "%d/%m/%Y %H:%M")
            t_end = datetime.strptime(f"{day} {end_str}", "%d/%m/%Y %H:%M")
            while t_start + timedelta(minutes=focus_minutes) <= t_end:
                slot_start = t_start.strftime("%d/%m/%Y %H:%M")
                slot_end = (t_start + timedelta(minutes=focus_minutes)).strftime("%d/%m/%Y %H:%M")
                slots.append((slot_start, slot_end))
                t_start += timedelta(minutes=focus_minutes + break_minutes)
    return slots

def minutes_between(start_str, end_str):
    """Calculate minutes between two time strings."""
    fmt = "%d/%m/%Y %H:%M"
    return int((datetime.strptime(end_str, fmt) - datetime.strptime(start_str, fmt)).total_seconds() // 60)

# === CSP VARIABLES ===

variables = []
domain = generate_time_slots(availability, focus_minutes, user_preferences["breakDuration"])

# Define study sessions with session duration
for course in courses:
    for topic in course["topics"]:
        session_times = estimate_sessions(topic["difficulty"], topic["understanding"], topic["studyTime"], user_preferences["userStudyStyle"])
        for idx, session_time in enumerate(session_times, 1):
            session_name = f"{course['name']} - {topic['name']} - S{idx}"
            variables.append((session_name, session_time))  # (name, required minutes)

# === FUNCTIONALITY ===

occupied_slots = set()

def is_within_preferred(slot_start, prefer_study_times):
    """Check if slot_start (datetime string) falls into preferred study times (morning, afternoon, etc.)."""
    time_periods = {
        "early morning": (4, 8),
        "late morning": (8, 12),
        "afternoon": (12, 18),
        "evening": (18, 22),
        "night": (22, 24),
        "late night": (0, 4)
    }

    slot_dt = datetime.strptime(slot_start, "%d/%m/%Y %H:%M")
    hour = slot_dt.hour

    for period in prefer_study_times:
        start_hour, end_hour = time_periods.get(period, (0, 24))
        if start_hour < end_hour:
            if start_hour <= hour < end_hour:
                return True
        else:  # Night case (22:00–02:00 wraps around midnight)
            if hour >= start_hour or hour < end_hour:
                return True
    return False

def assign_time_slot(session_name, required_minutes, is_difficult):
    """Assign time slot, prioritize preferred time if difficult topic."""
    preferred_first = []
    normal_slots = []

    for slot_start, slot_end in domain:
        if (slot_start, slot_end) not in occupied_slots:
            available_minutes = minutes_between(slot_start, slot_end)
            if available_minutes >= required_minutes:
                if is_difficult and is_within_preferred(slot_start, user_preferences["preferStudyTime"]):
                    preferred_first.append((slot_start, slot_end))
                else:
                    normal_slots.append((slot_start, slot_end))

    # Priority 1: Preferred slots (for difficult)
    if preferred_first:
        selected = preferred_first[0]
    # Priority 2: Normal slots
    elif normal_slots:
        selected = normal_slots[0]
    else:
        return None

    occupied_slots.add(selected)
    return selected

def assign_sequentially(assigned_slots):
    """Ensure sessions (S1, S2, S3) are scheduled consecutively for each topic."""
    sorted_sessions = sorted(assigned_slots.items(), key=lambda x: x[1][0])  # Sort by start time

    last_end_time = None
    for idx, (session_name, (start, end)) in enumerate(sorted_sessions):
        if last_end_time:
            # Ensure the next session starts immediately after the previous one
            new_start_time = datetime.strptime(last_end_time, "%d/%m/%Y %H:%M") + timedelta(minutes=1)
            new_end_time = new_start_time + timedelta(minutes=minutes_between(start, end))
            assigned_slots[session_name] = (new_start_time.strftime("%d/%m/%Y %H:%M"), new_end_time.strftime("%d/%m/%Y %H:%M"))
        last_end_time = assigned_slots[session_name][1]  # Update last end time

    return assigned_slots

# === MAIN FUNCTION ===

if __name__ == "__main__":
    study_plan = {}

    # Iterate over each session and assign time slots
    for session_name, required_minutes in variables:
        # Determine if the topic is difficult
        is_difficult = next(topic["difficulty"] >= 3 for course in courses for topic in course["topics"] if session_name.startswith(course["name"]))
        
        # Assign a time slot for the session
        slot = assign_time_slot(session_name, required_minutes, is_difficult)

        if slot:
            study_plan[session_name] = slot
        else:
            print(f"No valid time slot available for {session_name}")


    # Step to ensure sequentiality in session assignments
    if study_plan:
        organized_plan = defaultdict(list)
        for session, (start_time, end_time) in study_plan.items():
            date = start_time.split(" ")[0]
            organized_plan[date].append((start_time, end_time, session))

        for date in sorted(organized_plan.keys()):
            print(f"\n{date}")
            for start, end, session in sorted(organized_plan[date]):
                print(f"  {start.split(' ')[1]} - {end.split(' ')[1]} ➔ {session}")
    else:
        print("No study plan generated.")