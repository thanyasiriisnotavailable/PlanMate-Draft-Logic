from datetime import datetime, timedelta
import availability_parser, session_generator

def str_to_time(s):
    return datetime.strptime(s, "%H:%M")

def time_to_str(t):
    return t.strftime("%H:%M")

def can_fit_session(available_start, available_end, duration):
    return (available_end - available_start).total_seconds() / 60 >= duration

def schedule_review_sessions(sessions, slots, break_duration):
    reserved = []

    for session in sessions:
        if session["type"] != "review":
            continue

        exam_date = datetime.strptime(session["examDate"], "%d/%m/%Y")
        review_date = (exam_date - timedelta(days=1)).strftime("%d/%m/%Y")

        candidate_slots = [
            s for s in slots
            if s["date"] == review_date and can_fit_session(s["available_start"], s["available_end"], session["duration"])
        ]

        if not candidate_slots:
            print(f"⚠️ No slot for review: {session['course']} - {session['topic']}")
            continue

        candidate_slots.sort(key=lambda s: s["available_start"])
        best = candidate_slots[0]

        session_start = best["available_start"]
        session_end = session_start + timedelta(minutes=session["duration"])

        session["date"] = best["date"]
        session["start"] = time_to_str(session_start)
        session["end"] = time_to_str(session_end)
        session["slot_id"] = best["id"]

        best["available_start"] = session_end + timedelta(minutes=break_duration)
        reserved.append(session)

    return reserved

def schedule_related_topic_sessions(assignments, study_sessions, slots, break_duration):
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

                chosen["available_start"] = session_end + timedelta(minutes=break_duration)
                scheduled.append(session)

    return scheduled

def schedule_assignment_sessions(assignments, assignment_sessions, slots, break_duration):
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

            chosen["available_start"] = session_end + timedelta(minutes=break_duration)
            scheduled.append(session)

    return scheduled

def schedule_remaining_sessions(all_sessions, slots, break_duration):
    scheduled = []
    unscheduled = []

    for session in all_sessions:
        if "slot_id" in session:  # Already scheduled elsewhere
            continue

        candidate_slots = [
            s for s in slots
            if can_fit_session(s["available_start"], s["available_end"], session["duration"])
        ]

        if not candidate_slots:
            unscheduled.append(session)
            continue

        candidate_slots.sort(key=lambda s: (s["date"], s["available_start"]))
        best = candidate_slots[0]

        session_start = best["available_start"]
        session_end = session_start + timedelta(minutes=session["duration"])

        session["date"] = best["date"]
        session["start"] = time_to_str(session_start)
        session["end"] = time_to_str(session_end)
        session["slot_id"] = best["id"]

        best["available_start"] = session_end + timedelta(minutes=break_duration)
        scheduled.append(session)

    return scheduled, unscheduled

def build_final_timetable(courses, assignments, availability, user_preferences):
    # Step 1: Build sessions
    study_sessions = session_generator.build_study_sessions(courses, user_preferences)
    assignment_sessions = session_generator.build_assignment_sessions(assignments, user_preferences)

    # Step 2: Generate and enhance slots
    slots = availability_parser.generate_slots(availability, user_preferences)
    for slot in slots:
        slot["available_start"] = str_to_time(slot["start"])
        slot["available_end"] = str_to_time(slot["end"])

    # Step 3: Schedule sessions
    reserved_reviews = schedule_review_sessions(study_sessions, slots, user_preferences["breakDuration"])
    scheduled_related = schedule_related_topic_sessions(assignments, study_sessions, slots, user_preferences["breakDuration"])
    scheduled_assignments = schedule_assignment_sessions(assignments, assignment_sessions, slots, user_preferences["breakDuration"])

    # Step 4: Schedule any remaining sessions
    all_remaining_sessions = [s for s in (study_sessions + assignment_sessions) if "slot_id" not in s]
    scheduled_remaining, unscheduled = schedule_remaining_sessions(all_remaining_sessions, slots, user_preferences["breakDuration"])


    # Step 5: Create the final unified study plan
    study_plan = reserved_reviews + scheduled_related + scheduled_assignments + scheduled_remaining
    study_plan.sort(key=lambda s: (s["date"], s["start"]))

    return {
        "study_plan": study_plan,
        "unscheduled": unscheduled
    }

def print_schedule_results(reserved_reviews, scheduled_related, scheduled_assignments):
    def print_session_list(header, sessions, item_format, warning):
        print(f"\n{header}")
        if sessions:
            for s in sessions:
                print(item_format(s))
        else:
            print(warning)

    print_session_list(
        "🗓️ Reserved Review Slots:",
        reserved_reviews,
        lambda r: f"📌 {r['course']} → {r['topic']} → Review on {r['date']} from {r['start']} to {r['end']} ({r['duration']} min)",
        "⚠️ No review slots were reserved."
    )

    print_session_list(
        "📌 Study Sessions Related to Assignments:",
        scheduled_related,
        lambda s: f"📚 {s['course']} → {s['topic']} on {s['date']} from {s['start']} to {s['end']} ({s['duration']} min)",
        "⚠️ No related study sessions were scheduled."
    )

    print_session_list(
        "📝 Scheduled Assignment Sessions:",
        scheduled_assignments,
        lambda a: f"📌 {a['course']} → {a['title']} on {a['date']} from {a['start']} to {a['end']} ({a['duration']} min)",
        "⚠️ No assignment sessions were scheduled."
    )