import math
from input import courses, assignments, user_preferences

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
        overview = round10(adjusted_study_time * 0.1)
        deep = round10(adjusted_study_time)
        review = round10(adjusted_study_time * 0.2)
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

def build_study_sessions(courses, user_preferences):
    sessions = []

    for course in courses:
        for topic in course["topics"]:
            base_time = topic.get("studyTime", 60)
            adjusted_time = estimate_study_time(
                topic["difficulty"],
                topic["confidence"],
                base_time
            )
            durations = estimate_sessions(
                adjusted_time,
                user_preferences["revisionFrequency"],
                user_preferences["preferredSessionDuration"]
            )

            for i, dur in enumerate(durations):
                session_type = "review" if i == len(durations) - 1 else "study"
                sessions.append({
                    "course": course["name"],
                    "topic": topic["title"],
                    "duration": dur,
                    "type": session_type,
                    "examDate": course["examDate"]
                })

    return sessions


def build_assignment_sessions(assignments, user_preferences):
    sessions = []

    for assignment in assignments:
        durations = create_assignment_sessions(
            assignment["estimatedTime"],
            user_preferences["preferredSessionDuration"]
        )

        for dur in durations:
            sessions.append({
                "course": assignment["course"],
                "title": assignment["title"],
                "duration": dur,
                "type": "assignment"
            })

    return sessions

if __name__ == "__main__":
    # Build session data
    study_sessions = build_study_sessions(courses, user_preferences)
    assignment_sessions = build_assignment_sessions(assignments, user_preferences)

    # Print study sessions
    print("📚 Study Sessions for Courses:")

    # Group by course → topic → sessions
    from collections import defaultdict

    course_topic_sessions = defaultdict(lambda: defaultdict(list))
    for s in study_sessions:
        course_topic_sessions[s["course"]][s["topic"]].append(s)

    for course_name, topics in course_topic_sessions.items():
        print(f"\n📘 Course: {course_name}")
        for topic, sessions in topics.items():
            total = sum(s["duration"] for s in sessions)
            session_info = ", ".join(f"{s['duration']} min" for s in sessions)
            print(f"  • {topic} → Total Adjusted: {total} min → Sessions: {session_info}")

    # Print assignment sessions
    print("\n" + "=" * 30 + "\n")
    print("📝 Assignment Sessions:")

    grouped_assignments = {}
    for s in assignment_sessions:
        key = (s["course"], s["title"])
        grouped_assignments.setdefault(key, []).append(s)

    for (course_name, title), sessions in grouped_assignments.items():
        total = sum(s["duration"] for s in sessions)
        session_info = ", ".join(f"{s['duration']} min" for s in sessions)
        print(f"\n📌 Assignment: {title} ({course_name})")
        print(f"  • Estimated Time: {total} min → Sessions: {session_info}")
