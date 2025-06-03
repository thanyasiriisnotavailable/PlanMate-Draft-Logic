from datetime import datetime, timedelta

def schedule_review_sessions(sessions, slots, slot_availability):
    reserved = []

    for session in sessions:
        if session["type"] != "review":
            continue

        exam_date = datetime.strptime(session["examDate"], "%d/%m/%Y")
        review_date = (exam_date - timedelta(days=1)).strftime("%d/%m/%Y")

        # Filter slots on review date with enough time left
        candidate_slots = [
            slot for slot in slots
            if slot["date"] == review_date and slot_availability[slot["id"]] >= session["duration"]
        ]

        if not candidate_slots:
            print(f"⚠️ No slot available for review: {session['course']} - {session['topic']}")
            continue

        # Sort slots by remaining time descending
        candidate_slots.sort(key=lambda s: slot_availability[s["id"]], reverse=True)
        best_slot = candidate_slots[0]
        slot_id = best_slot["id"]

        # Deduct time
        slot_availability[slot_id] -= session["duration"]

        # Assign session to this slot
        session["date"] = best_slot["date"]
        session["start"] = best_slot["start"]
        session["end"] = best_slot["end"]
        session["slot_id"] = slot_id

        reserved.append(session)

    return reserved

def schedule_related_topic_sessions(assignments, study_sessions, slots, slot_availability):
    scheduled = []

    for assignment in assignments:
        due_date = datetime.strptime(assignment["dueDate"], "%d/%m/%Y")
        related_topics = assignment.get("associatedTopic", [])

        for topic in related_topics:
            # Find unscheduled study sessions matching the topic
            topic_sessions = [
                s for s in study_sessions
                if s["type"] == "study" and s["topic"] == topic and s["course"] == assignment["course"]
                and "slot_id" not in s  # Only unscheduled ones
            ]

            for session in topic_sessions:
                # Filter slots BEFORE the assignment due date and with enough duration
                valid_slots = [
                    slot for slot in slots
                    if datetime.strptime(slot["date"], "%d/%m/%Y") < due_date and
                    slot_availability[slot["id"]] >= session["duration"]
                ]

                if not valid_slots:
                    print(f"⚠️ No slot for related topic '{topic}' of assignment '{assignment['title']}'")
                    continue

                # Pick longest available slot
                valid_slots.sort(key=lambda s: slot_availability[s["id"]], reverse=True)
                chosen_slot = valid_slots[0]
                slot_id = chosen_slot["id"]

                # Assign slot info to session
                session["date"] = chosen_slot["date"]
                session["start"] = chosen_slot["start"]
                session["end"] = chosen_slot["end"]
                session["slot_id"] = slot_id

                slot_availability[slot_id] -= session["duration"]
                scheduled.append(session)

    return scheduled

from datetime import datetime

def schedule_assignment_sessions(assignments, assignment_sessions, slots, slot_availability):
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
                if datetime.strptime(slot["date"], "%d/%m/%Y") <= due_date
                and slot_availability[slot["id"]] >= session["duration"]
            ]

            if not valid_slots:
                print(f"⚠️ No slot found for assignment '{assignment['title']}' ({assignment['course']})")
                continue

            valid_slots.sort(key=lambda s: slot_availability[s["id"]], reverse=True)
            chosen_slot = valid_slots[0]
            slot_id = chosen_slot["id"]

            session["date"] = chosen_slot["date"]
            session["start"] = chosen_slot["start"]
            session["end"] = chosen_slot["end"]
            session["slot_id"] = slot_id

            slot_availability[slot_id] -= session["duration"]
            scheduled.append(session)

    return scheduled
