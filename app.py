from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import uuid

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.secret_key = "student-assignment-secret-key"

DATABASE = "database.db"

UPLOAD_FOLDER = os.path.join("static", "uploads")

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# CREATE DATABASE
# =========================================================

def create_database():

    conn = get_db_connection()

    # -----------------------------------------------------
    # USERS TABLE
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            dob TEXT,

            institute TEXT,

            course TEXT,

            branch TEXT,

            avatar TEXT

        )
    """)

    # -----------------------------------------------------
    # ADD NEW COLUMNS TO EXISTING DATABASE
    # -----------------------------------------------------

    existing_columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(users)"
        ).fetchall()
    ]

    new_columns = {

        "dob": "TEXT",

        "institute": "TEXT",

        "course": "TEXT",

        "branch": "TEXT",

        "avatar": "TEXT"

    }

    for column, column_type in new_columns.items():

        if column not in existing_columns:

            conn.execute(
                f"ALTER TABLE users ADD COLUMN {column} {column_type}"
            )

    # -----------------------------------------------------
    # ASSIGNMENTS TABLE
    # -----------------------------------------------------

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

            FOREIGN KEY (user_id)
            REFERENCES users(id)

        )
    """)

    conn.commit()

    conn.close()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def is_logged_in():

    return "user_id" in session


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# HOME / DASHBOARD
# =========================================================

@app.route("/")
def index():

    if not is_logged_in():

        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()

    # -----------------------------------------------------
    # SEARCH / FILTER VALUES
    # -----------------------------------------------------

    search = request.args.get(
        "search",
        ""
    ).strip()

    status = request.args.get(
        "status",
        "All"
    )

    priority = request.args.get(
        "priority",
        "All"
    )

    # -----------------------------------------------------
    # ASSIGNMENT QUERY
    # -----------------------------------------------------

    query = """
        SELECT *
        FROM assignments
        WHERE user_id = ?
    """

    params = [user_id]

    # SEARCH

    if search:

        query += """
            AND (
                title LIKE ?
                OR subject LIKE ?
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value
        ])

    # STATUS FILTER

    if status == "Completed":

        query += """
            AND completed = 1
        """

    elif status == "Pending":

        query += """
            AND completed = 0
        """

    # PRIORITY FILTER

    if priority in ["High", "Medium", "Low"]:

        query += """
            AND priority = ?
        """

        params.append(priority)

    # SORT

    query += """
        ORDER BY
            completed ASC,
            deadline ASC
    """

    assignments = conn.execute(
        query,
        params
    ).fetchall()

    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

    total = conn.execute(
        """
        SELECT COUNT(*)
        FROM assignments
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()[0]

    completed = conn.execute(
        """
        SELECT COUNT(*)
        FROM assignments
        WHERE user_id = ?
        AND completed = 1
        """,
        (user_id,)
    ).fetchone()[0]

    pending = total - completed

    if total > 0:

        progress = round(
            (completed / total) * 100
        )

    else:

        progress = 0

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    return render_template(

        "index.html",

        assignments=assignments,

        total=total,

        completed=completed,

        pending=pending,

        progress=progress,

        search=search,

        status=status,

        priority=priority,

        user_name=user["name"],

        user=user

    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not name or not email or not password:

            return "All fields are required."

        if len(password) < 6:

            return "Password must contain at least 6 characters."

        conn = get_db_connection()

        existing_user = conn.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:

            conn.close()

            return "Email is already registered."

        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------

        hashed_password = generate_password_hash(
            password
        )

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        conn.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                hashed_password
            )
        )

        conn.commit()

        conn.close()

        return redirect("/login")

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db_connection()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        conn.close()

        # -------------------------------------------------
        # CHECK LOGIN
        # -------------------------------------------------

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            return redirect("/")

        return "Invalid email or password."

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# ADD ASSIGNMENT
# =========================================================

@app.route(
    "/add",
    methods=["POST"]
)
def add_assignment():

    if not is_logged_in():

        return redirect("/login")

    title = request.form.get(
        "title",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    deadline = request.form.get(
        "deadline",
        ""
    )

    priority = request.form.get(
        "priority",
        "Medium"
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not title or not subject or not deadline:

        return "Title, subject and deadline are required."

    if priority not in [
        "Low",
        "Medium",
        "High"
    ]:

        priority = "Medium"

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO assignments
        (
            user_id,
            title,
            subject,
            description,
            deadline,
            priority,
            completed
        )
        VALUES (?, ?, ?, ?, ?, ?, 0)
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


# =========================================================
# COMPLETE ASSIGNMENT
# =========================================================

@app.route(
    "/complete/<int:assignment_id>"
)
def complete_assignment(
    assignment_id
):

    if not is_logged_in():

        return redirect("/login")

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE assignments

        SET completed = 1

        WHERE id = ?

        AND user_id = ?
        """,
        (
            assignment_id,
            session["user_id"]
        )
    )

    conn.commit()

    conn.close()

    return redirect("/")


# =========================================================
# DELETE ASSIGNMENT
# =========================================================

@app.route(
    "/delete/<int:assignment_id>"
)
def delete_assignment(
    assignment_id
):

    if not is_logged_in():

        return redirect("/login")

    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM assignments

        WHERE id = ?

        AND user_id = ?
        """,
        (
            assignment_id,
            session["user_id"]
        )
    )

    conn.commit()

    conn.close()

    return redirect("/")


# =========================================================
# EDIT ASSIGNMENT
# =========================================================

@app.route(
    "/edit/<int:assignment_id>",
    methods=["GET", "POST"]
)
def edit_assignment(
    assignment_id
):

    if not is_logged_in():

        return redirect("/login")

    conn = get_db_connection()

    # -----------------------------------------------------
    # GET ASSIGNMENT
    # -----------------------------------------------------

    assignment = conn.execute(
        """
        SELECT *
        FROM assignments

        WHERE id = ?

        AND user_id = ?
        """,
        (
            assignment_id,
            session["user_id"]
        )
    ).fetchone()

    if not assignment:

        conn.close()

        return "Assignment not found."

    # -----------------------------------------------------
    # UPDATE ASSIGNMENT
    # -----------------------------------------------------

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        deadline = request.form.get(
            "deadline",
            ""
        )

        priority = request.form.get(
            "priority",
            "Medium"
        )

        completed = request.form.get(
            "completed"
        )

        if completed in [
            "1",
            "true",
            "True",
            "on"
        ]:

            completed_value = 1

        else:

            completed_value = 0

        if priority not in [
            "Low",
            "Medium",
            "High"
        ]:

            priority = "Medium"

        conn.execute(
            """
            UPDATE assignments

            SET title = ?,
                subject = ?,
                description = ?,
                deadline = ?,
                priority = ?,
                completed = ?

            WHERE id = ?

            AND user_id = ?
            """,
            (
                title,
                subject,
                description,
                deadline,
                priority,
                completed_value,
                assignment_id,
                session["user_id"]
            )
        )

        conn.commit()

        conn.close()

        return redirect("/")

    conn.close()

    return render_template("edit_assignment.html", assignment=assignment)


# =========================================================
# PROFILE
# =========================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if not is_logged_in():

        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    if not user:

        conn.close()

        session.clear()

        return redirect("/login")

    # -----------------------------------------------------
    # UPDATE PROFILE
    # -----------------------------------------------------

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        dob = request.form.get(
            "dob",
            ""
        ).strip()

        institute = request.form.get(
            "institute",
            ""
        ).strip()

        course = request.form.get(
            "course",
            ""
        ).strip()

        branch = request.form.get(
            "branch",
            ""
        ).strip()

        new_password = request.form.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # BASIC VALIDATION
        # -------------------------------------------------

        if not name or not email:

            conn.close()

            return "Name and email are required."

        # -------------------------------------------------
        # CHECK EMAIL
        # -------------------------------------------------

        email_user = conn.execute(
            """
            SELECT id
            FROM users

            WHERE email = ?

            AND id != ?
            """,
            (
                email,
                user_id
            )
        ).fetchone()

        if email_user:

            conn.close()

            return "This email is already registered."

        # -------------------------------------------------
        # EXISTING AVATAR
        # -------------------------------------------------

        avatar = user["avatar"]

        # -------------------------------------------------
        # PROFILE PHOTO
        # -------------------------------------------------

        avatar_file = request.files.get(
            "avatar"
        )

        if (
            avatar_file
            and avatar_file.filename
        ):

            if not allowed_file(
                avatar_file.filename
            ):

                conn.close()

                return "Invalid image format."

            extension = (
                avatar_file
                .filename
                .rsplit(".", 1)[1]
                .lower()
            )

            filename = (
                str(uuid.uuid4())
                + "."
                + secure_filename(extension)
            )

            avatar_path = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            avatar_file.save(
                avatar_path
            )

            # Delete old profile image

            if avatar:

                old_avatar_path = os.path.join(
                    UPLOAD_FOLDER,
                    avatar
                )

                if os.path.exists(
                    old_avatar_path
                ):

                    try:

                        os.remove(
                            old_avatar_path
                        )

                    except OSError:

                        pass

            avatar = filename

        # -------------------------------------------------
        # PASSWORD UPDATE
        # -------------------------------------------------

        if new_password:

            if len(new_password) < 6:

                conn.close()

                return (
                    "New password must contain "
                    "at least 6 characters."
                )

            hashed_password = generate_password_hash(
                new_password
            )

            conn.execute(
                """
                UPDATE users

                SET
                    name = ?,
                    email = ?,
                    dob = ?,
                    institute = ?,
                    course = ?,
                    branch = ?,
                    password = ?,
                    avatar = ?

                WHERE id = ?
                """,
                (
                    name,
                    email,
                    dob,
                    institute,
                    course,
                    branch,
                    hashed_password,
                    avatar,
                    user_id
                )
            )

        else:

            conn.execute(
                """
                UPDATE users

                SET
                    name = ?,
                    email = ?,
                    dob = ?,
                    institute = ?,
                    course = ?,
                    branch = ?,
                    avatar = ?

                WHERE id = ?
                """,
                (
                    name,
                    email,
                    dob,
                    institute,
                    course,
                    branch,
                    avatar,
                    user_id
                )
            )

        conn.commit()

        conn.close()

        # -------------------------------------------------
        # UPDATE SESSION
        # -------------------------------------------------

        session["user_name"] = name

        return redirect("/profile")

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    create_database()

    app.run(host="0.0.0.0", port=5000, debug=True)