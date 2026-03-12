# institute_data.py — Single source of truth

INSTITUTE_CONTEXT = """
INSTITUTE: QTest Software Solution LLP
LOCATION: Emerald Mall, Mavoor Road, Kozhikode, Kerala
PHONE: 9961 544 424
WEBSITE: www.qtestsolutions.com

COURSES:
1. Manual Testing
   - Fee: Rs.10,000
   - Duration: 3 months
   - Syllabus: Software Testing Fundamentals, Test Case Writing, Bug Reporting, Jira, Selenium IDE

2. Java & Selenium Automation
   - Fee: Rs.18,000
   - Duration: 3 months
   - Syllabus: Core Java, Selenium WebDriver, TestNG, Cucumber, JMeter, Jira

3. Java Selenium + Manual Master (Combined)
   - Fee: Rs.28,000
   - Duration: 3 months
   - Syllabus: Core Java, Selenium WebDriver, TestNG, Cucumber, JMeter, Jira, Manual Testing, Real-time Projects

OTHER INFO:
- Placement: 100% Placement Assistance provided to all students
- Certificate: Industry-recognised Course Completion Certificate provided
- Demo: Free demo class available, call 9961 544 424 to schedule
- Batch modes: Online and Offline classes available
- Special batches: Night batches and Sunday batches for working professionals
"""

def get_context() -> str:
    return INSTITUTE_CONTEXT