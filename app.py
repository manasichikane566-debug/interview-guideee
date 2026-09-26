from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

app.secret_key = "interview-guide-secret-key"


# =========================================================
# DATABASE
# =========================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "interview_guide.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_achievements(user_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(*) AS total_quizzes,
        MAX(percentage) AS best_percentage
        FROM quiz_results
        WHERE user_id = ?
        """,
        (user_id,)
    )

    result = cur.fetchone()

    cur.close()
    conn.close()

    total_quizzes = result["total_quizzes"]
    best_percentage = result["best_percentage"] or 0

    achievements = [

        {
            "name": "🌱 First Step",
            "description": "Complete your first quiz.",
            "unlocked": total_quizzes >= 1
        },

        {
            "name": "🎯 Quiz Master",
            "description": "Complete 5 quizzes.",
            "unlocked": total_quizzes >= 5
        },

        {
            "name": "💯 Perfect Score",
            "description": "Score 100% in a quiz.",
            "unlocked": best_percentage >= 100
        },

        {
            "name": "🔥 High Scorer",
            "description": "Score 80% or higher in a quiz.",
            "unlocked": best_percentage >= 80
        },

        {
            "name": "👔 HR Ready",
            "description": "Practice HR interview questions.",
            "unlocked": False
        },

        {
            "name": "🚀 Interview Pro",
            "description": "Complete 10 interview activities.",
            "unlocked": total_quizzes >= 10
        }
    ]

    return achievements



def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS quiz_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        total INTEGER NOT NULL,
        percentage REAL NOT NULL,
        taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    cur.execute("""
CREATE TABLE IF NOT EXISTS achievement_views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")


    conn.commit()
    cur.close()
    conn.close()

init_db()
    # =========================================================
    # HOME
    # =========================================================

@app.route("/")
def home():
    return render_template("home.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        )

        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            conn.close()

            flash("Email already registered!", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        cur.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
            """,
            (name, email, hashed_password)
        )

        conn.commit()

        cur.close()
        conn.close()

        flash(
            "Registration successful! Please login.",
            "success"
        )

        return redirect(url_for("login"))

        # IMPORTANT:
            # This must be outside the POST block.
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for("login"))

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["name"] = user["name"]

            flash("Login successful!", "success")

            return redirect(url_for("questions"))

        flash("Invalid email or password!", "danger")

        return redirect(url_for("login"))

        # This handles GET /login
    return render_template("login.html")



        # =========================================================
        # LOGOUT
        # =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(url_for("home"))


# =========================================================
# QUIZ QUESTIONS
# =========================================================

QUESTIONS = [

    {
        "question": "What is Python?",
        "options": [
            "A programming language",
            "An operating system",
            "A database",
            "A web browser"
        ],
        "answer": "A programming language"
    },

    {
        "question": "Which keyword is used to define a function in Python?",
        "options": [
            "func",
            "define",
            "def",
            "function"
        ],
        "answer": "def"
    },

    {
        "question": "Which data type stores True or False?",
        "options": [
            "String",
            "Boolean",
            "Float",
            "List"
        ],
        "answer": "Boolean"
    },

    {
        "question": "Which symbol is used for a comment in Python?",
        "options": [
            "//",
            "#",
            "/* */",
            "--"
        ],
        "answer": "#"
    },

    {
        "question": "Which collection is ordered and changeable in Python?",
        "options": [
            "Tuple",
            "List",
            "Set",
            "String"
        ],
        "answer": "List"
    },

    {
        "question": "Which OOP concept allows a class to acquire properties of another class?",
        "options": [
            "Encapsulation",
            "Inheritance",
            "Polymorphism",
            "Abstraction"
        ],
        "answer": "Inheritance"
    },

    {
        "question": "Which OOP concept hides internal implementation details?",
        "options": [
            "Inheritance",
            "Encapsulation",
            "Polymorphism",
            "Compilation"
        ],
        "answer": "Encapsulation"
    },

    {
        "question": "What is polymorphism?",
        "options": [
            "One interface with different implementations",
            "Creating a database",
            "Deleting an object",
            "Running a program"
        ],
        "answer": "One interface with different implementations"
    },

    {
        "question": "What is a constructor?",
        "options": [
            "A method used to initialize an object",
            "A database",
            "A variable",
            "A loop"
        ],
        "answer": "A method used to initialize an object"
    },

    {
        "question": "Which data structure follows LIFO?",
        "options": [
            "Queue",
            "Stack",
            "Tree",
            "Graph"
        ],
        "answer": "Stack"
    },

    {
        "question": "Which data structure follows FIFO?",
        "options": [
            "Stack",
            "Queue",
            "Tree",
            "Heap"
        ],
        "answer": "Queue"
    },

    {
        "question": "What is the average time complexity of binary search?",
        "options": [
            "O(n)",
            "O(log n)",
            "O(n²)",
            "O(1)"
        ],
        "answer": "O(log n)"
    },

    {
        "question": "Which data structure is commonly used in BFS?",
        "options": [
            "Stack",
            "Queue",
            "Array",
            "Tree"
        ],
        "answer": "Queue"
    },

    {
        "question": "What does DBMS stand for?",
        "options": [
            "Database Management System",
            "Data Backup Management System",
            "Database Memory System",
            "Digital Base Management Software"
        ],
        "answer": "Database Management System"
    },

    {
        "question": "Which language is used to query relational databases?",
        "options": [
            "HTML",
            "CSS",
            "SQL",
            "Python"
        ],
        "answer": "SQL"
    },

    {
        "question": "Which SQL command is used to retrieve data?",
        "options": [
            "INSERT",
            "SELECT",
            "UPDATE",
            "DELETE"
        ],
        "answer": "SELECT"
    },

    {
        "question": "Which SQL command is used to add a new record?",
        "options": [
            "INSERT",
            "ADD",
            "UPDATE",
            "CREATE"
        ],
        "answer": "INSERT"
    },

    {
        "question": "Which SQL command modifies existing data?",
        "options": [
            "CHANGE",
            "UPDATE",
            "MODIFY",
            "ALTER"
        ],
        "answer": "UPDATE"
    },

    {
        "question": "What is a primary key?",
        "options": [
            "A field that uniquely identifies a record",
            "A password",
            "A duplicate field",
            "A backup table"
        ],
        "answer": "A field that uniquely identifies a record"
    },

    {
        "question": "What does OS stand for?",
        "options": [
            "Operating System",
            "Open Software",
            "Online Service",
            "Output System"
        ],
        "answer": "Operating System"
    },

    {
        "question": "What is a process?",
        "options": [
            "A program in execution",
            "A database",
            "A hardware device",
            "A web page"
        ],
        "answer": "A program in execution"
    },

    {
        "question": "Which memory is volatile?",
        "options": [
            "ROM",
            "RAM",
            "SSD",
            "DVD"
        ],
        "answer": "RAM"
    },

    {
        "question": "What does LAN stand for?",
        "options": [
            "Local Area Network",
            "Large Area Network",
            "Linked Area Network",
            "Local Access Node"
        ],
        "answer": "Local Area Network"
    },

    {
        "question": "Which device connects different networks?",
        "options": [
            "Router",
            "Keyboard",
            "Monitor",
            "Printer"
        ],
        "answer": "Router"
    },

    {
        "question": "What does IP stand for?",
        "options": [
            "Internet Protocol",
            "Internal Program",
            "Internet Process",
            "Interface Port"
        ],
        "answer": "Internet Protocol"
    },

    {
        "question": "How many layers are there in the OSI model?",
        "options": [
            "5",
            "6",
            "7",
            "8"
        ],
        "answer": "7"
    },

    {
        "question": "Which language is mainly used to structure web pages?",
        "options": [
            "HTML",
            "CSS",
            "SQL",
            "Python"
        ],
        "answer": "HTML"
    },

    {
        "question": "Which language is mainly used to style web pages?",
        "options": [
            "HTML",
            "CSS",
            "Java",
            "SQL"
        ],
        "answer": "CSS"
    },

    {
        "question": "Which language adds interactivity to web pages?",
        "options": [
            "JavaScript",
            "HTML",
            "CSS",
            "SQL"
        ],
        "answer": "JavaScript"
    },

    {
        "question": "What does API stand for?",
        "options": [
            "Application Programming Interface",
            "Application Process Internet",
            "Advanced Program Integration",
            "Automated Programming Input"
        ],
        "answer": "Application Programming Interface"
    },

    {
        "question": "What is Flask?",
        "options": [
            "A Python web framework",
            "A database",
            "An operating system",
            "A web browser"
        ],
        "answer": "A Python web framework"
    },

    {
        "question": "What is phishing?",
        "options": [
            "A fraudulent attempt to obtain sensitive information",
            "A backup method",
            "A sorting algorithm",
            "A database query"
        ],
        "answer": "A fraudulent attempt to obtain sensitive information"
    },

    {
        "question": "What does malware mean?",
        "options": [
            "Malicious software",
            "Managed hardware",
            "Manual software",
            "Memory language"
        ],
        "answer": "Malicious software"
    },

    {
        "question": "What is encryption?",
        "options": [
            "Converting data into an encoded form",
            "Deleting data",
            "Copying files",
            "Formatting a disk"
        ],
        "answer": "Converting data into an encoded form"
    },

    {
        "question": "What does authentication verify?",
        "options": [
            "Identity",
            "File size",
            "Internet speed",
            "Screen resolution"
        ],
        "answer": "Identity"
    },

    {
        "question": "What is a firewall?",
        "options": [
            "A system that filters network traffic",
            "A programming language",
            "A database",
            "A CPU component"
        ],
        "answer": "A system that filters network traffic"
    },

    {
        "question": "What does AI stand for?",
        "options": [
            "Artificial Intelligence",
            "Automated Internet",
            "Advanced Interface",
            "Application Integration"
        ],
        "answer": "Artificial Intelligence"
    },

    {
        "question": "What is machine learning?",
        "options": [
            "A method where systems learn patterns from data",
            "A database language",
            "A network cable",
            "A web styling method"
        ],
        "answer": "A method where systems learn patterns from data"
    },

    {
        "question": "What is Generative AI?",
        "options": [
            "AI that generates new content",
            "AI used only for storage",
            "A type of router",
            "A database backup"
        ],
        "answer": "AI that generates new content"
    },

    {
        "question": "What is cloud computing?",
        "options": [
            "Using computing resources over a network",
            "Only storing files on a USB",
            "A programming language",
            "A CPU instruction"
        ],
        "answer": "Using computing resources over a network"
    },

    {
        "question": "What does IoT stand for?",
        "options": [
            "Internet of Things",
            "Input of Technology",
            "Internet of Tools",
            "Integrated Online Transfer"
        ],
        "answer": "Internet of Things"
    },

    {
        "question": "Which is an example of an IoT device?",
        "options": [
            "Smart temperature sensor",
            "Paper notebook",
            "Printed book",
            "Pencil"
        ],
        "answer": "Smart temperature sensor"
    },

    {
        "question": "What does SDLC stand for?",
        "options": [
            "Software Development Life Cycle",
            "System Data Logic Control",
            "Software Design Language Code",
            "System Development Link Chain"
        ],
        "answer": "Software Development Life Cycle"
    },

    {
        "question": "What is debugging?",
        "options": [
            "Finding and fixing program errors",
            "Designing a logo",
            "Creating a database backup",
            "Installing hardware"
        ],
        "answer": "Finding and fixing program errors"
    },

    {
        "question": "Which tool is commonly used for version control?",
        "options": [
            "Git",
            "Flask",
            "MySQL",
            "Chrome"
        ],
        "answer": "Git"
    },

    {
        "question": "What does CPU stand for?",
        "options": [
            "Central Processing Unit",
            "Computer Personal Unit",
            "Central Program Utility",
            "Control Processing User"
        ],
        "answer": "Central Processing Unit"
    }
]
# =========================================================

# APTITUDE QUIZ QUESTIONS

# =========================================================

APTITUDE_QUESTIONS = [
    {
        "question": "What is 20% of 100?",
        "options": [
            "10",
            "20",
            "30",
            "40"
        ],
        "answer": "20"
    },

    {
        "question": "If a train travels 60 km in 1 hour, what is its speed?",
        "options": [
            "30 km/h",
            "40 km/h",
            "60 km/h",
            "80 km/h"
        ],
        "answer": "60 km/h"
    },

    {
        "question": "What is the average of 10, 20 and 30?",
        "options": [
            "15",
            "20",
            "25",
            "30"
        ],
        "answer": "20"
    },

    {
        "question": "If 5 + 5 = 10, what is 10 + 10?",
        "options": [
            "15",
            "20",
            "25",
            "30"
        ],
        "answer": "20"
    },

    {
        "question": "What is the next number in the series: 2, 4, 6, 8, ?",
        "options": [
            "9",
            "10",
            "11",
            "12"
        ],
        "answer": "10"
    }

]

# =========================================================
# HR INTERVIEW QUESTIONS
# =========================================================

HR_QUESTIONS = [

    {
        "question": "Tell me about yourself.",
        "answer": "Give a brief introduction about your education, skills, projects, experience, and career goals."
    },

    {
        "question": "What are your strengths?",
        "answer": "Mention 2-3 strengths that are relevant to the job and support them with examples."
    },

    {
        "question": "What is your weakness?",
        "answer": "Mention a genuine weakness and explain what you are doing to improve it."
    },

    {
        "question": "Why should we hire you?",
        "answer": "Explain how your skills, knowledge, attitude, and willingness to learn can contribute to the organization."
    },

    {
        "question": "Why do you want to join our company?",
        "answer": "Explain your interest in the company, its work, products, culture, or learning opportunities."
    },

    {
        "question": "Where do you see yourself in five years?",
        "answer": "Talk about your professional growth, responsibilities, skills, and contribution to the organization."
    },

    {
        "question": "How do you handle pressure?",
        "answer": "Explain how you prioritize tasks, stay organized, remain calm, and solve problems under pressure."
    },

    {
        "question": "How do you handle failure?",
        "answer": "Explain what you learned from the experience and how you used that learning to improve."
    },

    {
        "question": "Are you comfortable working in a team?",
        "answer": "Explain your teamwork experience and how you communicate and collaborate with others."
    },

    {
        "question": "Tell me about a challenge you faced.",
        "answer": "Describe the situation, what action you took, and the result."
    },

    {
        "question": "How do you manage deadlines?",
        "answer": "Explain how you prioritize tasks, plan your work, and track your progress."
    },

    {
        "question": "What motivates you?",
        "answer": "Talk about factors such as learning, solving problems, achieving goals, or taking responsibility."
    },

    {
        "question": "Are you willing to learn new technologies?",
        "answer": "Explain that you are open to learning and give an example of how you have learned something new."
    },

    {
        "question": "Do you have any questions for us?",
        "answer": "Ask relevant questions about the role, team, responsibilities, learning opportunities, or company."
    }
]
# =========================================================
# HR INTERVIEW
# =========================================================

@app.route("/hr-interview")
def hr_interview():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    return render_template(
        "hr.html",
        questions=HR_QUESTIONS
)
# =========================================================
# ACHIEVEMENTS
# =========================================================

@app.route("/achievements")
def achievements():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT achievement_id
        FROM achievement_views
        WHERE user_id = ?
        """,
        (session["user_id"],)
    )

    viewed_rows = cur.fetchall()

    cur.close()
    conn.close()

    viewed_ids = {
        row["achievement_id"]
        for row in viewed_rows
    }

    achievements = []

    for achievement_id, achievement in ACHIEVEMENT_DETAILS.items():

        achievement_copy = achievement.copy()

        achievement_copy["id"] = achievement_id
        achievement_copy["viewed"] = achievement_id in viewed_ids

        achievements.append(achievement_copy)

    total_achievements = len(achievements)

    explored_count = len(viewed_ids)

    progress = round(
         (explored_count / total_achievements) * 100
    ) if total_achievements else 0

    return render_template(
    "achievements.html",
    achievements=achievements,
    explored_count=explored_count,
    total_achievements=total_achievements,
    progress=progress
)


   

ACHIEVEMENT_DETAILS = {

    1: {
        "title": "🌱 First Step",
        "description": "Start your interview preparation journey.",
        "how_to_earn": "Complete your first interview quiz.",
        "benefit": "Build a habit of regular interview practice.",
        "color": "green",
        "action_text": "🎯 Start Quiz",
        "action_url": "quiz"
    },

    2: {
        "title": "🎯 Quiz Master",
        "description": "Become a regular quiz practice champion.",
        "how_to_earn": "Complete multiple practice quizzes.",
        "benefit": "Improve your knowledge through regular practice.",
        "color": "blue",
        "action_text": "🎯 Take Quiz",
        "action_url": "quiz"
    },

    3: {
        "title": "💯 Perfect Score",
        "description": "Achieve a perfect score in a quiz.",
        "how_to_earn": "Answer every question correctly in a quiz.",
        "benefit": "Demonstrate strong understanding of the topics.",
        "color": "gold",
        "action_text": "🎯 Try Quiz",
        "action_url": "quiz"
    },

    4: {
        "title": "🔥 High Scorer",
        "description": "Show excellent performance in your quiz.",
        "how_to_earn": "Achieve 80% or higher in a practice quiz.",
        "benefit": "Track your improvement and build confidence.",
        "color": "orange",
        "action_text": "🔥 Practice Quiz",
        "action_url": "quiz"
    },

    5: {
        "title": "👔 HR Ready",
        "description": "Prepare yourself for HR interviews.",
        "how_to_earn": "Practice common HR interview questions.",
        "benefit": "Improve your confidence when answering HR questions.",
        "color": "purple",
        "action_text": "👔 Practice HR Questions",
        "action_url": "hr_interview"
    },

    6: {
        "title": "💻 Technical Explorer",
        "description": "Explore important technical interview topics.",
        "how_to_earn": "Explore the technical topics section.",
        "benefit": "Strengthen your technical interview preparation.",
        "color": "cyan",
        "action_text": "💻 Explore Technical Topics",
        "action_url": "technical_topics"
    },

    7: {
        "title": "🚀 Interview Pro",
        "description": "Complete multiple interview preparation activities.",
        "how_to_earn": "Practice different sections of the Interview Guide.",
        "benefit": "Build well-rounded interview preparation skills.",
        "color": "red",
        "action_text": "🚀 Start Interview Practice",
        "action_url": "questions"
    }
}




@app.route("/achievement/<int:achievement_id>")
def achievement_detail(achievement_id):

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    achievement = ACHIEVEMENT_DETAILS.get(achievement_id)

    if achievement is None:
        flash("Achievement not found.", "danger")
        return redirect(url_for("achievements"))

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO achievement_views
        (user_id, achievement_id)
        VALUES (?, ?)
        """,
        (session["user_id"], achievement_id)
    )

    conn.commit()

    cur.close()
    conn.close()

    return render_template(
    "achievement_detail.html",
    achievement=achievement
)


# =========================================================
# QUESTIONS PAGE
# =========================================================

@app.route("/questions")
def questions():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    return render_template(
        "question.html",
        questions=QUESTIONS
    )


# =========================================================
# QUIZ
# =========================================================

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":

        score = 0
        total = len(QUESTIONS)

        for i, question in enumerate(QUESTIONS):

            user_answer = request.form.get("q" + str(i))

            if user_answer == question["answer"]:
                score += 1

        percentage = round((score / total) * 100, 2)

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
                    """
                    INSERT INTO quiz_results
                    (user_id, score, total, percentage)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        session["user_id"],
                        score,
                        total,
                        percentage
                    )
                )

        conn.commit()
        cur.close()
        conn.close()

        return render_template(
            "quiz_result.html",
            score=score,
            total=total,
            percentage=percentage
        )

    return render_template(
        "quiz.html",
        questions=QUESTIONS
        )

# =========================================================
# INTERVIEW TIPS
# =========================================================

@app.route("/tips")
def tips():

    tips_list = [
        "Read the job description carefully.",
        "Practice common interview questions.",
        "Revise programming and technical concepts.",
        "Prepare a clear self introduction.",
        "Maintain confidence and good communication.",
        "Be honest if you do not know an answer.",
        "Practice mock interviews regularly.",
        "Research the company and understand its products or services.",
        "Prepare a strong self-introduction.",
        "Be ready to explain every project mentioned in your resume.",
        "Practice technical questions related to the job role.",
        "Use real examples when explaining your skills.",
        "Listen carefully to the interviewer.",
        "If you do not know an answer, stay calm and be honest.",
        "Keep your answers clear and relevant.",
        "Prepare questions to ask the interviewer.",
        "Review your answers after the interview.",
        "Arrive 10-15 minutes before the interview.",
        "Keep your resume and important documents ready.",
        "Dress neatly and professionally.",
        "Keep your phone on silent.",
        "Maintain good eye contact.",
        "Speak clearly.",
        "Stay positive when answering difficult questions.",
        "Thank the interviewer before leaving."
    ]

    return render_template(
"tips.html",
tips=tips_list
)
# =========================================================
# COMMUNICATION SKILLS
# =========================================================

@app.route("/communication")
def communication():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    return render_template("communication.html")

@app.route("/communication/speaking")
def speaking_skills():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    return render_template("speaking.html")

@app.route("/communication/eye-contact")
def eye_contact():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    return render_template("eye_contact.html")


@app.route("/communication/body-language")
def body_language():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    return render_template("body_language.html")

@app.route("/communication/dressing-sense")
def dressing_sense():
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    return render_template("dressing_sense.html")

@app.route("/communication/interview-etiquette")
def interview_etiquette():
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    return render_template("interview_etiquette.html")

@app.route("/communication/confidence")
def confidence():
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    return render_template("confidence.html")
# =========================================================
# PROGRESS
# =========================================================

@app.route("/progress")
def progress():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT score, total, percentage, taken_at
        FROM quiz_results
        WHERE user_id = ?
        ORDER BY taken_at DESC
        """,
        (session["user_id"],)
    )

    results = cur.fetchall()

    cur.close()
    conn.close()

    best = max(
        [float(result["percentage"]) for result in results],
        default=0
    )

    return render_template(
    "progress.html",
    results=results,
    best=best
)
    
# =========================================================

# APTITUDE QUIZ

# =========================================================

@app.route("/aptitude-quiz", methods=["GET", "POST"])
def aptitude_quiz():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":

        score = 0
        total = len(APTITUDE_QUESTIONS)

        for i, question in enumerate(APTITUDE_QUESTIONS):

            user_answer = request.form.get("q" + str(i))

            if user_answer == question["answer"]:
                score += 1

        percentage = round((score / total) * 100, 2)

        return render_template(
            "aptitude_result.html",
            score=score,
            total=total,
            percentage=percentage
        )

    return render_template(
            "aptitude_quiz.html",
            questions=APTITUDE_QUESTIONS
        )


# =========================================================
# APTITUDE & STAR METHOD
# =========================================================

@app.route("/aptitude-star")
def aptitude_star():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    aptitude_topics = [
        {
            "name": "🔢 Quantitative Aptitude",
            "topics": [
                "Percentage",
                "Profit and Loss",
                "Ratio and Proportion",
                "Average",
                "Simple Interest",
                "Compound Interest",
                "Time and Work",
                "Time, Speed and Distance",
                "Number System",
                "Probability"
            ]
        },

        {
            "name": "🧩 Logical Reasoning",
            "topics": [
                "Number Series",
                "Coding and Decoding",
                "Blood Relations",
                "Direction Sense",
                "Syllogism",
                "Seating Arrangement",
                "Logical Puzzles"
            ]
        },

        {
            "name": "📊 Data Interpretation",
            "topics": [
                "Tables",
                "Bar Graphs",
                "Pie Charts",
                "Line Graphs",
                "Data Analysis"
            ]
        },

        {
            "name": "📝 Verbal Ability",
            "topics": [
                "Synonyms",
                "Antonyms",
                "Grammar",
                "Sentence Correction",
                "Reading Comprehension"
            ]
        }
    ]

    star_topics = [
        {
            "name": "⭐ STAR Method",
            "topics": [
                "Situation – Explain the situation",
                "Task – Explain your responsibility",
                "Action – Explain what you did",
                "Result – Explain the outcome",
                "How to use STAR in interviews"
            ]
        },

        {
            "name": "💡 STAR Answer Practice",
            "topics": [
                "Teamwork Example",
                "Leadership Example",
                "Problem-Solving Example",
                "Failure Example",
                "Challenge Example",
                "Achievement Example"
            ]
        }
    ]

    return render_template(
    "aptitude_star.html",
    aptitude_topics=aptitude_topics,
    star_topics=star_topics
)

# =========================================================
# TECHNICAL TOPICS
# =========================================================

@app.route("/technical-topics")
def technical_topics():

    topics = [

        {
            "name": "🐍 Python",
            "topics": [
                "Variables and Data Types",
                "Operators",
                "Conditional Statements",
                "Loops",
                "Functions",
                "Lists, Tuples and Dictionaries",
                "Object-Oriented Programming",
                "Exception Handling",
                "File Handling",
                "Modules and Packages"
            ]
        },

        {
            "name": "☕ Java",
            "topics": [
                "Classes and Objects",
                "Inheritance",
                "Polymorphism",
                "Encapsulation",
                "Abstraction",
                "Exception Handling",
                "Interfaces",
                "Collections",
                "Multithreading"
            ]
        },

        {
            "name": "💻 C / C++",
            "topics": [
                "Variables and Data Types",
                "Operators",
                "Loops",
                "Functions",
                "Arrays",
                "Pointers",
                "Structures",
                "Classes and Objects",
                "Inheritance",
                "Polymorphism"
            ]
        },

        {
            "name": "🗄️ Database",
            "topics": [
                "DBMS Basics",
                "SQL",
                "SELECT, INSERT, UPDATE and DELETE",
                "Joins",
                "Primary Key and Foreign Key",
                "Normalization",
                "Transactions",
                "Indexes",
                "Constraints"
            ]
        },

        {
            "name": "🌐 Web Development",
            "topics": [
                "HTML",
                "CSS",
                "JavaScript",
                "HTTP and HTTPS",
                "Forms",
                "Responsive Design",
                "DOM",
                "Web APIs",
                "Frontend and Backend"
            ]
        },

        {
            "name": "📊 Data Structures",
            "topics": [
                "Array",
                "Stack",
                "Queue",
                "Linked List",
                "Tree",
                "Graph",
                "Hashing",
                "Searching",
                "Sorting",
                "Time Complexity"
            ]
        },

        {
            "name": "🖥️ Operating System",
            "topics": [
                "Introduction to Operating System",
                "Process Management",
                "Threads",
                "CPU Scheduling",
                "Memory Management",
                "Virtual Memory",
                "Deadlock",
                "File Management",
                "Process Synchronization"
            ]
        },

        {
            "name": "🌐 Computer Networks",
            "topics": [
                "Introduction to Networking",
                "LAN, MAN and WAN",
                "OSI Model",
                "TCP/IP Model",
                "IP Address",
                "MAC Address",
                "Router and Switch",
                "DNS",
                "HTTP and HTTPS",
                "TCP and UDP"
            ]
        },

        {
            "name": "🔐 Cyber Security",
            "topics": [
                "Introduction to Cyber Security",
                "CIA Triad",
                "Authentication",
                "Authorization",
                "Encryption",
                "Hashing",
                "Firewall",
                "Malware",
                "Phishing",
                "Network Security"
            ]
        },

        {
            "name": "🤖 Artificial Intelligence",
            "topics": [
                "Introduction to AI",
                "Machine Learning",
                "Deep Learning",
                "Neural Networks",
                "Natural Language Processing",
                "Computer Vision",
                "Generative AI",
                "AI Applications"
            ]
        },

        {
            "name": "☁️ Cloud Computing",
            "topics": [
                "Introduction to Cloud Computing",
                "Cloud Service Models",
                "IaaS",
                "PaaS",
                "SaaS",
                "Public Cloud",
                "Private Cloud",
                "Hybrid Cloud",
                "Virtualization"
            ]
        },

        {
            "name": "📱 IoT",
            "topics": [
                "Introduction to IoT",
                "IoT Architecture",
                "Sensors",
                "Actuators",
                "IoT Devices",
                "Communication Protocols",
                "Smart Home",
                "IoT Security",
                "IoT Applications"
            ]
        },

        {
            "name": "⚙️ Software Engineering",
            "topics": [
                "Software Development Life Cycle",
                "Waterfall Model",
                "Agile Model",
                "Requirement Analysis",
                "Software Design",
                "Software Testing",
                "Maintenance",
                "Software Documentation"
            ]
        },

        {
            "name": "🔧 Git & GitHub",
            "topics": [
                "Introduction to Git",
                "Git Repository",
                "git init",
                "git add",
                "git commit",
                "git push",
                "git pull",
                "Branches",
                "Merge",
                "GitHub Repository"
            ]
        }
    ]

    return render_template(
"technical.html",
topics=topics
)

# =========================================================
# ADMIN PANEL
# =========================================================

@app.route("/admin")
def admin():

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, name, email
    FROM users
    ORDER BY id DESC
    """)

    users = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
    "admin.html",
    users=users
)
# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print("Database tables are ready.")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
