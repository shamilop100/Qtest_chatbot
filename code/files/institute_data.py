# institute_data.py

COURSES = {
    "manual":   {"name": "Manual Testing",                 "fee": 10000, "duration": "3 months"},
    "selenium": {"name": "Java & Selenium Automation",     "fee": 18000, "duration": "3 months"},
    "combined": {"name": "Java Selenium + Manual (Master)","fee": 28000, "duration": "3 months"},
}

SYLLABUS = {
    "manual":   ["Software Testing Fundamentals", "Test Case Writing",
                 "Bug Reporting", "Jira", "Selenium IDE"],
    "selenium": ["Core Java", "Selenium WebDriver", "TestNG",
                 "Cucumber", "JMeter", "Jira"],
    "combined": ["Core Java", "Selenium WebDriver", "TestNG",
                 "Cucumber", "JMeter", "Jira", "Manual Testing", "Real-time Projects"],
}

INFO = {
    "demo":        "Demo class available. Contact 9961 544 424.",
    "placement":   "100% Placement Assistance.",
    "certificate": "Industry-recognised Certificate provided.",
    "online_offline": "Online & Offline. Night & Sunday batches for professionals.",
    "location":    "📍 Emerald Mall, Mavoor Road, Kozhikode\n📞 9961 544 424",
}

# ── Course detector — message നോക്കി course identify ──────────────
_COURSE_KEYWORDS = {
    "manual":   ["manual", "മാനുവൽ"],
    "selenium": ["selenium", "java", "automation", "ഓട്ടോമേഷൻ"],
    "combined": ["combined", "master", "both", "രണ്ടും"],
}

def _detect_course(message: str) -> str | None:
    msg = message.lower()
    for course, keywords in _COURSE_KEYWORDS.items():
        if any(k in msg for k in keywords):
            return course
    return None  # course mention ഇല്ല → None

# ── Syllabus chunker — topic match ────────────────────────────────
_TOPIC_KEYWORDS = {
    "Core Java":              ["java", "core java", "oop"],
    "Selenium WebDriver":     ["selenium", "webdriver", "automation"],
    "TestNG":                 ["testng", "testing framework", "framework"],
    "Cucumber":               ["cucumber", "bdd"],
    "JMeter":                 ["jmeter", "performance", "load"],
    "Jira":                   ["jira", "bug tracking", "ticket"],
    "Manual Testing":         ["manual", "test case", "bug report"],
    "Real-time Projects":     ["project", "real time", "practical"],
}

def _find_topic(message: str) -> str | None:
    msg = message.lower()
    for topic, keywords in _TOPIC_KEYWORDS.items():
        if any(k in msg for k in keywords):
            return topic
    return None

# ── Main function — TRUNCATED output ──────────────────────────────
def get_institute_info(intent: str, course: str = None, message: str = "") -> str:

    # Level 1: detect course from actual message
    detected_course = _detect_course(message) or course or None

    # Level 2: intent-based field selection
    if intent == "pricing":
        if detected_course:
            # Only 1 course fee — not all 3
            c = COURSES[detected_course]
            return f"{c['name']}: ₹{c['fee']}"
        # No course mentioned → show all (unavoidable)
        return "\n".join(f"{v['name']}: ₹{v['fee']}" for v in COURSES.values())

    if intent == "duration":
        if detected_course:
            c = COURSES[detected_course]
            return f"{c['name']}: {c['duration']}"
        return "\n".join(f"{v['name']}: {v['duration']}" for v in COURSES.values())

    if intent == "syllabus":
        target = detected_course or "combined"
        syllabus = SYLLABUS[target]

        # Level 3: topic chunking — specific topic ചോദിച്ചോ?
        topic = _find_topic(message)
        if topic and topic in syllabus:
            return f"Yes, {topic} is covered in {COURSES[target]['name']}."

        # No specific topic → full syllabus (but only 1 course)
        return COURSES[target]["name"] + ":\n• " + "\n• ".join(syllabus)

    # Other intents — INFO dict direct lookup (already minimal)
    return INFO.get(intent, "Contact: 9961 544 424 | www.qtestsolutions.com")
