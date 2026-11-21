"""Student OS schema: modules, databases, properties, sample rows, views and rollups."""
ROOT = "🎓 Student OS"

MODULES = [
    ("🎒 01. Academic Manager", "Manage all your subjects, classes, courses, assignments and attendance."),
    ("📚 02. Knowledge Hub", "Notes, study materials, reading and every idea you capture."),
    ("📝 03. Exam & Revision Center", "Plan exams, schedule revision and track the syllabus."),
    ("⚡ 04. Productivity Center", "Tasks, projects, daily and weekly planning, and study sessions."),
    ("🌱 05. Personal Life Manager", "Habits, goals, journaling and routines."),
    ("💰 06. Finance Manager", "Expenses, budgets, savings and subscriptions."),
    ("🚀 07. Self-Learning Center", "Online courses, skills, roadmaps and personal projects."),
    ("🤝 08. Collaboration Hub", "Group projects, team tasks and meeting notes."),
    ("🏆 09. Progress & Growth Center", "Grades, achievements, reviews and statistics."),
    ("🧰 10. Student Resources", "Contacts, documents, opportunities and emergency information."),
]
M = {i + 1: m[0] for i, m in enumerate(MODULES)}

# Each column: (name, type, detail). type: title text select multi status date number checkbox url files relation
# relation detail: (target_db, synced_property_name_on_target)
DBS = []
def db(name, module, section, desc, cols, rows, views):
    DBS.append(dict(name=name, module=module, section=section, desc=desc, cols=cols, rows=rows, views=views))

ST_TASK = "Not Started · In Progress · Done"
db("Courses", 1, "My Courses", "Every subject, class and course: school, university or online.",
   [("Course Name","title",""),("Course Code","text",""),("Instructor","text",""),
    ("Course Type","select","High School Subject · University Course · Online Course"),
    ("Semester","relation",("Semesters","Courses")),("Credits","number",""),
    ("Platform","select","Coursera · Udemy · edX · YouTube · Other"),("Course URL","url",""),
    ("Start Date","date",""),("End Date","date",""),("Progress","number","Percent"),
    ("Status","select","Active · Completed · Archived"),("Certificate","files","")],
   [["Calculus I","MATH101","Dr. Rahman","University Course","Fall 2026","3","","","2026-09-01","2026-12-20","60","Active",""],
    ["Intro to Programming","CS101","Prof. Ahmed","University Course","Fall 2026","3","","","2026-09-01","2026-12-20","70","Active",""],
    ["English Literature","ENG201","Ms. Karim","University Course","Spring 2026","3","","","2026-01-10","2026-05-30","100","Completed",""],
    ["Python for Data Science","","Andrew Ng","Online Course","","","Coursera","https://www.coursera.org","2026-10-01","2027-01-31","35","Active",""]],
   ["Active: Status = Active", "Completed: Status = Completed", "Archived: Status = Archived",
    "Online Courses (Gallery): Course Type = Online Course"])
db("Semesters", 1, "Semesters", "University terms. Courses roll up into each semester for GPA.",
   [("Semester","title",""),("Start Date","date",""),("End Date","date",""),("Status","select","Current · Upcoming · Completed")],
   [["Spring 2026","2026-01-10","2026-05-30","Completed"],["Fall 2026","2026-09-01","2026-12-20","Current"],["Spring 2027","2027-01-10","2027-05-30","Upcoming"]],
   ["Current: Status = Current"])
db("Class Timetable", 1, "Class Timetable", "Your weekly class schedule.",
   [("Class Name","title",""),("Course","relation",("Courses","Classes")),("Day","select","Monday · Tuesday · Wednesday · Thursday · Friday · Saturday · Sunday"),
    ("Start Time","text",""),("End Time","text",""),("Location","text",""),("Instructor","text","")],
   [["Calculus Lecture","Calculus I","Monday","09:00","10:30","Room 204","Dr. Rahman"],
    ["Programming Lab","Intro to Programming","Tuesday","11:00","13:00","Lab 3","Prof. Ahmed"],
    ["Calculus Tutorial","Calculus I","Thursday","14:00","15:00","Room 110","Dr. Rahman"]],
   ["Weekly Board: group by Day, sort by Start Time"])
db("Assignments", 1, "Assignment Tracker", "Every assignment and homework item with its deadline.",
   [("Assignment Name","title",""),("Course","relation",("Courses","Assignments")),("Due Date","date",""),
    ("Priority","select","High · Medium · Low"),("Status","status","Not Started · In Progress · Submitted · Completed · Overdue"),
    ("Estimated Hours","number",""),("Actual Hours","number",""),("Grade","text",""),("Submission Link","url","")],
   [["Problem Set 5","Calculus I","2026-11-25","High","In Progress","4","2","",""],
    ["Mini Project: Calculator","Intro to Programming","2026-12-02","Medium","Not Started","6","","",""],
    ["Problem Set 4","Calculus I","2026-11-15","High","Completed","4","5","A-","https://example.com"]],
   ["Calendar: by Due Date", "By Course: Table grouped by Course",
    "Pending Submission: Status is Not Started, In Progress or Overdue; sort Due Date ascending"])
db("Attendance", 1, "Attendance Tracker", "Log attendance for every class session.",
   [("Session","title",""),("Course","relation",("Courses","Attendance")),("Class Date","date",""),
    ("Attendance Status","select","Present · Absent · Late · Excused"),("Notes","text","")],
   [["Calculus Lecture – Nov 16","Calculus I","2026-11-16","Present",""],["Programming Lab – Nov 17","Intro to Programming","2026-11-17","Late","Bus delay"]],
   ["By Course: grouped by Course", "Absences: Attendance Status = Absent"])

db("Notes", 2, "My Notes", "Lecture notes, summaries and ideas, linked to courses and resources.",
   [("Note Title","title",""),("Course","relation",("Courses","Notes")),("Topic","text",""),
    ("Note Type","select","Lecture · Summary · Reading · Lab · Idea"),("Created Date","date",""),
    ("Tags","multi","Important · Review · Formula · Definition"),("Resources","relation",("Resources","Notes"))],
   [["Limits & Continuity","Calculus I","Limits","Lecture","2026-11-10","Important, Formula","Khan Academy – Limits"],
    ["Loops in Python","Intro to Programming","Control flow","Lecture","2026-11-12","Review","Python Docs"],
    ["Pandas basics","Python for Data Science","DataFrames","Summary","2026-11-18","","Python Docs"]],
   ["By Course: grouped by Course", "Recently Added: sort Created Date descending"])
db("Resources", 2, "Study Materials", "Videos, articles, books, files and links for your studies.",
   [("Resource Name","title",""),("Type","select","Video · Article · Book · PDF · Website · Course"),
    ("Course","relation",("Courses","Resources")),("Roadmap","relation",("Learning Roadmaps","Resources")),
    ("Source URL","url",""),("File Attachment","files",""),("Status","select","To Review · In Progress · Done")],
   [["Khan Academy – Limits","Video","Calculus I","","https://www.khanacademy.org","","Done"],
    ["Python Docs","Website","Intro to Programming","Phase 1: Python Basics","https://docs.python.org","","In Progress"]],
   ["By Course: grouped by Course", "To Review: Status = To Review"])
db("Reading Library", 2, "Reading Library", "Books and articles you are reading.",
   [("Title","title",""),("Author","text",""),("Category","select","Textbook · Non-fiction · Fiction · Article"),
    ("Reading Status","select","Want to Read · Reading · Finished"),("Progress","number","Percent"),("Key Takeaways","text","")],
   [["Atomic Habits","James Clear","Non-fiction","Reading","40","Small habits compound."]],
   ["Reading: Reading Status = Reading", "Gallery: all books"])
db("Brain Dump Inbox", 2, "Brain Dump Inbox", "Capture ideas, questions, reminders and random thoughts. Process them weekly.",
   [("Title","title",""),("Content","text",""),("Category","select","Idea · Question · Reminder · Thought"),
    ("Date Captured","date",""),("Processed","checkbox","")],
   [["Ask Dr. Rahman about L'Hôpital","Before next tutorial","Question","2026-11-20","No"]],
   ["Unprocessed: Processed is unchecked"])

db("Exams", 3, "Exam Tracker", "All quizzes, midterms and finals.",
   [("Exam Name","title",""),("Course","relation",("Courses","Exams")),("Exam Date","date",""),
    ("Exam Type","select","Quiz · Midterm · Final · Practical · Oral"),("Preparation Status","select","Not Started · Preparing · Ready"),
    ("Target Grade","text",""),("Status","select","Upcoming · Completed"),("Result","text","")],
   [["Calculus Final","Calculus I","2026-12-15","Final","Preparing","A","Upcoming",""],
    ["Programming Midterm","Intro to Programming","2026-10-20","Midterm","Ready","A","Completed","B+"]],
   ["Upcoming: Status = Upcoming; sort Exam Date ascending", "Calendar: by Exam Date", "Completed: Status = Completed"])
db("Revision Planner", 3, "Revision Planner", "Schedule revision topics for each exam.",
   [("Topic","title",""),("Course","relation",("Courses","Revision")),("Exam","relation",("Exams","Revision Plan")),
    ("Revision Date","date",""),("Priority","select","High · Medium · Low"),("Confidence Level","select","Low · Medium · High"),("Done","checkbox","")],
   [["Derivatives","Calculus I","Calculus Final","2026-12-01","High","Medium","No"],
    ["Integrals","Calculus I","Calculus Final","2026-12-05","High","Low","No"]],
   ["Calendar: by Revision Date", "This Week: Revision Date is this week"])
db("Syllabus Tracker", 3, "Syllabus Tracker", "Track every chapter and topic you need to learn.",
   [("Topic","title",""),("Course","relation",("Courses","Syllabus")),("Chapter","text",""),
    ("Learning Status","select","Not Started · Learning · Learned · Mastered"),("Confidence Level","select","Low · Medium · High")],
   [["Limits","Calculus I","Ch. 2","Learned","High"],["Derivatives","Calculus I","Ch. 3","Learning","Medium"]],
   ["By Course: grouped by Course", "Weak Topics: Confidence Level = Low"])

db("Tasks", 4, "Master Task Manager", "Every to-do in one place: academic, personal, project and team tasks.",
   [("Task Name","title",""),("Category","select","Academic · Personal · Project · Team"),("Priority","select","High · Medium · Low"),
    ("Due Date","date",""),("Status","status",ST_TASK),("Course","relation",("Courses","Tasks")),
    ("Project","relation",("Projects","Tasks")),("Goal","relation",("Goals","Tasks")),("Assigned To","text",""),
    ("Estimated Time (min)","number",""),("Completed Date","date","")],
   [["Finish Problem Set 5","Academic","High","2026-11-21","In Progress","Calculus I","","Get a 3.7 GPA","","120",""],
    ["Build calculator UI","Project","Medium","2026-11-28","Not Started","Intro to Programming","Calculator App","","","90",""],
    ["Write project report section","Team","Medium","2026-11-24","Not Started","Intro to Programming","Group Research Project","","Me",  "60",""],
    ["Review lecture notes","Academic","Low","2026-11-18","Done","Calculus I","","Get a 3.7 GPA","","30","2026-11-18"],
    ["Plan weekly budget","Personal","Low","2026-11-19","Not Started","","","Save for a laptop","","20",""]],
   ["Today: Due Date is today AND Status is not Done",
    "Upcoming: Due Date is after today AND Status is not Done; sort Due Date ascending",
    "Overdue: Due Date is before today AND Status is not Done",
    "Completed: Status is Done; sort Completed Date descending",
    "Board: grouped by Status", "Team Tasks: Category = Team (used in Collaboration Hub)"])
db("Projects", 4, "Projects", "Course, personal and group projects. Tasks roll up into progress.",
   [("Project Name","title",""),("Type","select","Personal · Group · Course"),("Course","relation",("Courses","Projects")),
    ("Skills","relation",("Skills","Projects")),("Team Members","text",""),("Start Date","date",""),("Deadline","date",""),
    ("Status","select","Planning · In Progress · Completed · On Hold"),("Project Link","url","")],
   [["Calculator App","Personal","Intro to Programming","Python","","2026-11-10","2026-12-10","In Progress","https://github.com"],
    ["Group Research Project","Group","Intro to Programming","Python","Sara, Tanvir, Me","2026-11-01","2026-12-05","In Progress",""]],
   ["Group Projects: Type = Group", "Personal Projects: Type = Personal", "Board: grouped by Status"])
db("Daily Planner", 4, "Daily Planner", "One page per day: priorities, schedule, habits and reflection.",
   [("Day","title",""),("Date","date",""),("Top 3 Priorities","text",""),("Schedule","text",""),
    ("Habits Done","relation",("Habits","Days Completed")),("Notes","text",""),("Daily Reflection","text","")],
   [["Sat, Nov 21","2026-11-21","1. Problem Set 5  2. Read Ch.3  3. Gym","09:00 Study · 14:00 Lab · 18:00 Gym","Read 20 minutes, Exercise","",""]],
   ["Today: Date is today", "Calendar: by Date"])
db("Weekly Planner", 4, "Weekly Planner", "Plan and review each week.",
   [("Week","title",""),("Week Start","date",""),("Weekly Goals","text",""),("Important Deadlines","text",""),
    ("Study Plan","text",""),("Personal Tasks","text",""),("Weekly Review","text","")],
   [["Week of Nov 16","2026-11-16","Finish PS5, start calculator app","PS5 – Nov 25","Calculus 6h, Programming 5h","Budget review",""]],
   ["Timeline: by Week Start"])
db("Study Sessions", 4, "Study Session Log", "Log every focused study session.",
   [("Session Name","title",""),("Course","relation",("Courses","Study Sessions")),("Task","relation",("Tasks","Study Sessions")),
    ("Date","date",""),("Duration (min)","number",""),("Focus Rating","select","⭐ · ⭐⭐ · ⭐⭐⭐ · ⭐⭐⭐⭐ · ⭐⭐⭐⭐⭐"),("Notes","text","")],
   [["Calculus practice","Calculus I","Finish Problem Set 5","2026-11-20","90","⭐⭐⭐⭐",""],
    ["Python loops","Intro to Programming","","2026-11-19","60","⭐⭐⭐",""]],
   ["This Week: Date is this week", "By Subject: grouped by Course (show Sum of Duration)"])

db("Habits", 5, "Habit Tracker", "Habits you are building. Tick them off in the Daily Planner.",
   [("Habit","title",""),("Category","select","Health · Study · Mindset · Personal"),("Frequency","select","Daily · Weekdays · Weekly"),
    ("Target","text",""),("Goal","relation",("Goals","Habits")),("Status","select","Active · Paused")],
   [["Read 20 minutes","Study","Daily","7 / week","Get a 3.7 GPA","Active"],["Exercise","Health","Weekdays","5 / week","","Active"]],
   ["Active: Status = Active"])
db("Goals", 5, "Goals & Milestones", "Long-term goals. Linked tasks roll up into progress.",
   [("Goal","title",""),("Category","select","Academic · Career · Health · Finance · Personal"),("Start Date","date",""),
    ("Target Date","date",""),("Status","select","Active · Completed · Paused"),("Next Action","text","")],
   [["Get a 3.7 GPA","Academic","2026-09-01","2026-12-20","Active","Finish Problem Set 5"],
    ["Save for a laptop","Finance","2026-10-01","2027-03-01","Active","Set monthly budget"]],
   ["Active: Status = Active", "Completed: Status = Completed"])
db("Personal Journal", 5, "Personal Journal", "Daily reflection.",
   [("Entry","title",""),("Date","date",""),("Mood","select","😄 Great · 🙂 Good · 😐 Okay · 😔 Low"),("Daily Highlights","text",""),
    ("Challenges","text",""),("Gratitude","text",""),("Reflection","text","")],
   [["Nov 20","2026-11-20","🙂 Good","Finished calculus practice","Felt tired","Supportive friends",""]],
   ["Calendar: by Date"])

db("Expenses", 6, "Expense Tracker", "Every expense, linked to its monthly budget.",
   [("Expense Name","title",""),("Amount","number","Currency"),("Date","date",""),
    ("Category","select","Food · Transport · Books · Rent · Entertainment · Other"),("Payment Method","select","Cash · Card · Mobile Banking"),
    ("Month","relation",("Monthly Budget","Expenses")),("Notes","text","")],
   [["Lunch","8","2026-11-20","Food","Cash","November 2026",""],["Bus pass","25","2026-11-02","Transport","Card","November 2026",""],
    ["Calculus textbook","45","2026-11-05","Books","Card","November 2026",""]],
   ["This Month: Date is this month", "By Category: grouped by Category (show Sum of Amount)"])
db("Monthly Budget", 6, "Monthly Budget", "One row per month. Expenses roll up automatically.",
   [("Month","title",""),("Budget Amount","number","Currency")],
   [["November 2026","300"],["December 2026","300"]], ["All months: sort by Month"])
db("Savings Goals", 6, "Savings Goals", "What you are saving for.",
   [("Goal","title",""),("Target Amount","number","Currency"),("Saved Amount","number","Currency"),("Target Date","date","")],
   [["New laptop","800","250","2027-03-01"]], ["Gallery: all goals"])
db("Subscriptions", 6, "Subscriptions", "Recurring payments and renewal dates.",
   [("Subscription Name","title",""),("Cost","number","Currency"),("Billing Frequency","select","Monthly · Yearly"),("Renewal Date","date","")],
   [["Spotify Student","5","Monthly","2026-12-01"],["Notion Plus","0","Monthly","2026-12-10"]], ["Upcoming Renewals: sort Renewal Date ascending"])

db("Skills", 7, "Skill Development", "Skills you are developing.",
   [("Skill Name","title",""),("Current Level","select","Beginner · Intermediate · Advanced · Expert"),
    ("Target Level","select","Beginner · Intermediate · Advanced · Expert"),("Category","select","Programming · Language · Design · Soft Skill · Other"),
    ("Progress","number","Percent")],
   [["Python","Beginner","Advanced","Programming","30"],["Public Speaking","Beginner","Intermediate","Soft Skill","15"]],
   ["Gallery: grouped by Category"])
db("Learning Roadmaps", 7, "Learning Roadmap", "Phase-by-phase plans for each learning goal.",
   [("Phase","title",""),("Learning Goal","text",""),("Skill","relation",("Skills","Roadmap")),("Topics","text",""),
    ("Practice Tasks","text",""),("Completion Status","select","Not Started · In Progress · Completed")],
   [["Phase 1: Python Basics","Become a data analyst","Python","Syntax, loops, functions","10 exercises","In Progress"],
    ["Phase 2: Data with Pandas","Become a data analyst","Python","DataFrames, cleaning","Analyze one dataset","Not Started"]],
   ["Board: grouped by Completion Status"])

db("Meeting Notes", 8, "Meeting Notes", "Notes and action items from group meetings.",
   [("Meeting Name","title",""),("Project","relation",("Projects","Meetings")),("Date","date",""),("Participants","text",""),
    ("Discussion","text",""),("Decisions","text",""),("Action Items","text","")],
   [["Kick-off","Group Research Project","2026-11-02","Sara, Tanvir, Me","Scope and roles","Topic: AI in education","Me: draft outline"]],
   ["Recent: sort Date descending"])

db("Grades", 9, "Academic Progress", "Every graded assessment. Feeds course averages and GPA.",
   [("Assessment","title",""),("Course","relation",("Courses","Grades")),("Grade (%)","number",""),
    ("Grade Points","number",""),("Date","date",""),("Feedback","text","")],
   [["Problem Set 4","Calculus I","90","3.7","2026-11-15","Great work"],["Programming Midterm","Intro to Programming","87","3.3","2026-10-20","Review recursion"]],
   ["By Course: grouped by Course"])
db("Achievements", 9, "Achievement Tracker", "Wins worth remembering.",
   [("Achievement","title",""),("Category","select","Academic · Extracurricular · Personal · Career"),("Date","date",""),("Description","text","")],
   [["Dean's List","Academic","2026-06-15","Spring 2026 semester"]], ["Timeline: by Date"])
db("Monthly Reviews", 9, "Monthly Review", "One review per month.",
   [("Month","title",""),("What did I accomplish?","text",""),("What did I struggle with?","text",""),
    ("What did I learn?","text",""),("What should I improve?","text",""),("Next month's priorities","text","")],
   [["October 2026","Passed midterm","Time management","Pomodoro works","Start assignments earlier","Finals prep"]],
   ["All reviews: sort by Month descending"])

db("Contacts", 10, "Important Contacts", "Instructors, advisors, classmates and offices.",
   [("Name","title",""),("Role","select","Instructor · Advisor · Classmate · Office · Emergency"),("Email","text",""),("Phone","text",""),("Notes","text","")],
   [["Dr. Rahman","Instructor","rahman@university.edu","","Office hours Mon 2–4pm"]], ["By Role: grouped by Role"])
db("Documents", 10, "Important Documents", "IDs, transcripts, certificates and other key files.",
   [("Document Name","title",""),("Document Type","select","ID · Transcript · Certificate · Visa · Other"),("File","files",""),
    ("Expiration Date","date",""),("Notes","text","")],
   [["Student ID","ID","","2027-08-31",""]], ["Expiring Soon: sort Expiration Date ascending"])
db("Scholarships & Opportunities", 10, "Scholarships & Opportunities", "Scholarships, internships and competitions.",
   [("Opportunity","title",""),("Organization","text",""),("Application Deadline","date",""),("Eligibility","text",""),
    ("Application Status","select","Researching · Applying · Submitted · Accepted · Rejected"),("Website","url","")],
   [["Merit Scholarship 2027","University Foundation","2027-01-15","GPA 3.5+","Researching","https://example.com"]],
   ["Board: grouped by Application Status", "Deadlines: sort Application Deadline ascending"])

DBN = {d["name"]: d for d in DBS}

# Computed properties, added after relations exist. Same list drives the API build and the setup guide.
# (database, property, "formula", expression) or (database, property, "rollup", (relation, target_property, function))
COMPUTED = [
    ("Tasks","Done Score","formula",'if(prop("Status") == "Done", 100, 0)'),
    ("Tasks","Overdue","formula",'not empty(prop("Due Date")) and prop("Due Date") < today() and prop("Status") != "Done"'),
    ("Tasks","Study Time (min)","rollup",("Study Sessions","Duration (min)","sum")),
    ("Assignments","Done Score","formula",'if(prop("Status") == "Completed" or prop("Status") == "Submitted", 100, 0)'),
    ("Courses","Assignments Done (%)","rollup",("Assignments","Done Score","average")),
    ("Courses","Study Minutes","rollup",("Study Sessions","Duration (min)","sum")),
    ("Courses","Study Hours","formula",'round(prop("Study Minutes") / 6) / 10'),
    ("Courses","Next Exam","rollup",("Exams","Exam Date","earliest_date")),
    ("Courses","Average Grade","rollup",("Grades","Grade (%)","average")),
    ("Courses","Avg Grade Points","rollup",("Grades","Grade Points","average")),
    ("Courses","GPA Points","formula",'prop("Avg Grade Points")'),
    ("Semesters","GPA","rollup",("Courses","GPA Points","average")),
    ("Semesters","Total Credits","rollup",("Courses","Credits","sum")),
    ("Projects","Progress (%)","rollup",("Tasks","Done Score","average")),
    ("Goals","Progress (%)","rollup",("Tasks","Done Score","average")),
    ("Exams","Revision Progress","rollup",("Revision Plan","Done","percent_checked")),
    ("Exams","Days Left","formula",'if(empty(prop("Exam Date")), "", dateBetween(prop("Exam Date"), today(), "days"))'),
    ("Habits","Times Completed","rollup",("Days Completed","Day","count")),
    ("Monthly Budget","Total Expenses","rollup",("Expenses","Amount","sum")),
    ("Monthly Budget","Remaining Budget","formula",'prop("Budget Amount") - prop("Total Expenses")'),
    ("Savings Goals","Progress (%)","formula",'if(prop("Target Amount") == 0, 0, round(prop("Saved Amount") / prop("Target Amount") * 100))'),
    ("Skills","Projects Built","rollup",("Projects","Project Name","count")),
    ("Resources","Linked Notes","rollup",("Notes","Note Title","count")),
]

FN_LABEL = {"sum":"Sum","average":"Average","count":"Count all","earliest_date":"Earliest date","percent_checked":"Percent checked"}
ROLLUPS = [(d, p, "Formula", c) if k == "formula" else (d, p, "Rollup", f"{c[0]} → {c[1]} → {FN_LABEL[c[2]]}")
           for d, p, k, c in COMPUTED]

