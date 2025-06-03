from datetime import datetime, timedelta

def str_to_time(s):
    return datetime.strptime(s, "%H:%M")

def time_to_str(t):
    return t.strftime("%H:%M")

def can_fit_session(available_start, available_end, duration):
    return (available_end - available_start).total_seconds() / 60 >= duration

def schedule_review_sessions(sessions, slots):
    reserved = []

    for session in sessions:
        if session["type"] != "review":
            continue

        exam_date = datetime.strptime(session["examDate"], "%d/%m/%Y")
        review_date = (exam_date - timedelta(days=1)).strftime("%d/%m/%Y")

        # Find slots for the review date
        candidate_slots = [
            s for s in slots
            if s["date"] == review_date and can_fit_session(s["available_start"], s["available_end"], session["duration"])
        ]

        if not candidate_slots:
            print(f"⚠️ No slot for review: {session['course']} - {session['topic']}")
            continue

        # Pick earliest fitting slot
        candidate_slots.sort(key=lambda s: s["available_start"])
        best = candidate_slots[0]

        session_start = best["available_start"]
        session_end = session_start + timedelta(minutes=session["duration"])

        session["date"] = best["date"]
        session["start"] = time_to_str(session_start)
        session["end"] = time_to_str(session_end)
        session["slot_id"] = best["id"]

        best["available_start"] = session_end  # Update what's left
        reserved.append(session)

    return reserved

def schedule_related_topic_sessions(assignments, study_sessions, slots):
    scheduled = []

    for assignment in assignments:
        due_date = datetime.strptime(assignment["dueDate"], "%d/%m/%Y")
        related_topics = assignment.get("associatedTopic", [])

        for topic in related_topics:
            topic_sessions = [
                s for s in study_sessions
                if s["type"] == "study" and s["topic"] == topic and s["course"] == assignment["course"]
                and "slot_id" not in s
            ]

            for session in topic_sessions:
                valid_slots = [
                    slot for slot in slots
                    if datetime.strptime(slot["date"], "%d/%m/%Y") < due_date and
                    can_fit_session(slot["available_start"], slot["available_end"], session["duration"])
                ]

                if not valid_slots:
                    print(f"⚠️ No slot for topic '{topic}' of assignment '{assignment['title']}'")
                    continue

                valid_slots.sort(key=lambda s: s["available_start"])
                chosen = valid_slots[0]

                session_start = chosen["available_start"]
                session_end = session_start + timedelta(minutes=session["duration"])

                session["date"] = chosen["date"]
                session["start"] = time_to_str(session_start)
                session["end"] = time_to_str(session_end)
                session["slot_id"] = chosen["id"]

                chosen["available_start"] = session_end
                scheduled.append(session)

    return scheduled

def schedule_assignment_sessions(assignments, assignment_sessions, slots):
    scheduled = []

    for assignment in assignments:
        due_date = datetime.strptime(assignment["dueDate"], "%d/%m/%Y")

        sessions = [
            s for s in assignment_sessions
            if s["course"] == assignment["course"] and s["title"] == assignment["title"]
            and "slot_id" not in s
        ]

        for session in sessions:
            valid_slots = [
                slot for slot in slots
                if datetime.strptime(slot["date"], "%d/%m/%Y") <= due_date and
                can_fit_session(slot["available_start"], slot["available_end"], session["duration"])
            ]

            if not valid_slots:
                print(f"⚠️ No slot for assignment '{assignment['title']}' ({assignment['course']})")
                continue

            valid_slots.sort(key=lambda s: s["available_start"])
            chosen = valid_slots[0]

            session_start = chosen["available_start"]
            session_end = session_start + timedelta(minutes=session["duration"])

            session["date"] = chosen["date"]
            session["start"] = time_to_str(session_start)
            session["end"] = time_to_str(session_end)
            session["slot_id"] = chosen["id"]

            chosen["available_start"] = session_end
            scheduled.append(session)

    return scheduled
