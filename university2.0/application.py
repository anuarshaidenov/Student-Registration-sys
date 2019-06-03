import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from helpers import login_required, apology

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#connect the university database
db = SQL("sqlite:///University.db")

@app.route("/")
def index():
    return render_template("index.html")

#assign courses to instructor
@app.route("/assignteacher", methods=["GET", "POST"])
@login_required
def assignteacher():
        #if the user reached the route via POST
    if request.method == "POST":

        #ensure id was submitted
        if not request.form.get("ID"):
            return apology("must provide id")

        #ensure data was submitted
        elif not request.form.get("course_id"):
            return apology("must provide course id")

        elif not request.form.get("semester"):
            return apology("must provide semester")

        elif not request.form.get("year"):
            return apology("must provide year")

        #insert new user into the table
        result = db.execute("insert into teaches(ID, course_id, semester, year) values(:ID, :course_id, :semester, :year)", ID=request.form.get("ID"), course_id = request.form.get("course_id"), semester = request.form.get("semester"), year = request.form.get("year"))

        return redirect("/admin")

    #if user reached the route via GET
    else:
        positions = []
        rows = db.execute("select course_id from course")
        for row in rows:
            positions.append({"course_id": row['course_id']})
        return render_template("assignteacher.html", positions = positions)


@app.route("/coursesinfo")
@login_required
def coursesinfo():
    """show info about student"""
    rows = db.execute("select c.course_id as course_id, title, dept_name, credits from course c join takes t on c.course_id = t.course_id where t.ID = :ID ", ID = session["user_id"])
    positions = []
    for row in rows:
        positions.append({"course_id": row['course_id'], "title": row['title'], "dept_name": row['dept_name'], "credits": row['credits']})

    return render_template("coursesinfo.html", positions = positions)


@app.route("/studentcourses")
@login_required
def studentcourses():
    """show info about student"""
    rows = db.execute("select course_id, semester, year, grade from takes where ID = :ID", ID = session["user_id"])
    positions = []
    for row in rows:
        positions.append({"course_id": row['course_id'], "semester": row['semester'], "year": row['year'], "grade": row['grade']})

    return render_template("studentcourses.html", positions = positions)

@app.route("/instructorstudent")
@login_required
def instructorstudent():
    """show info about student"""
    rows = db.execute("select student.ID as ID, name, Dept_name, Total_crd from student join (select t.ID, t.course_id from takes t join teaches s on t.course_id = s.course_id where s.ID = :ID) as t on student.ID = t.ID", ID = session["user_id"])
    positions = []
    for row in rows:
        positions.append({"ID": row['ID'], "name": row['name'], "Dept_name": row['Dept_name'], "Total_crd": row['Total_crd']})

    return render_template("instructorstudent.html", positions = positions)


#main page for courseinstructor
@app.route("/coursesinstructor")
@login_required
def coursesinstructor():
    """courses instructor page"""
    rows = db.execute("select t.ID, t.course_id from takes t join teaches s on t.course_id = s.course_id where s.ID = :ID", ID  = session["user_id"])
    positions = []
    for row in rows:
        positions.append({"ID": row['ID'], "course_id": row['course_id']})

    if not rows:
        return render_template("coursesinstructor.html", ID = "null", name = "null")
    else:
        return render_template("coursesinstructor.html", positions = positions)


#main page for instructor
@app.route("/instructor")
@login_required
def instructor():
    """instructor page"""
    rows_for_info = db.execute("SELECT * FROM instructor WHERE ID = :ID", ID  = session["user_id"])
    rows_for_teaching = db.execute("SELECT * FROM teaches WHERE ID = :ID", ID = session["user_id"])
    positions = []
    for row in rows_for_teaching:
        positions.append({"course_id": row['course_id'], "semester": row['semester'], "year":row['year']})

    if not rows_for_teaching:
        return render_template("instructor.html", ID = rows_for_info[0]["ID"], name = rows_for_info[0]["name"], dept_name = rows_for_info[0]["dept_name"], salary = rows_for_info[0]["salary"], course_id = "null", semester = "null", year = "null")
    else:
        return render_template("instructor.html", ID = rows_for_info[0]["ID"], name = rows_for_info[0]["name"], dept_name = rows_for_info[0]["dept_name"], salary = rows_for_info[0]["salary"], positions = positions)


#main page for student
@app.route("/student")
@login_required
def student():
    """show info about student"""
        # Query database for username
    rows = db.execute("SELECT * FROM Student WHERE ID = :ID", ID  = session["user_id"])
    return render_template("student.html", ID = rows[0]["ID"], name = rows[0]["name"], Dept_name = rows[0]["Dept_name"], Total_crd = rows[0]["Total_crd"])



@app.route("/login")
def login():
    session.clear()

    return render_template("login.html")

@app.route("/logininstructor", methods=["GET", "POST"])
def logininstructor():
    """login instructor"""

    #forget any user_id
    session.clear()

    #ensure user entered id
    if request.method == "POST":
        if not request.form.get("ID"):
            return apology("must provide ID")

        #query database for instructor id
        rows = db.execute("SELECT * FROM instructor WHERE ID = :ID", ID = request.form.get("ID"))

        #remember which user logged in
        session["user_id"] = rows[0]["ID"]

        #redirect user to instructor page
        return redirect("/instructor")

    else:
        return render_template("logininstructor.html")




@app.route("/loginstudent", methods=["GET", "POST"])
def loginstudent():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("ID"):
            return apology("must provide ID")

        # Query database for username
        rows = db.execute("SELECT * FROM Student WHERE ID = :ID", ID = request.form.get("ID"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["ID"]

        # Redirect user to home page
        return redirect("/student")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("loginstudent.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():

    #forget any user_id
    session.clear()

    #if the user reached the route via POST
    if request.method == "POST":

        #ensure id was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        #ensure name was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        #ensure dept_name was submitted
        elif not request.form.get("password_confirm"):
            return apology("must provide password(again)")

        elif request.form.get("password") != request.form.get("password_confirm"):
            return apology("passwords must match")

        #insert new user into the table
        result = db.execute("INSERT INTO admin (username, password) VALUES(:username, :password)", username=request.form.get("username"), password = request.form.get("password"))
        if not result:
            return apology("username taken")

        #query database for id
        rows = db.execute("SELECT * FROM admin WHERE username = :username", username = request.form.get("username"))

        #remember which user logged in
        session["user_id"] = rows[0]["ID"]

        return redirect("/login")

    #if user reached the route via GET
    else:
        return render_template("register.html")

@app.route("/loginadmin", methods=["GET", "POST"])
def loginadmin():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must type username")

        elif not request.form.get("password"):
            return apology("must type password")

        # Query database for username
        rows = db.execute("SELECT * FROM admin WHERE username = :username", username = request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["ID"]

        # Redirect user to home page
        return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("loginadmin.html")


@app.route("/admin")
@login_required
def admin():
    """show info about admin"""
        # Query database for username
    rows_student = db.execute("select * from student")
    rows_instructor = db.execute("select * from instructor")
    rows_courses  = db.execute("select * from course")
    positions1 = []
    positions2 = []
    positions3 = []

    for row1 in rows_student:
        positions1.append({"ID": row1['ID'], "name": row1['name'], "Dept_name": row1['Dept_name'], "Total_crd": row1['Total_crd']})

    for row2 in rows_instructor:
        positions2.append({"ID": row2['ID'], "name": row2['name'], "dept_name": row2['dept_name'], "salary": row2['salary']})

    for row3 in rows_courses:
        positions3.append({"course_id": row3['course_id'], "title": row3['title'], "dept_name": row3['dept_name'], "credits": row3['credits']})


    return render_template("admin.html", positions1 = positions1, positions2 = positions2, positions3 = positions3)

@app.route("/newcourse", methods=["GET", "POST"])
@login_required
def newcourse():

    #if the user reached the route via POST
    if request.method == "POST":

        #ensure id was submitted
        if not request.form.get("course_id"):
            return apology("must provide course id")

        #ensure name was submitted
        elif not request.form.get("title"):
            return apology("must provide title")

        elif not request.form.get("dept_name"):
            return apology("must provide department")

        elif not request.form.get("credits"):
            return apology("must provide credits")

        #insert new user into the table
        result = db.execute("insert into course values(:course_id, :title, :dept_name, :credits)", course_id=request.form.get("course_id"), title = request.form.get("title"), dept_name = request.form.get("dept_name"), credits = request.form.get("credits"))

        return redirect("/admin")

    #if user reached the route via GET
    else:
        return render_template("newcourse.html")

@app.route("/newteacher", methods=["GET", "POST"])
@login_required
def newteacher():

    #if the user reached the route via POST
    if request.method == "POST":

        #ensure id was submitted
        if not request.form.get("ID"):
            return apology("must provide id")

        #ensure name was submitted
        elif not request.form.get("name"):
            return apology("must provide name")

        elif not request.form.get("dept_name"):
            return apology("must provide department")

        #insert new user into the table
        result = db.execute("insert into instructor values(:ID, :name, :dept_name, :salary)", ID=request.form.get("ID"), name = request.form.get("name"), dept_name = request.form.get("dept_name"), salary = request.form.get("salary"))

        return redirect("/admin")

    #if user reached the route via GET
    else:
        return render_template("newteacher.html")

@app.route("/newstudent", methods=["GET", "POST"])
@login_required
def newstudent():

    #if the user reached the route via POST
    if request.method == "POST":

        #ensure id was submitted
        if not request.form.get("ID"):
            return apology("must provide id")

        #ensure name was submitted
        elif not request.form.get("name"):
            return apology("must provide name")

        elif not request.form.get("Dept_name"):
            return apology("must provide department")

        #insert new user into the table
        result = db.execute("insert into student values(:ID, :name, :Dept_name, :Total_crd)", ID=request.form.get("ID"), name = request.form.get("name"), Dept_name = request.form.get("Dept_name"), Total_crd = request.form.get("Total_crd"))

        return redirect("/admin")

    #if user reached the route via GET
    else:
        return render_template("newstudent.html")

@app.route("/assignstd", methods=["GET", "POST"])
@login_required
def assignstd():

    #if the user reached the route via POST
    if request.method == "POST":

        #ensure id was submitted
        if not request.form.get("ID"):
            return apology("must provide id")

        #ensure name was submitted
        elif not request.form.get("course_id"):
            return apology("must provide course id")

        elif not request.form.get("semester"):
            return apology("must provide semester")

        elif not request.form.get("year"):
            return apology("must provide year")

        #insert new user into the table
        result = db.execute("insert into takes(ID, course_id, semester, year, grade) values(:ID, :course_id, :semester, :year, :grade)", ID=request.form.get("ID"), course_id = request.form.get("course_id"), semester = request.form.get("semester"), year = request.form.get("year"), grade = request.form.get("grade"))

        return redirect("/admin")

    #if user reached the route via GET
    else:
        positions = []
        rows = db.execute("select course_id from course")
        for row in rows:
            positions.append({"course_id": row['course_id']})
        return render_template("assignstd.html", positions = positions)



