from datetime import datetime, timedelta
from availability_parser import generate_slots
from input import availability, user_preferences

def parse_date(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y")

def schedule_sessions(sessions, slots):
    scheduled = []
    unscheduled = []
    
    # Sort sessions by earliest due/exam date
    sessions = sorted(sessions, key=lambda s: parse_date(s.get("due", "31/12/2099")))

    # Copy slots to allow mutation
    slot_pool = slots.copy()

    for session in sessions:
        found = False
        for idx, slot in enumerate(slot_pool):
            if slot["duration"] >= session["duration"]:
                # Allocate this session
                scheduled.append({
                    "date": slot["date"],
                    "start": slot["start"],
                    "end": slot["end"],
                    "course": session["course"],
                    "title": session["title"],
                    "duration": session["duration"],
                    "type": session["type"]
                })

                # Remove the used slot or shorten it
                remaining = slot["duration"] - session["duration"]
                if remaining >= user_preferences["preferredSessionDuration"]["min"]:
                    start_time = datetime.strptime(slot["start"], "%H:%M")
                    new_start = start_time + timedelta(minutes=session["duration"] + user_preferences["breakDuration"])
                    slot_pool[idx]["start"] = new_start.strftime("%H:%M")
                    slot_pool[idx]["duration"] = remaining
                else:
                    slot_pool.pop(idx)

                found = True
                break
        
        if not found:
            unscheduled.append(session)

    return scheduled, unscheduled

if __name__ == "__main__":
    from input import courses, assignments

    # 1. Convert course topics to study sessions
    study_sessions = []
    for course in courses:
        for topic in course["topics"]:
            adjusted = topic.get("studyTime", 60)
            study_sessions.append({
                "type": "topic",
                "course": course["name"],
                "title": topic["title"],
                "duration": adjusted,
                "due": course["examDate"]
            })

    # 2. Add assignment sessions
    for assignment in assignments:
        study_sessions.append({
            "type": "assignment",
            "course": assignment["course"],
            "title": assignment["title"],
            "duration": assignment["estimatedTime"],
            "due": assignment["dueDate"]
        })

    # 3. Generate slots and schedule
    slots = generate_slots(availability, user_preferences)
    scheduled, unscheduled = schedule_sessions(study_sessions, slots)

    print("\n📅 Scheduled Sessions:")
    for item in scheduled:
        print(f"{item['date']} | {item['start']}–{item['end']} | {item['course']} - {item['title']} ({item['duration']} min)")

    print("\n⚠️ Unscheduled Sessions:")
    for item in unscheduled:
        print(f"{item['course']} - {item['title']} ({item['duration']} min), due {item['due']}")