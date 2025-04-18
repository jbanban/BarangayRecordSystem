from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
Bootstrap5(app)

#database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="barangayrecordsystem"
)
app.secret_key = 'InformationManagementSystem' 

cursor = db.cursor(dictionary=True)  

class User(UserMixin):
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email


#initializing login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#fething user from datebase
@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user['id'], username=user['username'], password=user['password'], email=user['email'])
    return None


@app.route('/')
@login_required
def home():
    cursor.execute("SELECT * FROM tbl_profile")
    profiles = cursor.fetchall()
    return render_template('home/home.html', profiles=profiles, user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username already exists
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user:
            flash('Username is already taken.', 'danger')
            return redirect(url_for('register'))

        # Check if email already exists
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        existing_email = cursor.fetchone()

        if existing_email:
            flash('Email is already registered.', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert new user into the database
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, hashed_password))
        db.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', msg=None, success=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            user_obj = User(id=user['id'], username=user['username'], password=user['password'], email=user['email'])
            login_user(user_obj)
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))

        flash("Invalid credentials.", "danger")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route("/table")
def table():
    cursor.execute("SELECT * FROM tbl_profile, tbl_purok, tbl_household")
    profiles = cursor.fetchall()
    cursor.execute("""
                    SELECT tbl_purok.purokID FROM tbl_purok 
                    INNER JOIN tbl_population ON tbl_purok.purokID = tbl_population.purokID
                    INNER JOIN tbl_profile ON tbl_population.populationID = tbl_profile.populationID
                    """)
    puroks = cursor.fetchall()
    return render_template("home/tables.html",
                           profiles=profiles,
                           puroks=puroks)

@app.route("/view/<int:id>")
def view_profile(id):
    cursor.execute("SELECT * FROM profiles WHERE id = %s", (id,))
    profile = cursor.fetchone()
    return render_template("profile.html", profile=profile)

@app.route("/profile")
@login_required
def profile():
    cursor.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
    user_data = cursor.fetchone()

    return render_template("profile.html", user=user_data)

@app.route("/update_account/<int:id>", methods=["GET", "POST"])
def update_account(id):
    cursor.execute("SELECT * FROM profiles WHERE id = %s", (id,))
    profile = cursor.fetchone()

    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        
        cursor.execute(
            "UPDATE profiles SET firstname = %s, lastname = %s WHERE id = %s",
            (firstname, lastname, id),
        )
        db.commit()
        flash(f"{profile['username']} edited successfully")
        return redirect(url_for("home"))

    return render_template("update.html", profile=profile)

@app.route("/delete_account/<int:id>")
def delete_account(id):
    cursor.execute("DELETE FROM profiles WHERE id = %s", (id,))
    db.commit()
    flash("Deleted successfully")
    return redirect(url_for("home"))

@app.route("/addpeople", methods=["GET", "POST"])
def addpeople():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        age = request.form["age"]
        gender = request.form["gender"]
        purok = request.form["purok"]
        barangay = request.form["barangay"]
        city = request.form["city"]
        province = request.form["province"]
        contact = request.form["contact"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "INSERT INTO profiles (firstname, lastname, age, gender, purok, barangay, city, province, contact, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (firstname, lastname, age, gender, purok, barangay, city, province, contact, email, password),
        )
        db.commit()
        flash("Added a person successfully")
        return redirect(url_for("home"))

    return render_template("home/addpeople.html")

@app.route("/create_post/<int:id>", methods=["GET", "POST"])
def create_post(id):
    cursor.execute("SELECT * FROM profiles WHERE id = %s", (id,))
    profile = cursor.fetchone()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        
        cursor.execute(
            "INSERT INTO posts (title, content, profile_id) VALUES (%s, %s, %s)",
            (title, content, id),
        )
        db.commit()
        flash("Created a post successfully")
        return redirect(url_for("home"))

    return render_template("create_post.html", profile=profile)

@app.route("/view_all_post")
def view_all_post():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return render_template("all_posts.html", posts=posts)

@app.route("/view_post/<int:id>")
def view_post(id):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    post = cursor.fetchone()
    return render_template("view_post.html", post=post)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
