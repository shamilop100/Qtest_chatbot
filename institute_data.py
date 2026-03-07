# institute_data.py — Knowledge Engine
# Single source of truth. No hallucination possible.

COURSES = {
    "manual":   {"name": "Manual Testing",                  "fee": 10000, "duration": "3 months"},
    "selenium": {"name": "Java & Selenium Automation",      "fee": 18000, "duration": "3 months"},
    "combined": {"name": "Java Selenium + Manual (Master)", "fee": 28000, "duration": "3 months"},
}

SYLLABUS = {
    "manual":   ["Software Testing Fundamentals", "Test Case Writing",
                 "Bug Reporting", "Jira", "Selenium IDE"],
    "selenium": ["Core Java", "Selenium WebDriver", "TestNG", "Cucumber", "JMeter", "Jira"],
    "combined": ["Core Java", "Selenium WebDriver", "TestNG", "Cucumber",
                 "JMeter", "Jira", "Manual Testing", "Real-time Projects"],
}

CONTACT = {
    "phone":   "9961 544 424",
    "website": "www.qtestsolutions.com",
    "address": "Emerald Mall, Mavoor Road, Kozhikode",
}

def get_answer(intent: str, course: str = None) -> str | None:
    """
    Knowledge Engine — returns answer if data exists, None if Claude needed.
    Returns None only for: other / truly unknown questions
    """

    if intent == "greeting":
        return "Hello! Welcome to QTest Software Solutions 😊 How can I help you?"

    if intent == "location":
        return (f"📍 {CONTACT['address']}\n"
                f"📞 {CONTACT['phone']}\n"
                f"🌐 {CONTACT['website']}")

    if intent == "courses":
        lines = ["We offer 3 courses:"]
        for c in COURSES.values():
            lines.append(f"• {c['name']} — ₹{c['fee']:,} ({c['duration']})")
        lines.append("\nAsk me about syllabus, demo or placement 😊")
        return "\n".join(lines)

    if intent == "duration":
        if course:
            c = COURSES[course]
            return f"{c['name']}: {c['duration']}"
        return "All 3 courses are 3 months duration 😊"

    if intent == "pricing":
        if course:
            c = COURSES[course]
            return f"{c['name']} fee: ₹{c['fee']:,} (3 months) 😊"
        lines = ["Course Fees:"]
        for c in COURSES.values():
            lines.append(f"• {c['name']} — ₹{c['fee']:,}")
        return "\n".join(lines)

    if intent == "syllabus":
        target = course or "combined"
        c = COURSES[target]
        topics = "\n• ".join(SYLLABUS[target])
        return f"{c['name']} syllabus:\n• {topics}"

    if intent == "placement":
        return ("✅ 100% Placement Assistance provided to all students.\n"
                f"Call {CONTACT['phone']} for details.")

    if intent == "certificate":
        return ("✅ Industry-recognised Course Completion Certificate\n"
                "provided upon successful course completion.")

    if intent == "demo":
        return (f"✅ Free Demo class available!\n"
                f"Call {CONTACT['phone']} to schedule your session.")

    if intent == "online_offline":
        return ("We offer both Online and Offline classes.\n"
                "🌙 Night batches available\n"
                "📅 Sunday batches for working professionals\n"
                f"Call {CONTACT['phone']} for batch timings.")

    return None  # → Claude handles this