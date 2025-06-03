from datetime import datetime, timedelta

def reserve_review_sessions(courses, slots, preferred_durations):
    reserved_reviews = []
    used_slot_ids = set()

    for course in courses:
        exam_date = datetime.strptime(course["examDate"], "%d/%m/%Y")
        review_date = (exam_date - timedelta(days=1)).strftime("%d/%m/%Y")

        # Try to find a slot on review_date that is not already used
        candidate_slots = [slot for slot in slots if slot["date"] == review_date and (slot["date"], slot["start"], slot["end"]) not in used_slot_ids]

        if not candidate_slots:
            print(f"⚠️ No available slots for review of {course['name']} on {review_date}")
            continue

        candidate_slots.sort(key=lambda x: x["duration"], reverse=True)
        best_slot = candidate_slots[0]
        used_slot_ids.add((best_slot["date"], best_slot["start"], best_slot["end"]))

        reserved_reviews.append({
            "title": f"Review: {course['name']}",
            "course": course["name"],
            "type": "review",
            "date": best_slot["date"],
            "start": best_slot["start"],
            "end": best_slot["end"],
            "duration": best_slot["duration"]
        })

    return reserved_reviews