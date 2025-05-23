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
    database="barangay_system",
    consume_results=True
)
app.secret_key = 'InformationManagementSystem' 

cursor = db.cursor(dictionary=True)  


class User(UserMixin):
    def __init__(self, id, username, password, email=None, role=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.role = role


#initializing login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT * FROM users WHERE userID = %s", (user_id,))
    admin = cursor.fetchone()
    
    if admin:
        return User(
            id=admin['userID'],
            username=admin['username'],
            password=admin['password']
        )
    
    cursor.execute("SELECT * FROM tbl_account WHERE accountID = %s", (user_id,))
    user = cursor.fetchone()
    
    if user:
        return User(
            id=user['accountID'], 
            username=user['username'],
            password=user['password'],
            email=user.get('email'),
            role=user.get('role')
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
    cursor.execute("SELECT * FROM tbl_profile")
    profiles = cursor.fetchall()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        profileID = request.form['profileID']

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
        cursor.execute('INSERT INTO tbl_account (username, email, password, role, profileID) VALUES (%s, %s, %s, %s, %s)', (username, email, hashed_password, role, profileID))
        db.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('register'))

    return render_template('register.html',profiles=profiles, msg=None, success=False)

@app.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user:
            flash('Username is already taken.', 'danger')
            return redirect(url_for('create_admin'))

        hashed_password = generate_password_hash(password)

        cursor.execute('INSERT INTO users (username, password ) VALUES (%s, %s)', (username, hashed_password))
        db.commit()

        flash('Administrator successful created!', 'success')
        return redirect(url_for('create_admin'))

    return render_template('create_admin.html', msg=None, success=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            user_obj = User(id=user['userID'], username=user['username'], password=user['password'])
            login_user(user_obj)
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))
        
        cursor.execute("SELECT * FROM tbl_account WHERE username = %s", (username,)) 
        account = cursor.fetchone()
        if account and check_password_hash(account['password'], password):
            user_obj = User(id=account['accountID'], username=account['username'], password=account['password'], email=account.get('email'), role=account.get('role'))
            login_user(user_obj)
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))

        flash("Invalid credentials.", "danger")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route("/tables")
def tables():
    cursor.execute(" SELECT * FROM tbl_purok ")
    puroks = cursor.fetchall()
    return render_template("home/tables.html",
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
    cursor.execute("SELECT * FROM tbl_household")
    households = cursor.fetchall()

    cursor.execute("SELECT * FROM tbl_profile")
    profiles = cursor.fetchall()

    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        middlename = request.form["middlename"]
        age = request.form["age"]
        bloodtype = request.form["bloodtype"]
        height = request.form["height"]
        weight = request.form["weight"]
        gender = request.form["gender"]
        birthdate = request.form["dateofBirth"]
        birthplace = request.form["placeofBirth"]
        civilStatus = request.form["civilStatus"]
        nationality = request.form["nationality"]
        religion = request.form["religion"]
        educationLevel = request.form["educationLevel"]
        voterStatus = request.form["voterStatus"]
        occupation = request.form["occupation"]
        contactNumber = request.form["contactNumber"]
        email = request.form["email"]
        houseID = request.form["houseID"]

        cursor.execute(
            "INSERT INTO tbl_profile (firstname, lastname, middlename, age, bloodtype, height, weight, gender, birthdate, birthplace, civilStatus, nationality, religion, educationLevel, voterStatus, occupation, contactNumber, email, houseID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (firstname, lastname, middlename, age, bloodtype, height, weight, gender, birthdate, birthplace, civilStatus, nationality, religion, educationLevel, voterStatus, occupation, contactNumber, email, houseID),
        )
        db.commit()
        flash("Added a person successfully")
        return redirect(url_for("addpeople"))

    return render_template("home/addpeople.html", 
                           profiles=profiles, 
                           households=households)

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

@app.route("/purok", methods=["GET", "POST"])
def purok():
    cursor.execute("SELECT * FROM tbl_purok")
    puroks = cursor.fetchall()

    cursor.execute("SELECT * FROM tbl_purok")
    if request.method == "POST":
        purokname = request.form["purokname"]
        
        cursor.execute("INSERT INTO tbl_purok (purokName) VALUES (%s)",(purokname,))
        db.commit()

        flash("Purok Created Successfully!")
        return redirect(url_for("purok"))
    return render_template("home/purok.html", puroks=puroks)

@app.route("/purok_details/<int:id>")
def purok_details(id):
    cursor.execute("SELECT * FROM tbl_purok WHERE purokID = %s", (id,))
    purok = cursor.fetchone()

    cursor.execute("SELECT * FROM tbl_profile WHERE tbl_profile.purokID = %s", (id,))
    profiles = cursor.fetchall()

    return render_template("home/purok_details.html", 
                           profiles=profiles, 
                           purok=purok)

@app.route("/households")
def households():
    cursor.execute("SELECT * FROM tbl_household")
    households = cursor.fetchall()
    return render_template("home/households.html", households=households)

@app.route("/household", methods=["GET", "POST"])
def household():
    cursor.execute("SELECT * FROM tbl_purok")
    puroks = cursor.fetchall()

    cursor.execute("SELECT * FROM tbl_household")
    households = cursor.fetchall()

    cursor.execute("SELECT * FROM tbl_household")
    if request.method == "POST":
        householdname = request.form["houseOwner"]
        purokID = request.form["purokID"]
        block = request.form["block"]
        lot = request.form["lot"]
        
        cursor.execute("INSERT INTO tbl_household (houseOwner, purokID, block, lot) VALUES (%s, %s, %s, %s)",(householdname, purokID, block, lot))
        db.commit()

        flash("Household Created Successfully!")
        return redirect(url_for("household"))

    return render_template("home/household.html",
                           households=households, 
                           puroks=puroks)

@app.route("/settings")
def settings():
    return render_template("home/settings.html")

@app.route("/people-list")
def people_list():
    cursor.execute("SELECT * FROM tbl_profile")
    profiles = cursor.fetchall()
    return render_template("home/people-list.html", profiles=profiles)

@app.route("/search")
def search():
    q = request.args.get("q")

    if q:
        query = """
            SELECT * FROM tbl_purok
            WHERE purokName LIKE %s 
            ORDER BY purokName ASC
            LIMIT 20
        """
        param = (f"%{q}%", f"%{q}%")
        cursor.execute(query, param)
        results = cursor.fetchall()

        cursor.close()

    else:
        results = []

    return render_template("search_results.html", results=results)

@app.route("/assign_account", methods=["GET", "POST"])
def assign_account():
    cursor.execute("SELECT profileID, lastname, firstname, middlename FROM tbl_profile")
    profiles = cursor.fetchall() 

    return render_template("assign_account.html", profiles=profiles)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, port=8080)
