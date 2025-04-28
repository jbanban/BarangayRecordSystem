from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)

#database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="barangayrecordsystem"
)
app.secret_key = 'InformationManagementSystem' 

cursor = db.cursor(dictionary=True)  

DATA = [f"Item {i}" for i in range(1, 51)]  # 50 items

ITEMS_PER_PAGE = 5

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    page = int(request.args.get('page', 1))
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    paginated_data = DATA[start:end]
    total_pages = (len(DATA) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    return jsonify({
        'items': paginated_data,
        'total_pages': total_pages
    })

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
    admin = cursor.fetchone()
    
    if admin:
        return User(
            id=admin['id'],
            username=admin['username'],
            password=admin['password'],
            email=admin['email']
        )
    cursor.execute("SELECT * FROM tbl_profile WHERE accountID = %s", (user_id,))
    user = cursor.fetchone()
    
    if user:
        return User(
            id=user['id'],
            username=user['username'],
            password=user['password'],
            email=user['email'],
            role=user['role']
        )
    
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
        role = request.form['role']

        # Check if username already exists
        cursor.execute('SELECT * FROM tbl_account WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user:
            flash('Username is already taken.', 'danger')
            return redirect(url_for('register'))

        # Check if email already exists
        cursor.execute('SELECT * FROM tbl_account WHERE email = %s', (email,))
        existing_email = cursor.fetchone()

        if existing_email:
            flash('Email is already registered.', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert new user into the database
        cursor.execute('INSERT INTO tbl_account (username, email, password, role) VALUES (%s, %s, %s, %s)', (username, email, hashed_password, role))
        db.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('register'))

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
    cursor.execute("SELECT * FROM tbl_account WHERE accountID = %s", (current_user.id,))
    user_data = cursor.fetchone()

    return render_template("home/profile.html", user=user_data)

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
    cursor.execute("SELECT * FROM tbl_profile, tbl_purok, tbl_household")
    profile = cursor.fetchall()

    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        middlename = request.form["middlename"]
        age = request.form["age"]
        sex = request.form["sex"]
        bloodtype = request.form["bloodtype"]
        height = request.form["height"]
        weight = request.form["weight"]
        gender = request.form["gender"]
        dateofBirth = request.form["dateofBirth"]
        placeofBirth = request.form["placeofBirth"]
        civilStatus = request.form["civilStatus"]
        nationality = request.form["nationality"]
        religion = request.form["religion"]
        educationLevel = request.form["educationLevel"]
        voterStatus = request.form["voterStatus"]
        occupation = request.form["occupation"]
        contactNumber = request.form["contactNumber"]
        email = request.form["email"]

        cursor.execute(
            "INSERT INTO tbl_profile (firstname, lastname, middlename, age, sex, bloodtype, height, weight, gender, dateofBirth, placeofBirth, civilStatus, nationality, religion, educationLevel, voterStatus, occupation, contactNumber, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (firstname, lastname, middlename, age, sex, bloodtype, height, weight, gender, dateofBirth, placeofBirth, civilStatus, nationality, religion, educationLevel, voterStatus, occupation, contactNumber, email),
        )
        db.commit()
        flash("Added a person successfully")
        return redirect(url_for("home"))

    return render_template("home/addpeople.html", profile=profile)

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

@app.route("/update_purok")
def update_purok():
    pass
    return render_template("update_purok.html")

@app.route("/household")
def household():
    cursor.execute("SELECT * FROM tbl_household")
    household = cursor.fetchall()
    return render_template("home/household.html", household=household)

@app.route("/settings")
def settings():
    return render_template("home/settings.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
