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

def estimate_study_time(difficulty, confidence, base_time=None):
    """
    Estimate adjusted study time based on difficulty and confidencial.
    Rounds the result to the nearest 10 minutes.
    """
    if base_time is None:
        base_time = 60  # default if not provided

    adjustment = (difficulty - confidence) * 0.1
    adjusted_time = base_time * (1 + adjustment)

    # Clamp to minimum of 15 minutes, then round to nearest 10
    adjusted_time = max(15, adjusted_time)
    rounded_time = round(adjusted_time / 10) * 10

    return rounded_time

def estimate_sessions(adjusted_study_time, revision_freq, preferred_study_duration):
    """
    Break adjusted study time into sessions based on revision strategy.
    Enforce preferred session duration by splitting oversized chunks.
    All durations are rounded UP to the nearest 10 minutes.
    """
    def round10(x):
        return math.ceil(x / 10) * 10

    min_dur = preferred_study_duration["min"]
    max_dur = preferred_study_duration["max"]

    sessions = []

    if revision_freq == "single deep review before exam":
        deep = round10(adjusted_study_time)
        review = round10(adjusted_study_time * 0.2)
        sessions = [deep, review]

    elif revision_freq == "2-3 reviews per topic":
        overview = round10(adjusted_study_time * 0.2)
        deep = round10(adjusted_study_time)
        review = round10(adjusted_study_time * 0.3)
        sessions = [overview, deep, review]

    elif revision_freq == "daily review sessions":
        review = round10(adjusted_study_time * 0.25)
        core_time = adjusted_study_time

        # 🗓️ Target up to 5 daily sessions (or as many fit given min_dur)
        num_daily = min(5, max(1, core_time // min_dur))

        base = core_time // num_daily
        remainder = core_time % num_daily

        sessions = []
        for i in range(num_daily):
            session_length = base + (1 if i < remainder else 0)
            sessions.append(round10(session_length))

        sessions.append(review)

    else: # Default fallback if revision_freq is not recognized
        core = round10(adjusted_study_time)
        review = round10(adjusted_study_time * 0.2) # Default to a simple core + review
        sessions = [core, review]


    # 💡 Enforce preferred max duration (split if too long)
    final_sessions = []
    for s in sessions:
        if s > max_dur:
            parts = math.ceil(s / max_dur)
            per_part = round10(s / parts)
            final_sessions.extend([per_part] * parts)
        elif s < min_dur and s > 0: # Ensure session is not too short, unless it's 0
            final_sessions.append(min_dur) # Or round10(s) if very short sessions are acceptable
        elif s >= min_dur:
            final_sessions.append(s)
        # if s is 0, it will be ignored

    return final_sessions

def create_assignment_sessions(estimated_time, preferred_study_duration):
    """
    Transforms an assignment's estimated time into study sessions,
    respecting the preferred maximum session duration.
    All durations are rounded UP to the nearest 10 minutes.
    """
    def round10(x):
        return math.ceil(x / 10) * 10

    min_dur = preferred_study_duration["min"]
    max_dur = preferred_study_duration["max"]
    
    assignment_sessions = []
    
    if estimated_time == 0:
        return []

    if estimated_time > max_dur:
        parts = math.ceil(estimated_time / max_dur)
        per_part = round10(estimated_time / parts)
        assignment_sessions.extend([per_part] * parts)
    else:
        assignment_sessions.append(round10(estimated_time))
        
    # Ensure no session is too short if it got split that way,
    # although with round10(estimated_time / parts) it's less likely
    # to be below min_dur unless estimated_time is very close to max_dur
    # or parts is large.
    final_assignment_sessions = []
    for s_val in assignment_sessions:
        if s_val < min_dur and s_val > 0 : # if a session ends up less than min_dur, bump to min_dur
            final_assignment_sessions.append(min_dur)
        else:
            final_assignment_sessions.append(s_val)

    return final_assignment_sessions

if __name__ == "__main__":
    print("📚 Study Sessions for Courses:")
    for course in courses:
        print(f"\n📘 Course: {course['name']}")
        for topic in course["topics"]:
            base_time = topic.get("studyTime", 60)
            adjusted_time = estimate_study_time(topic["difficulty"], topic["confidence"], base_time)
            sessions = estimate_sessions(adjusted_time, user_preferences["revisionFrequency"], user_preferences["preferredSessionDuration"])
            session_info = ", ".join([f"{int(s)} min" for s in sessions if s > 0])
            if session_info: # only print if there are sessions
                print(f"  • {topic['title']} → Total Adjusted: {adjusted_time} min → Sessions: {session_info}")
            else:
                print(f"  • {topic['title']} → Total Adjusted: {adjusted_time} min → No sessions generated (check duration/logic)")
    print("\n" + "="*30 + "\n")
    print("📝 Assignment Sessions:")
    for assignment in assignments:
        print(f"\n📌 Assignment: {assignment['title']} ({assignment['course']})")
        estimated_time = assignment["estimatedTime"]
        sessions = create_assignment_sessions(estimated_time, user_preferences["preferredSessionDuration"])
        session_info = ", ".join([f"{int(s)} min" for s in sessions if s > 0])
        if session_info: # only print if there are sessions
            print(f"  • Estimated Time: {estimated_time} min → Sessions: {session_info}")
        else:
            print(f"  • Estimated Time: {estimated_time} min → No sessions generated (check duration/logic)")