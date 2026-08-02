from flask import Flask, render_template, request, redirect, session, url_for, sessions, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "your_secret_key"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Student(db.Model):   
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    homeroom_teacher = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    student_number = db.Column(db.String(20), unique=True, nullable=False)



@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("register"))
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register/backend", methods=["POST"])
def register_backend():
    username = request.form.get("username")
    password = request.form.get("password")

    newuser = User(username=username, password=password)
    db.session.add(newuser)
    db.session.commit()

    return redirect(url_for("login"))    

@app.route("/login/backend", methods=["POST"])
def login_backend():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        session["username"] = username
        return redirect(url_for("dashboard"))
    else:
        return "Invalid credentials"


@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"], student=Student.query.all())

@app.route("/search", methods=["POST"])
def search():
    student_id = request.form["student_id"]
    student = Student.query.filter_by(student_number=student_id).first()
    if student:
        return render_template("dashboard.html", username=session["username"], student=student, searched_id=student_id)
    return "Student not found", 404

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    email = request.form["email"]
    grade = request.form["grade"]
    homeroom_teacher = request.form["homeroom_teacher"]
    student_number = request.form["student_number"]   
    is_active = request.form["is_active"] == "true"

    new_student = Student(
        name=name,
        email=email,
        grade=grade,
        homeroom_teacher=homeroom_teacher,
        student_number=student_number,
        is_active=is_active
    )
    db.session.add(new_student)
    db.session.commit()

    return redirect(url_for("dashboard"))

@app.route("/students")
def view_students():
    if "username" in session:
        students = Student.query.all()
        data = [
            {"name": s.name, "id": s.id, "student_number": s.student_number}
            for s in students
        ]
        return jsonify(data), 200
    return jsonify([]), 404

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404



@app.route("/remove", methods=["POST"])
def remove():
    student_number = request.form["student_number"]
    student = Student.query.filter_by(student_number=student_number).first()
    if student:
        db.session.delete(student)
        db.session.commit()
        return "Student removed successfully"

    return "Student not found", 404

@app.route("/updateuser")
def update_user():
    if "username" in session:
        return render_template("updateuser.html", username=session["username"])
    else:
        return redirect(url_for("login"))
    
@app.route("/update", methods=["POST"])
def update():
    student_number_updating = request.form["student_number_updating"]
    student = Student.query.filter_by(student_number=student_number_updating).first()
    if student:
        student.name = request.form["name"]
        student.email = request.form["email"]
        student.grade = request.form["grade"]
        student.homeroom_teacher = request.form["homeroom_teacher"]
        student.is_active = request.form["is_active"] == "true"
        db.session.commit()
        return "Student updated successfully"

    return "Student not found", 404



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)