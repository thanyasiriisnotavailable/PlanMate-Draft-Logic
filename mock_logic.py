from datetime import datetime, timedelta
from collections import defaultdict

# === INPUTS ===

user_preferences = {
    "optimalFocusDuration": "30–45 minutes",
    "breakDuration": 15,
    "userStudyStyle": "multiple_passes",  # "multiple_passes" or "one_pass_deep"
    "preferStudyTime": ["late morning", "afternoon", "night"]
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
            {"name": "Introduction", "difficulty": 1, "understanding": 5, "studyTime": 30},
            {"name": "System Architecture", "difficulty": 4, "understanding": 1, "studyTime": 120}
        ]
    }
]

# === HELPERS ===

def get_focus_minutes(pref):
    mapping = {
        "~30 minutes": 30,
        "30–45 minutes": 45,
        "1–2 hours": 90,
        "Over 2 hours": 120
    }
    return mapping.get(pref, 30)

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

def minutes_between(start_str, end_str):
    fmt = "%d/%m/%Y %H:%M"
    return int((datetime.strptime(end_str, fmt) - datetime.strptime(start_str, fmt)).total_seconds() // 60)

# === RULE-BASED SYSTEM ===

def apply_rule_based_adjustments(courses, user_preferences):
    adjusted_sessions = []
    focus_minutes = get_focus_minutes(user_preferences["optimalFocusDuration"])

    for course in courses:
        for topic in course["topics"]:
            difficulty = topic["difficulty"]
            understanding = topic["understanding"]
            base_time = topic["studyTime"]

            # Rule 1: More sessions if difficulty gap is high
            if difficulty - understanding >= 2:
                number_of_sessions = 3
            elif difficulty >= 3:
                number_of_sessions = 2
            else:
                number_of_sessions = 1

            # Rule 2: Study style (multiple passes), only if base_time is big enough
            if user_preferences["userStudyStyle"] == "multiple_passes" and base_time >= focus_minutes:
                session_length = min(base_time / number_of_sessions, focus_minutes)
                overview = session_length * 0.2
                deep = session_length * 0.6
                review = session_length * 0.2
                session_durations = [overview, deep, review]
            else:
                # If study time is small, just make 1 session
                session_length = min(base_time, focus_minutes)
                session_durations = [session_length]

            # Create sessions
            for idx, duration in enumerate(session_durations, 1):
                session_name = f"{course['name']} - {topic['name']} - S{idx}"
                adjusted_sessions.append((session_name, duration, difficulty))
    
    return adjusted_sessions

# === TIME SLOT GENERATION ===

def generate_time_slots(availability, focus_minutes, break_minutes):
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

def is_within_preferred(slot_start, prefer_study_times):
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
        if start_hour <= hour < end_hour or (start_hour > end_hour and (hour >= start_hour or hour < end_hour)):
            return True
    return False

# === CSP ASSIGNMENT ===

occupied_slots = set()

def assign_time_slot(session_name, required_minutes, difficulty, domain, user_preferences):
    preferred_slots = []
    normal_slots = []

    for slot_start, slot_end in domain:
        if (slot_start, slot_end) not in occupied_slots:
            available_minutes = minutes_between(slot_start, slot_end)
            if available_minutes >= required_minutes:
                if difficulty >= 3 and is_within_preferred(slot_start, user_preferences["preferStudyTime"]):
                    preferred_slots.append((slot_start, slot_end))
                else:
                    normal_slots.append((slot_start, slot_end))

    if preferred_slots:
        selected = preferred_slots[0]
    elif normal_slots:
        selected = normal_slots[0]
    else:
        return None

    occupied_slots.add(selected)
    return selected

def prepare_sessions(courses, user_preferences):
    """Prepare sessions grouped by course, sorted by topic difficulty."""
    sessions_by_course = defaultdict(list)

    for course in courses:
        # Sort topics inside the course by difficulty (easy ➔ hard)
        sorted_topics = sorted(course["topics"], key=lambda x: x["difficulty"])
        for topic in sorted_topics:
            # Estimate sessions for each topic
            session_times = estimate_sessions(topic["difficulty"], topic["understanding"], topic["studyTime"], user_preferences["userStudyStyle"])
            for idx, session_time in enumerate(session_times, 1):
                session_name = f"{course['name']} - {topic['name']} - S{idx}"
                sessions_by_course[course["name"]].append((session_name, session_time, topic["difficulty"]))  # We keep difficulty too
    return sessions_by_course


# === MAIN FUNCTION ===

if __name__ == "__main__":
    # Phase 1: Apply Rule-Based adjustments
    adjusted_sessions = apply_rule_based_adjustments(courses, user_preferences)

    # Phase 2: CSP setup
    focus_minutes = get_focus_minutes(user_preferences["optimalFocusDuration"])
    domain = generate_time_slots(availability, focus_minutes, user_preferences["breakDuration"])

    study_plan = {}

    # Phase 3: Assign sessions
    for session_name, required_minutes, difficulty in adjusted_sessions:
        slot = assign_time_slot(session_name, required_minutes, difficulty, domain, user_preferences)
        if slot:
            study_plan[session_name] = slot
        else:
            print(f"No valid time slot available for {session_name}")

    # Phase 4: Organize and print study plan
    if study_plan:
        organized_plan = defaultdict(list)
        for session, (start_time, end_time) in study_plan.items():
            date = start_time.split(" ")[0]
            organized_plan[date].append((start_time, end_time, session))

        print("Study Plan:")
        for date in sorted(organized_plan.keys()):
            print(f"\n{date}")
            for start, end, session in sorted(organized_plan[date]):
                print(f"  {start.split(' ')[1]} - {end.split(' ')[1]} ➔ {session}")
    else:
        print("No study plan generated.")