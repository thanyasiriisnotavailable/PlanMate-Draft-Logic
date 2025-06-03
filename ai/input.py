user_preferences = {
    "preferredStudyTimes": ["late morning", "afternoon", "night"],
    "preferredSessionDuration": { "min": 30, "max": 90 },
    "revisionFrequency": "2-3 reviews per topic",
    "breakDuration": 15
}

availability = {
    "11/02/2025": ["10:00-12:00", "14:00-17:00", "20:00-22:00"],
    "12/02/2025": ["09:00-11:00", "14:00-16:00", "20:00-22:00"],
    "13/02/2025": ["10:00-12:00", "14:00-17:00", "20:00-22:00"],
    "14/02/2025": ["10:00-12:00", "14:00-18:00", "20:00-22:00"],
    "15/02/2025": ["08:00-11:00", "14:00-16:00", "20:00-22:00"],
    "17/02/2025": ["10:00-12:00", "14:00-17:00", "20:00-22:00"],
    "18/02/2025": ["10:00-12:00", "14:00-17:00", "20:00-22:00"],
    "19/02/2025": ["09:00-12:00", "14:00-17:00", "20:00-22:00"],
    "20/02/2025": ["09:00-12:00", "14:00-17:00", "20:00-22:00"],
    "21/02/2025": ["09:00-12:00", "14:00-17:00", "20:00-22:00"],
    "22/02/2025": ["09:00-12:00", "14:00-17:00", "20:00-22:00"],
    "24/02/2025": ["09:00-12:00", "14:00-17:00", "20:00-22:00"],
    "26/02/2025": ["09:00-12:00", "14:00-17:00", "20:00-22:00"]
}

courses = [
    {
        "name": "Operating Systems", "credit": 3, "examDate": "25/02/2025", "examTime": "09:00–11:00",
        "topics": [
            {"title": "CPU Scheduling", "difficulty": 3, "confidence": 2, "studyTime": 90},
            {"title": "Deadlocks", "difficulty": 4, "confidence": 3, "studyTime": 75},
            {"title": "Virtual Memory", "difficulty": 5, "confidence": 2, "studyTime": 120}
        ]
    },
    {
        "name": "Data Structures and Algorithms", "credit": 3, "examDate": "22/02/2025", "examTime": "10:00–12:00",
        "topics": [
            {"title": "Trees & Graphs", "difficulty": 3, "confidence": 2, "studyTime": 80},
            {"title": "Sorting Algorithms", "difficulty": 2, "confidence": 4, "studyTime": 50},
            {"title": "Dynamic Programming", "difficulty": 5, "confidence": 2, "studyTime": 110}
        ]
    },
    {
        "name": "Machine Learning", "credit": 3, "examDate": "23/02/2025", "examTime": "13:00–15:00",
        "topics": [
            {"title": "Regression Models", "difficulty": 3, "confidence": 3, "studyTime": 70},
            {"title": "Classification", "difficulty": 4, "confidence": 2, "studyTime": 90},
            {"title": "Neural Networks", "difficulty": 5, "confidence": 2, "studyTime": 130}
        ]
    },
    {
        "name": "Database Systems", "credit": 2, "examDate": "27/02/2025", "examTime": "09:30–11:30",
        "topics": [
            {"title": "SQL Joins", "difficulty": 2, "confidence": 4, "studyTime": 40},
            {"title": "Normalization", "difficulty": 3, "confidence": 3, "studyTime": 60},
            {"title": "Indexing & Query Optimization", "difficulty": 4, "confidence": 2, "studyTime": 90}
        ]
    },
    {
        "name": "Computer Networks", "credit": 2, "examDate": "25/02/2025", "examTime": "14:00–16:00",
        "topics": [
            {"title": "TCP/IP Model", "difficulty": 2, "confidence": 4, "studyTime": 50},
            {"title": "Routing Protocols", "difficulty": 4, "confidence": 2, "studyTime": 100},
            {"title": "Congestion Control", "difficulty": 3, "confidence": 3, "studyTime": 60}
        ]
    }
]

assignments = [
    {
        "course": "Computer Networks", "title": "Midterm Essay", "associatedTopic": ["TCP/IP Model"],
        "dueDate": "15/02/2025", "time": "15:00", "estimatedTime": 50
    },
    {
        "course": "Machine Learning", "title": "Final Project",
        "associatedTopic": ["Regression Models", "Classification", "Neural Networks"],
        "dueDate": "05/03/2025", "estimatedTime": 180
    }
]