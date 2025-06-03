# === INPUTS ===

import math


user_preferences = {
  "preferredStudyTimes": ["late morning", "afternoon", "night"],
  "preferredSessionDuration": {
    "min": 30,
    "max": 90
  },
  "revisionFrequency": "2-3 reviews per topic",
  "breakDuration": 15
}

availability = {
    "12/02/2025": ["09:00-11:00", "14:00-16:00", "20:00-22:00"],
    "14/02/2025": ["10:00-12:00", "14:00-18:00", "20:00-22:00"],
    "15/02/2025": ["08:00-11:00", "14:00-16:00", "20:00-22:00"],
    "17/02/2025": ["10:00-12:00", "14:00-17:00", "20:00-22:00"]
}

courses = [
    {
        "name": "Operating Systems",
        "credit": 3,
        "examDate": "25/02/2025",
        "examTime": "09:00–11:00",
        "topics": [
            {"title": "CPU Scheduling", "difficulty": 3, "confidence": 2, "studyTime": 90},
            {"title": "Deadlocks", "difficulty": 4, "confidence": 3, "studyTime": 75},
            {"title": "Virtual Memory", "difficulty": 5, "confidence": 2, "studyTime": 120}
        ]
    },
    {
        "name": "Data Structures and Algorithms",
        "credit": 3,
        "examDate": "22/02/2025",
        "examTime": "10:00–12:00",
        "topics": [
            {"title": "Trees & Graphs", "difficulty": 3, "confidence": 2, "studyTime": 80},
            {"title": "Sorting Algorithms", "difficulty": 2, "confidence": 4, "studyTime": 50},
            {"title": "Dynamic Programming", "difficulty": 5, "confidence": 2, "studyTime": 110}
        ]
    },
    {
        "name": "Machine Learning",
        "credit": 3,
        "examDate": "23/02/2025",
        "examTime": "13:00–15:00",
        "topics": [
            {"title": "Regression Models", "difficulty": 3, "confidence": 3, "studyTime": 70},
            {"title": "Classification", "difficulty": 4, "confidence": 2, "studyTime": 90},
            {"title": "Neural Networks", "difficulty": 5, "confidence": 2, "studyTime": 130}
        ]
    },
    {
        "name": "Database Systems",
        "credit": 2,
        "examDate": "27/02/2025",
        "examTime": "09:30–11:30",
        "topics": [
            {"title": "SQL Joins", "difficulty": 2, "confidence": 4, "studyTime": 40},
            {"title": "Normalization", "difficulty": 3, "confidence": 3, "studyTime": 60},
            {"title": "Indexing & Query Optimization", "difficulty": 4, "confidence": 2, "studyTime": 90}
        ]
    },
    {
        "name": "Computer Networks",
        "credit": 2,
        "examDate": "25/02/2025",
        "examTime": "14:00–16:00",
        "topics": [
            {"title": "TCP/IP Model", "difficulty": 2, "confidence": 4, "studyTime": 50},
            {"title": "Routing Protocols", "difficulty": 4, "confidence": 2, "studyTime": 100},
            {"title": "Congestion Control", "difficulty": 3, "confidence": 3, "studyTime": 60}
        ]
    }
]

assignments = [
    {
        "course": "Computer Networks",
        "title": "Midterm Essay",
        "associatedTopic": ["TCP/IP Model"],
        "dueDate": "14/02/2025",
        "time": "15.00",
        "estimatedTime": 50 
    },
    {
        "course": "Machine Learning",
        "title": "Final Project",
        "assiociatedTopic": ["Regression Models", "Classification", "Neural Networks"],
        "dueDate": "10/03/2025",
        "estimatedTime": 180
    }
]

# --- Helper Functions ---
def round10(x):
    return round(x / 10) * 10

def get_preferred_time_ranges(pref_strings):
    time_periods_map = {
        "early morning": (4, 8), "late morning": (8, 12), "afternoon": (12, 18),
        "evening": (18, 22), "night": (22, 24), "late night": (0, 4)
    }
    return [time_periods_map[p] for p in pref_strings if p in time_periods_map]

def get_session_types_for_freq(revision_freq):
    if revision_freq == "single deep review before exam":
        return ["deep", "review"]
    elif revision_freq == "2-3 reviews per topic":
        return ["overview", "deep", "review"]
    elif revision_freq == "daily review sessions": # Simplified for this context
        return ["daily_1", "daily_2", "review"] # Assume 2 daily + 1 review
    else:
        return ["core", "review"]
    
def estimate_study_time(difficulty, confidence, base_time=60):
    adjustment = (difficulty - confidence) * 0.1
    adjusted_time = base_time * (1 + adjustment)
    adjusted_time = max(15, adjusted_time)
    return round10(adjusted_time)
    
def estimate_topic_sessions(adjusted_study_time, revision_freq, preferred_study_duration):
    min_dur, max_dur = preferred_study_duration["min"], preferred_study_duration["max"]
    sessions_temp = []
    if revision_freq == "single deep review before exam":
        deep = round10(adjusted_study_time)
        review = round10(adjusted_study_time * 0.2)
        sessions_temp = [deep, review]
    elif revision_freq == "2-3 reviews per topic":
        overview = round10(adjusted_study_time * 0.2)
        deep = round10(adjusted_study_time)
        review = round10(adjusted_study_time * 0.3)
        sessions_temp = [overview, deep, review]
    elif revision_freq == "daily review sessions":
        # Simplified: assume 3 sessions if daily, one main, two smaller reviews
        core_time = adjusted_study_time
        r_time = round10(core_time * 0.25)
        main_time = core_time - r_time # this is rough, needs better distribution
        sessions_temp = [round10(main_time/2), round10(main_time/2), r_time] if main_time > 0 else [r_time]

    else: # Default
        core = round10(adjusted_study_time)
        review = round10(adjusted_study_time * 0.2)
        sessions_temp = [core, review]
    
    final_sessions = []
    for s in sessions_temp:
        if s == 0: continue
        if s > max_dur:
            parts = math.ceil(s / max_dur)
            per_part = round10(s / parts)
            final_sessions.extend([per_part] * parts)
        elif s < min_dur:
             final_sessions.append(min_dur) # ensure min duration
        else:
            final_sessions.append(s)
    return [s for s in final_sessions if s > 0]

def create_assignment_sessions(estimated_time, preferred_study_duration):
    # min_dur from preferred_study_duration is NOT used for assignments.
    max_dur = preferred_study_duration["max"]

    if estimated_time <= 0: # Handles 0 and any potential negative input
        return []

    # Case 1: Estimated time is small enough for a single session (<= max_dur)
    if estimated_time <= max_dur:
        session_duration = round10(estimated_time)
        # round10(positive_small_number) will be at least 10.
        # We expect estimated_time > 0 here due to the check above.
        return [session_duration]

    # Case 2: Estimated time is greater than max_dur, requires splitting
    else:
        num_parts = math.ceil(estimated_time / float(max_dur)) # Number of sessions
        
        # Calculate what each part would be if total time was distributed, then round it.
        # This initial rounding might make the sum of parts larger than estimated_time.
        per_part_ideal_rounded = round10(estimated_time / num_parts)
        
        sessions = [per_part_ideal_rounded] * int(num_parts)

        # Adjust sum if rounding per_part_ideal_rounded up made the total too high
        current_sum = sum(sessions)
        if current_sum > estimated_time and len(sessions) > 0:
            difference_to_cut = current_sum - estimated_time
            
            # Value of the last session before its own final rounding
            last_session_unrounded_adjusted_value = sessions[-1] - difference_to_cut
            
            if last_session_unrounded_adjusted_value > 0:
                sessions[-1] = round10(last_session_unrounded_adjusted_value)
            else:
                # If reducing the last session makes its unrounded value non-positive,
                # it means the other sessions (due to their own rounding up)
                # already cover or exceed the estimated_time.
                # Mark this last session as 0 to be filtered out.
                sessions[-1] = 0
        
        # Filter out any zero-duration sessions that might have resulted from the adjustment
        final_sessions = [s_duration for s_duration in sessions if s_duration > 0]
        
        return final_sessions
    
if __name__ == "__main__":
    print("--- Topic Sessions ---")
    for course in courses:
        print(f"\n📘 Course: {course['name']}")
        for topic in course["topics"]:
            base_time = topic.get("studyTime", 60) # Default to 60 if studyTime not present
            adjusted_time = estimate_study_time(topic["difficulty"], topic["confidence"], base_time)
            # Using the 'estimate_topic_sessions' function as it's designed for topics
            sessions = estimate_topic_sessions(adjusted_time, user_preferences["revisionFrequency"], user_preferences["preferredSessionDuration"])
            session_info = ", ".join([f"{int(s)} min" for s in sessions])
            print(f"  • {topic['title']} → Total Adjusted: {adjusted_time} min → Sessions: {session_info}")

    print("\n\n--- Assignment Sessions ---") # Added extra newline for separation
    for assignment in assignments:
        print(f"\n🛠️ Assignment: {assignment['title']} (Course: {assignment.get('course', 'N/A')})")
        estimated_time = assignment["estimatedTime"]
        assignment_sessions_durations = create_assignment_sessions(estimated_time, user_preferences["preferredSessionDuration"])
        session_info = ", ".join([f"{int(s)} min" for s in assignment_sessions_durations])
        print(f"  • Total Estimated: {estimated_time} min → Sessions: {session_info}")