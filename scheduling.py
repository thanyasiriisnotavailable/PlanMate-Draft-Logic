def get_preferred_time_ranges(pref_strings):
    time_periods_map = {
        "early morning": (4, 8), "late morning": (8, 12), "afternoon": (12, 18),
        "evening": (18, 22), "night": (22, 24), "late night": (0, 4)
    }
    return [time_periods_map[p] for p in pref_strings if p in time_periods_map]

def get_session_types_for_freq(revision_freq):
    """
    Maps revision frequency to a list of session types.
    Ensures we avoid division by zero in session generation.
    """
    mapping = {
        "single deep review before exam": ["deep", "review"],
        "2-3 reviews per topic": ["overview", "deep", "review"],
        "daily review sessions": ["deep"] * 5 + ["review"],
    }
    return mapping.get(revision_freq, ["deep", "review"])  # default fallback


from datetime import datetime, timedelta

def parse_timeblock(tblock_str):
    start_str, end_str = tblock_str.split("-")
    return (datetime.strptime(start_str.strip(), "%H:%M"),
            datetime.strptime(end_str.strip(), "%H:%M"))

def timeblock_duration(start, end):
    return int((end - start).total_seconds() / 60)

def format_time(dt):
    return dt.strftime("%H:%M")

def split_timeblock(start, duration):
    """Returns (block_start, block_end) after consuming `duration`."""
    end = start + timedelta(minutes=duration)
    return (start, end)

def build_all_sessions(courses, assignments, prefs):
    session_list = []
    
    for course in courses:
        for topic in course["topics"]:
            base = topic["studyTime"]
            adjusted = estimate_study_time(topic["difficulty"], topic["confidence"], base)
            session_durations = estimate_sessions(adjusted, prefs["revisionFrequency"], prefs["preferredSessionDuration"])
            types = get_session_types_for_freq(prefs["revisionFrequency"])
            for i, duration in enumerate(session_durations):
                session_list.append({
                    "course": course["name"],
                    "topic": topic["title"],
                    "type": types[i % len(types)],
                    "duration": duration,
                    "due": datetime.strptime(course["examDate"], "%d/%m/%Y"),
                    "priority": 0 if types[i % len(types)] == "review" else 1  # reviews go last
                })

    for assign in assignments:
        sessions = create_assignment_sessions(assign["estimatedTime"], prefs["preferredSessionDuration"])
        for duration in sessions:
            session_list.append({
                "course": assign["course"],
                "topic": ", ".join(assign.get("associatedTopic", assign.get("assiociatedTopic", []))),
                "type": "assignment",
                "duration": duration,
                "due": datetime.strptime(assign["dueDate"], "%d/%m/%Y"),
                "priority": 1
            })
    
    # Sort by due date, then course name, then topic
    return sorted(session_list, key=lambda s: (s["due"], s["course"], s["topic"], s["priority"]))


def schedule_sessions(session_list, availability, prefs):
    scheduled = []
    break_min = prefs["breakDuration"]
    
    for session in session_list:
        scheduled_flag = False
        for date_str in sorted(availability.keys()):
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            if date_obj > session["due"]:
                continue  # Skip dates after due

            for i, block in enumerate(availability[date_str]):
                start, end = parse_timeblock(block)
                duration = timeblock_duration(start, end)
                if duration >= session["duration"]:
                    # Schedule session
                    sess_start, sess_end = split_timeblock(start, session["duration"])
                    break_end = sess_end + timedelta(minutes=break_min)
                    scheduled.append({
                        "date": date_str,
                        "start": format_time(sess_start),
                        "end": format_time(sess_end),
                        "course": session["course"],
                        "topic": session["topic"],
                        "type": session["type"]
                    })

                    # Update block to remaining time
                    if break_end < end:
                        availability[date_str][i] = f"{format_time(break_end)}-{format_time(end)}"
                    else:
                        availability[date_str].pop(i)
                    scheduled_flag = True
                    break
            if scheduled_flag:
                break
    return scheduled


