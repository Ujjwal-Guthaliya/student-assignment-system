from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "student-assignment-secret-key"

DATABASE = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    conn = get_db_connection()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Assignments table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        description TEXT,
        deadline TEXT NOT NULL,
        priority TEXT DEFAULT 'Medium',
        completed INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
   
    conn.commit()
    conn.close()


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if name and email and password:

            hashed_password = generate_password_hash(password)

            conn = get_db_connection()

            try:

                conn.execute(
                    """
                    INSERT INTO users (name, email, password)
                    VALUES (?, ?, ?)
                    """,
                    (name, email, hashed_password)
                )

                conn.commit()
                conn.close()

                return redirect("/login")

            except sqlite3.IntegrityError:

                conn.close()

                return "Email already registered."

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect("/")

        return "Invalid email or password."

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ---------------- DASHBOARD ----------------

@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    search = request.args.get("search", "")
    status = request.args.get("status", "All")
    priority = request.args.get("priority", "All")

    conn = get_db_connection()

    query = """
        SELECT * FROM assignments
        WHERE user_id = ?
    """

    params = [session["user_id"]]

    # Search
    if search:
        query += """
            AND (title LIKE ? OR subject LIKE ?)
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value
        ])

    # Status filter
    if status == "Pending":
        query += " AND completed = 0"

    elif status == "Completed":
        query += " AND completed = 1"

    # Priority filter
    if priority != "All":
        query += " AND priority = ?"
        params.append(priority)

    query += " ORDER BY deadline"

    assignments = conn.execute(
        query,
        params
    ).fetchall()

    # Statistics
    all_assignments = conn.execute(
        """
        SELECT * FROM assignments
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchall()

    total = len(all_assignments)

    completed = sum(
        1 for assignment in all_assignments
        if assignment["completed"] == 1
    )

    pending = total - completed

    progress = round(
        (completed / total) * 100
    ) if total > 0 else 0

    conn.close()

    return render_template(
        "index.html",
        assignments=assignments,
        user_name=session["user_name"],
        total=total,
        completed=completed,
        pending=pending,
        progress=progress,
        search=search,
        status=status,
        priority=priority
    )


# ---------------- ADD ASSIGNMENT ----------------

@app.route("/add", methods=["POST"])
def add_assignment():

    if "user_id" not in session:
        return redirect("/login")

    title = request.form.get("title")
    subject = request.form.get("subject")
    description = request.form.get("description")
    deadline = request.form.get("deadline")
    priority = request.form.get("priority")
    if title and subject and deadline:

     conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO assignments
        (user_id, title, subject, description, deadline, priority)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            title,
            subject,
            description,
            deadline,
            priority
        )
    )

    conn.commit()
    conn.close()
    return redirect("/")


# ---------------- COMPLETE ----------------

@app.route("/complete/<int:id>")
def complete_assignment(id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE assignments
        SET completed = 1
        WHERE id = ? AND user_id = ?
        """,
        (id, session["user_id"])
    )

    conn.commit()
    conn.close()

    return redirect("/")

# ---------------- EDIT ASSIGNMENT ----------------

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_assignment(id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    assignment = conn.execute(
        """
        SELECT * FROM assignments
        WHERE id = ? AND user_id = ?
        """,
        (id, session["user_id"])
    ).fetchone()

    if assignment is None:
        conn.close()
        return "Assignment not found."

    if request.method == "POST":

        title = request.form.get("title")
        subject = request.form.get("subject")
        description = request.form.get("description")
        deadline = request.form.get("deadline")
        priority = request.form.get("priority")

        conn.execute(
            """
            UPDATE assignments
            SET title = ?,
                subject = ?,
                description = ?,
                deadline = ?,
                priority = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                title,
                subject,
                description,
                deadline,
                priority,
                id,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect("/")

    conn.close()

    return render_template(
        "edit_assignment.html",
        assignment=assignment
    )
# ---------------- DELETE ----------------

@app.route("/delete/<int:id>")
def delete_assignment(id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM assignments
        WHERE id = ? AND user_id = ?
        """,
        (id, session["user_id"])
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":

    create_database()

    app.run(debug=True)