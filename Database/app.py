from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import uuid
import os

from flask import Flask
app = Flask(__name__)

app.secret_key = "cmms_secret_key"

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# UPLOAD FOLDER
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
UPLOAD_FOLDER = "uploads"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# MYSQL CONFIGURATION
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cmms_db'

mysql = MySQL(app)

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# PRIORITY DETECTOR
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
def detect_priority(description):

    text = description.lower()

    critical = [
        "fire",
        "smoke",
        "explosion",
        "electrical",
        "live wire",
        "short circuit",
        "gas leak",
        "collapsed",
        "collapse",
        "flood",
        "emergency",
        "sparking",
        "exposed wire"
    ]

    high = [
        "broken door",
        "broken window",
        "aircon",
        "air conditioner",
        "projector",
        "computer",
        "internet",
        "network",
        "no power",
        "water leak",
        "leaking ceiling"
    ]

    medium = [
        "leak",
        "light",
        "bulb",
        "fan",
        "chair",
        "desk",
        "lock",
        "toilet",
        "sink",
        "faucet"
    ]

    for word in critical:
        if word in text:
            return "Critical"

    for word in high:
        if word in text:
            return "High"

    for word in medium:
        if word in text:
            return "Medium"

    return "Low"

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# HOME PAGE
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/')
def home():
    return render_template('login.html')

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# LOGIN
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM users
        WHERE email=%s
        AND password=%s
    """, (email, password))

    user = cur.fetchone()

    cur.close()

    if user:

        session['user_id'] = user[0]
        session['fullname'] = user[1]
        session['role'] = user[4]

        # ROLE REDIRECTION
        if session['role'] == "admin":
            return redirect('/admin/dashboard')

        elif session['role'] == "maintenance":
            return redirect('/maintenance/dashboard')

        else:
            return redirect('/dashboard')

    return "Invalid Email or Password"

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# STUDENT DASHBOARD
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM tickets
        WHERE reporter_id=%s
        ORDER BY id DESC
    """, (session['user_id'],))

    tickets = cur.fetchall()

    cur.close()

    return render_template(
        'dashboard.html',
        tickets=tickets,
        fullname=session['fullname']
    )

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# ADMIN DASHBOARD
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/admin/dashboard')
def admin_dashboard():

    if 'user_id' not in session:
        return redirect('/')

    if session['role'] != "admin":
        return "Access Denied"

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM tickets
        ORDER BY id DESC
    """)

    tickets = cur.fetchall()

    cur.close()

    return render_template(
        'admin_dashboard.html',
        tickets=tickets,
        fullname=session['fullname']
    )

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# MAINTENANCE DASHBOARD
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/maintenance/dashboard')
def maintenance_dashboard():

    if 'user_id' not in session:
        return redirect('/')

    if session['role'] != "maintenance":
        return "Access Denied"

    cur = mysql.connection.cursor()

    cur.execute("""

        SELECT *

        FROM tickets

        WHERE status != 'Completed'

        ORDER BY

        FIELD(priority,'Critical','High','Medium','Low'),

        id DESC

    """)

    tickets = cur.fetchall()

    cur.close()

    return render_template(
        "maintenance_dashboard.html",
        tickets=tickets,
        fullname=session['fullname']
    )

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# MAINTENANCE TICKET 
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/maintenance/ticket/<int:id>')
def maintenance_view_ticket(id):

    if 'user_id' not in session:
        return redirect('/')

    if session['role'] != "maintenance":
        return "Access Denied"

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM tickets WHERE id=%s",
        (id,)
    )

    ticket = cur.fetchone()

    cur.close()

    if ticket is None:
        return "Ticket not found"

    return render_template(
        "maintenance_ticket.html",
        ticket=ticket
    )

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# SUBMIT TICKET PAGE
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/submit_ticket')
def submit_ticket():

    if 'user_id' not in session:
        return redirect('/')

    return render_template('submit_ticket.html')

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# SAVE TICKET
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/save_ticket', methods=['POST'])
def save_ticket():

    if 'user_id' not in session:
        return redirect('/')

    category = request.form['category']
    location = request.form['location']
    description = request.form['description']
    priority = detect_priority(description)

    filename = ""

    photo = request.files.get('photo')

    if photo and photo.filename != "":

        extension = os.path.splitext(photo.filename)[1]
        filename = f"{uuid.uuid4().hex}{extension}"

        photo.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )
        )

    cur = mysql.connection.cursor()

    # Insert first with a temporary ticket number
    cur.execute("""

        INSERT INTO tickets
        (
            ticket_no,
            reporter_id,
            category,
            location,
            description,
            priority,
            status,
            photo
        )

        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s)

    """, (

        "",                     # Temporary ticket number
        session['user_id'],
        category,
        location,
        description,
        priority,
        "Pending",
        filename

    ))

    # Get the auto-generated ticket ID
    ticket_id = cur.lastrowid

    # Create a unique ticket number
    ticket_no = f"TCK-{ticket_id:05d}"

    # Update the ticket with the generated ticket number
    cur.execute("""

        UPDATE tickets

        SET ticket_no=%s

        WHERE id=%s

    """, (

        ticket_no,
        ticket_id

    ))

    mysql.connection.commit()

    cur.close()

    return redirect('/dashboard')

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# LOGOUT
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# VIEW UPLOADED IMAGE
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/uploads/<filename>')
def uploaded_file(filename):

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# EDIT TICKET PAGE
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/edit_ticket/<int:id>')
def edit_ticket(id):

    if 'user_id' not in session:
        return redirect('/')

    if session['role'] != "admin":
        return "Access Denied"

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM tickets WHERE id=%s",
        (id,)
    )

    ticket = cur.fetchone()

    cur.close()

    if ticket is None:
        return "Ticket not found"

    return render_template(
        "edit_ticket.html",
        ticket=ticket
    )

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# UPDATE TICKET
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/update_ticket/<int:id>', methods=['POST'])
def update_ticket(id):

    if 'user_id' not in session:
        return redirect('/')

    if session['role'] != "admin":
        return "Access Denied"

    category = request.form['category']
    location = request.form['location']
    description = request.form['description']
    priority = request.form['priority']
    status = request.form['status']

    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE tickets
        SET
            category=%s,
            location=%s,
            description=%s,
            priority=%s,
            status=%s
        WHERE id=%s
    """, (
        category,
        location,
        description,
        priority,
        status,
        id
    ))

    mysql.connection.commit()
    cur.close()

    return redirect('/admin/dashboard')
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# VIEW TICKET
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/view_ticket/<int:id>')
def view_ticket(id):

    if 'user_id' not in session:
        return redirect('/')

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM tickets
        WHERE id=%s
    """, (id,))

    ticket = cur.fetchone()

    cur.execute("""
    SELECT
        stage,
        note,
        photo,
        created_at
    FROM progress_updates
    WHERE ticket_id=%s
    ORDER BY created_at ASC
""", (id,))

    updates = cur.fetchall()

    cur.close()

    if ticket is None:
        return "Ticket not found"

    return render_template(
        "view_ticket.html",
        ticket=ticket,
        updates=updates
    )
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# DELETE TICKET
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/delete_ticket/<int:id>')
def delete_ticket(id):

    if 'user_id' not in session:
        return redirect('/')

    if session['role'] != "admin":
        return "Access Denied"

    cur = mysql.connection.cursor()

    # Check if the ticket exists and is completed
    cur.execute("""
        SELECT status
        FROM tickets
        WHERE id=%s
    """, (id,))

    ticket = cur.fetchone()

    if ticket is None:
        cur.close()
        return "Ticket not found"

    if ticket[0] != "Completed":
        cur.close()
        return "Only completed tickets can be deleted."

    # Delete the ticket
    cur.execute("""
        DELETE FROM tickets
        WHERE id=%s
    """, (id,))

    mysql.connection.commit()

    cur.close()

    return redirect('/admin/dashboard')

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# RESGISTER
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/register')
def register():

    return render_template("register.html")

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# RESGISTER USSER
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/register_user', methods=['POST'])
def register_user():

    fullname = request.form['fullname']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    cur = mysql.connection.cursor()

    # Check if email already exists
    cur.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    existing = cur.fetchone()

    if existing:
        cur.close()
        return "Email already registered."

    cur.execute("""

        INSERT INTO users
        (
            fullname,
            email,
            password,
            role
        )

        VALUES
        (%s,%s,%s,%s)

    """, (

        fullname,
        email,
        password,
        role

    ))

    mysql.connection.commit()

    cur.close()

    return redirect('/')

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# FORGOT PASSWORD
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/forgot_password')
def forgot_password():
    return render_template("forgot_password.html")

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# RESET PASSWORD
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/reset_password', methods=['POST'])
def reset_password():

    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirm_password']

    if password != confirm:
        return "Passwords do not match."

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    user = cur.fetchone()

    if user is None:

        cur.close()

        return "Email not found."

    cur.execute("""

        UPDATE users

        SET password=%s

        WHERE email=%s

    """,(

        password,
        email

    ))

    mysql.connection.commit()

    cur.close()

    return redirect("/")

# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# MAINTENANCE ADD PROGRESS
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
@app.route('/maintenance/add_progress/<int:id>', methods=['POST'])
def maintenance_add_progress(id):

    if 'user_id' not in session:
        return redirect('/')

    if session['role'] != "maintenance":
        return "Access Denied"

    stage = request.form['stage']
    note = request.form['note']

    filename = ""

    photo = request.files.get('photo')

    if photo and photo.filename != "":

        extension = os.path.splitext(photo.filename)[1]
        filename = f"{uuid.uuid4().hex}{extension}"

        photo.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )
        )

    cur = mysql.connection.cursor()

    # Save the progress update
    cur.execute("""
        INSERT INTO progress_updates
        (
            ticket_id,
            maintenance_id,
            stage,
            note,
            photo
        )
        VALUES
        (%s,%s,%s,%s,%s)
    """, (
        id,
        session['user_id'],
        stage,
        note,
        filename
    ))

    # Determine the ticket status
    if stage == "Completed":
        status = "Completed"
    else:
        status = "In Progress"

    # Update the main ticket
    cur.execute("""
        UPDATE tickets
        SET
            maintenance_note=%s,
            status=%s,
            started_at=IF(started_at IS NULL, NOW(), started_at)
        WHERE id=%s
    """, (
        note,
        status,
        id
    ))

    # Save completion time
    if stage == "Completed":

        cur.execute("""
            UPDATE tickets
            SET completed_at=NOW()
            WHERE id=%s
        """, (id,))

    mysql.connection.commit()

    cur.close()

    return redirect(f"/maintenance/ticket/{id}")
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
# RUN APP
# MAKOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONUT
if __name__ == '__main__':
    app.run(debug=True)
