from datetime import datetime, timedelta
from input import availability, user_preferences

def str_to_time(s):
    return datetime.strptime(s, "%H:%M")

def time_to_str(t):
    return t.strftime("%H:%M")

def generate_slots(availability, preferences):
    min_dur = preferences["preferredSessionDuration"]["min"]
    max_dur = preferences["preferredSessionDuration"]["max"]
    break_dur = preferences["breakDuration"]

    all_slots = []
    slot_id = 0

    for date, blocks in availability.items():
        for block in blocks:
            start_str, end_str = block.split("-")
            block_start = str_to_time(start_str)
            block_end = str_to_time(end_str)
            current = block_start

            while (block_end - current).total_seconds() / 60 >= min_dur:
                remaining = (block_end - current).total_seconds() / 60

                if remaining >= max_dur:
                    session_length = max_dur
                elif remaining >= min_dur:
                    session_length = int(remaining)
                else:
                    break

                session_end = current + timedelta(minutes=session_length)

                all_slots.append({
                    "id": slot_id,
                    "date": date,
                    "start": time_to_str(current),
                    "end": time_to_str(session_end),
                    "duration": session_length
                })

                slot_id += 1
                current = session_end + timedelta(minutes=break_dur)

    return all_slots

# Test run
if __name__ == "__main__":
    slots = generate_slots(availability, user_preferences)
    for slot in slots:
        print(f"ID {slot['id']} | {slot['date']} | {slot['start']}–{slot['end']} ({slot['duration']} min)")
