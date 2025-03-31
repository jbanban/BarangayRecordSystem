from flask import Flask, render_template, url_for, redirect, request, flash
from flask_bootstrap import Bootstrap5
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="barangayrecordsystem"
)

cursor = db.cursor(dictionary=True)  
app.config["SECRET_KEY"] = ""

bootstrap = Bootstrap5(app)
@app.route("/home")
def home():
    cursor.execute("SELECT * FROM profiles")
    profiles = cursor.fetchall()
    return render_template("home.html", profiles=profiles)

@app.route("/view/<int:id>")
def view_profile(id):
    cursor.execute("SELECT * FROM profiles WHERE id = %s", (id,))
    profile = cursor.fetchone()
    return render_template("profile.html", profile=profile)

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        username = request.form["username"]
        password = request.form["password"]
        
        # Insert new profile
        cursor.execute(
            "INSERT INTO profiles (firstname, lastname, username, password) VALUES (%s, %s, %s, %s)",
            (firstname, lastname, username, password),
        )
        db.commit()
        flash(f"{username} added successfully")
        return redirect(url_for("home"))

    return render_template("create.html")

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



if __name__ == "__main__":
    app.run(debug=True)
