import os
import re
import json
import string
import secrets
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from database import mysql_connector, retrive_tables
from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect

# --------------------------------------------------------------------------#

INDEX_HTML = r"index.html"
SQL_SELECT_USERNAME = "select UserName from users where id = %s"
SQL_SELECT_DOCTOR_NAME = "select FName, MidName, LName from doctors where id = %s"
SQL_SELECT_TREATMENT_NAME = "select Name from treatments where id = %s"
REGEX_ALPHA = r"[A-Za-z]+"

"""Functions"""


# Generate random password
def get_random_number():
    length = secrets.choice(range(8, 11))
    numbers = string.digits
    result_str = "".join(secrets.choice(numbers) for _ in range(length))
    return result_str


# --------------------------------------------------------------------------#
# Connecting with Database
mydb = None
mycursor = None


def init_db():
    global mydb, mycursor
    if mydb is None or mycursor is None:
        mydb, mycursor = mysql_connector()
        if mydb is None:
            raise RuntimeError("Database connection failed")
    return mydb, mycursor


# --------------------------------------------------------------------------#
"""The Website"""
app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key = os.getenv("SECRET_KEY", "orthosecure")

# Initilize contact us information
app.config.update(
    {
        "MAIL_SERVER": "smtp.googlemail.com",
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME": "contact@orthosecure.com",
        "MAIL_PASSWORD": "orthosecure",
    }
)
mail = Mail(app)

# --------------------------------------------------------------------------#


""" Routes of Pages """


# Home Page
# CSRF protection is enabled globally via Flask-WTF's CSRFProtect
@app.route("/", methods=["GET", "POST"])
def home_page():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    # Identify site's information
    session["title"] = db_tables["site_information"][0]
    session["address"] = db_tables["site_information"][1]
    session["email"] = db_tables["site_information"][2]
    session["phone"] = db_tables["site_information"][3]
    session["short"] = db_tables["site_information"][4]
    session["long"] = db_tables["site_information"][5]

    rates_list = []
    for rate in db_tables["rates"]:
        rate = list(rate)
        mycursor.execute("SELECT * FROM users where id=%s", (rate[2],))
        rate[2] = mycursor.fetchall()[0][1]
        rates_list.append(rate)

    message = ""
    # If login
    if request.method == "POST":

        doctor = request.form.get("doctor")
        email = request.form["email"]
        password = request.form["password"]

        if doctor == "on":
            # If doctor
            mycursor.execute(
                "SELECT * FROM doctors WHERE Email = %s AND password = %s",
                (
                    email,
                    password,
                ),
            )
            doctor = mycursor.fetchone()

            if doctor:
                # If info of doctor is right
                session["loggedin"] = True
                session["id"] = doctor[0]
                session["ssn"] = doctor[1]
                session["username"] = doctor[8]
                session["doctor"] = True

                return redirect(url_for("profile_page"))

            else:
                # If info is Wrong
                message = "Incorrect email or password !"
                return render_template(
                    INDEX_HTML,
                    titlePage="Homepage",
                    ActiveHome="active",
                    msg=message,
                    TreatData=db_tables["treatments"],
                    sliderImg=db_tables["slider"],
                    RatesTable=rates_list,
                    users=db_tables["users"],
                )
        else:
            # If normal user
            mycursor.execute(
                "SELECT * FROM users WHERE email = %s AND password = %s",
                (
                    email,
                    password,
                ),
            )
            user = mycursor.fetchone()
            if user:
                session["loggedin"] = True
                session["id"] = user[0]
                session["username"] = user[5]
                session["doctor"] = False

                return redirect(url_for("profile_page"))

            else:
                message = "Incorrect email or password !"
                return render_template(
                    INDEX_HTML,
                    titlePage="Homepage",
                    ActiveHome="active",
                    msg=message,
                    TreatData=db_tables["treatments"],
                    sliderImg=db_tables["slider"],
                    RatesTable=rates_list,
                    users=db_tables["users"],
                )

    else:
        return render_template(
            INDEX_HTML,
            titlePage="Homepage",
            ActiveHome="active",
            msg=message,
            TreatData=db_tables["treatments"],
            sliderImg=db_tables["slider"],
            RatesTable=rates_list,
            users=db_tables["users"],
        )


# About Us
@app.route("/About")
def about_us_page():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    # Retrieve all information about app
    return render_template(
        "about.html",
        titlePage="About Us",
        ActiveAbout="active",
        users=db_tables["users"],
    )


# Doctors
@app.route("/Doctors")
def doctors_page():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    return render_template(
        "doctors.html",
        titlePage="Our Dentists",
        ActiveDoctors="active",
        DoctorsData=db_tables["doctors"],
    )


# Appointments
# CSRF protection is enabled globally via Flask-WTF's CSRFProtect
@app.route("/Appointment", methods=["GET", "POST"])
def appointment():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    message = ""
    tcost = 0
    pass_or_not = "text-danger"  # nosec

    if request.method == "POST":
        ssn = request.form["SSN"]
        f_name = request.form["FName"]
        mid_name = request.form["MidName"]
        l_name = request.form["LName"]
        age = request.form["Age"]
        gender = request.form["Gender"]
        user_id = session["id"]
        doctor = request.form["Doctor"]
        doctor_name = doctor.split()
        service = request.form["Service"]

        # Display Cost
        mycursor.execute("SELECT cost FROM treatments where Name = %s", (service,))
        tcost = mycursor.fetchone()

        mycursor.execute(
            "SELECT Id FROM doctors where FName = %s and MidName = %s and LName = %s",
            (doctor_name[0], doctor_name[1], doctor_name[2]),
        )
        d_id = mycursor.fetchone()

        mycursor.execute("SELECT id FROM treatments where Name = %s", (service,))
        service_id = mycursor.fetchone()

        mycursor.execute(
            "INSERT INTO appointments(SSN, FName, MidName, LName, Age, Gender,  Status  , userId, DoctorID, ServiceID ) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s)",
            (
                ssn,
                f_name,
                mid_name,
                l_name,
                age,
                gender,
                "Waiting",
                user_id,
                d_id[0],
                service_id[0],
            ),
        )
        mydb.commit()
        message = "You have successfully booked an appointment!"
        pass_or_not = "text-success"  # nosec

    return render_template(
        "appointment.html",
        titlePage="Book an appointment",
        DoctorsData=db_tables["doctors"],
        TreatData=db_tables["treatments"],
        cost=tcost,
        msg=message,
        PassOrNot=pass_or_not,
    )


# Register
# CSRF protection is enabled globally via Flask-WTF's CSRFProtect
@app.route("/register", methods=["GET", "POST"])
def register():
    # retrive all tables
    _, mycursor = init_db()
    retrive_tables(mycursor)

    message = ""
    pass_or_not = "text-danger"  # nosec
    if request.method == "POST":
        f_name = request.form["FName"]
        mid_name = request.form["MidName"]
        l_name = request.form["LName"]
        image = request.files["file"]
        username = request.form["username"]
        password = request.form["password"]
        repassword = request.form["repassword"]
        email = request.form["email"]
        phone = request.form["Phone"]

        mycursor.execute("SELECT * FROM users WHERE UserName = %s", (username,))
        new_user = mycursor.fetchone()

        mycursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
        new_email = mycursor.fetchone()

        mycursor.execute("SELECT * FROM users WHERE Phone = %s", (phone,))
        new_phone = mycursor.fetchone()

        if new_user:
            message = "Username already exists !"
        elif new_email:
            message = "Email already exists !"
        elif new_phone:
            message = "Phone already exists !"
        elif not re.match(r"[A-Za-z0-9]+", username):
            message = "Username must contain only characters and numbers !"
        elif repassword != password:
            message = "Please Enter the same password !"
        elif len(password) < 5:
            message = "Weak Password !"
        else:

            if image.filename == "":
                path = ""
            else:
                path = "static/img/UsersProfile/" + secure_filename(image.filename)
                image.save(path)

            mycursor.execute(
                "INSERT INTO users(FName, MidName, LName, Image, UserName, Password, Email, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (f_name, mid_name, l_name, path, username, password, email, phone),
            )
            mydb.commit()
            message = "Congratulation !! You have successfully registered."
            pass_or_not = "text-success"  # nosec

    return render_template(
        "register.html",
        titlePage="Sign Up",
        msg=message,
        registered=pass_or_not,
        hidden="d-none",
    )


# Profile
@app.route("/profile", methods=["GET"])
def profile_page():
    _, mycursor = init_db()
    retrive_tables(mycursor)

    appointments_list = []
    appointments_list_json = []
    user_info = None
    if session["username"]:
        if session["doctor"]:
            user_info, appointments_list, appointments_list_json = (
                get_doctor_appointments(mycursor, session)
            )
        else:
            user_info, appointments_list = get_user_appointments(mycursor, session)
    return render_template(
        "profile.html",
        titlePage=session["username"],
        Info=user_info,
        AppointmentsTable=appointments_list,
        AppointmentsListJson=json.dumps(appointments_list_json),
    )


# Contact Us
# CSRF protection is enabled globally via Flask-WTF's CSRFProtect
@app.route("/Contact", methods=["GET", "POST"])
def contact_us():
    _, mycursor = init_db()
    db_tables = retrive_tables(mycursor)
    message = ""

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        try:
            msg = Message(
                subject=subject,
                sender=email,
                recipients=[db_tables["site_information"][2]],
            )
            msg.body = f"From: {email}\n{name} says:\n{message}"
            mail.send(msg)
            message = "Thanks for the message!!"
        except Exception as e:
            message = f"An error occurred while sending the email: {str(e)}"
            # Log the error for debugging (optional)
            app.logger.error(f"Email sending failed: {str(e)}")

    return render_template(
        "contact.html", titlePage="Contact Us", ActiveContact="active", msg=message
    )


# Rate Us
# CSRF protection is enabled globally via Flask-WTF's CSRFProtect
@app.route("/Rate", methods=["GET", "POST"])
def rate_us():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    message = ""
    pass_or_not = "text-danger"  # nosec

    if request.method == "POST":
        rating = request.form["rating"]
        message = request.form["message"]
        user_id = session["id"]

        mycursor.execute(
            "INSERT INTO rates(rating, Review, UserID) VALUES (%s, %s, %s)",
            (rating, message, user_id),
        )
        mydb.commit()

        message = "Thanks for you!"
        pass_or_not = "text-success"  # nosec

    return render_template(
        "rate.html",
        titlePage="Rate Us",
        RateData=db_tables["rates"],
        msg=message,
        PassOrNot=pass_or_not,
    )


# Logout
@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    session.pop("doctor", None)

    return redirect(url_for("home_page"))


# --------------------------------------------------------------------------#

"""Admin Control Panal"""


# Admin Page
@app.route("/Admin/Home")
def admin():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    # Check if Admin is loggedin
    if "loggedinAdmin" in session:

        """Statistical Analysis"""
        # Average of ratings
        rates = [rate[0] for rate in db_tables["rates"]]
        if len(rates) == 0:
            avg_of_rates = 0
        else:
            avg_of_rates = sum(rates) / len(rates)
        print("Im Here")
        # Statistical Analysis Appointments
        mycursor.execute("SELECT Count(id) FROM appointments")
        num_of_app = mycursor.fetchall()[0][0]

        mycursor.execute('SELECT Count(id) FROM appointments where Status="Scheduled"')
        num_of_app_succ = mycursor.fetchall()[0][0]

        mycursor.execute('SELECT Count(id) FROM appointments where Status="Accepted"')
        num_of_app_acc = mycursor.fetchall()[0][0]

        mycursor.execute('SELECT Count(id) FROM appointments where Status="Refused"')
        num_of_app_ref = mycursor.fetchall()[0][0]

        appointments_list = [
            num_of_app,
            num_of_app_succ,
            num_of_app_acc,
            num_of_app_ref,
        ]
        if num_of_app == 0:
            appointments_list_percentage = [0, 0, 0]
        else:
            appointments_list_percentage = [
                num_of_app_succ / num_of_app,
                num_of_app_acc / num_of_app,
                num_of_app_ref / num_of_app,
            ]

        # Statistical Analysis Doctors
        mycursor.execute("SELECT Count(id) FROM doctors")
        num_of_doctors = mycursor.fetchall()[0][0]

        mycursor.execute("SELECT Count(id) FROM doctors where Age>=20 and Age<30")
        num_of_doctors_20 = mycursor.fetchall()[0][0]

        mycursor.execute("SELECT Count(id) FROM doctors where Age>=30 and Age<40")
        num_of_doctors_30 = mycursor.fetchall()[0][0]

        mycursor.execute("SELECT Count(id) FROM doctors where Age>=40 and Age<50")
        num_of_doctors_40 = mycursor.fetchall()[0][0]

        mycursor.execute("SELECT Count(id) FROM doctors where Age>=50")
        num_of_doctors_50 = mycursor.fetchall()[0][0]

        doctors_list = [
            num_of_doctors,
            num_of_doctors_20,
            num_of_doctors_30,
            num_of_doctors_40,
            num_of_doctors_50,
        ]
        if num_of_doctors == 0:
            doctors_list_percentage = [0, 0, 0, 0]
        else:
            doctors_list_percentage = [
                num_of_doctors_20 / num_of_doctors,
                num_of_doctors_30 / num_of_doctors,
                num_of_doctors_40 / num_of_doctors,
                num_of_doctors_50 / num_of_doctors,
            ]

        # Statistical Analysis Services
        mycursor.execute(
            "select ServiceID, COUNT(id) from appointments group by ServiceID order by ServiceID"
        )
        services_list_items = mycursor.fetchall()

        services_dict = {}
        for service in services_list_items:
            mycursor.execute("select Name from treatments where id = %s", (service[0],))
            services_dict[mycursor.fetchall()[0][0]] = service[1]

        colors = [
            "color-brown",
            "color-black",
            "color-blue",
            "color-green",
            "color-yellow",
            "color-orange",
            "color-red",
        ]

        # Admin is loggedin show them the home page
        return render_template(
            "Admin/home.html",
            titlePage="Admin Control Panel",
            AvgOfRates=avg_of_rates,
            AppointmentsList=appointments_list,
            AppointmentsListPrecentage=appointments_list_percentage,
            DoctorsList=doctors_list,
            DoctorsListPrecentage=doctors_list_percentage,
            ServicesDict=services_dict,
            colors=colors,
        )

    # Admin is not loggedin redirect to login page
    return redirect(url_for("login"))


# CSRF protection is enabled globally via Flask-WTF's CSRFProtect
@app.route("/Admin/", methods=["GET", "POST"])
def login():
    _, mycursor = init_db()
    # retrive all tables
    retrive_tables(mycursor)

    if "loggedinAdmin" in session:
        return redirect(url_for("admin"))
    else:
        # Output message if something goes wrong...
        msg = ""
        # Check if "username" and "password" POST requests exist (user submitted form)
        if request.method == "POST":
            # Create variables for easy access
            username = request.form["username"]
            password = request.form["password"]

            # Check if account exists using MySQL
            mycursor.execute(
                "SELECT * FROM admin WHERE UserName = %s AND Password = %s",
                (
                    username,
                    password,
                ),
            )

            # Fetch one record and return result
            account = mycursor.fetchone()

            # If account exists in accounts table in out database
            if account:
                # Create session data, we can access this data in other routes
                session["loggedinAdmin"] = True
                session["idAdmin"] = account[0]
                session["usernameAdmin"] = account[1]
                # Redirect to home page
                return redirect(url_for("admin"))
            else:
                # Account doesnt exist or username/password incorrect
                msg = "Incorrect username/password!"
        # Show the login form with message (if any)
        return render_template(
            r"Admin/index.html",
            msg=msg,
            titlePage="Admin Control Panel",
            hide="d-none",
            login=True,
        )


@app.route("/Admin/logout")
def logout_admin():
    # Remove session data, this will log the user out
    session.pop("loggedinAdmin", None)
    session.pop("idAdmin", None)
    session.pop("usernameAdmin", None)
    # Redirect to login page
    return redirect(url_for("login"))


def validate_doctor_form(request, mycursor):
    ssn = request.form["SSN"]
    file = request.files["file"]
    f_name = request.form["FName"]
    mid_name = request.form["MidName"]
    l_name = request.form["LName"]
    phone = request.form["Phone"]
    gender = request.form["Gender"]
    email = request.form["Email"]
    age = request.form["Age"]
    degree = request.form["Degree"]
    password = get_random_number()
    mycursor.execute("SELECT * FROM doctors WHERE SSN = %s", (ssn,))
    d_ssn = mycursor.fetchone()
    mycursor.execute("SELECT * FROM doctors WHERE Email = %s", (email,))
    email_add = mycursor.fetchone()
    if d_ssn:
        return False, "SSN already exists !", None
    elif email_add:
        return False, "Email already exists !", None
    elif not re.match(REGEX_ALPHA, f_name):
        return False, "First Name must contain only characters", None
    elif not re.match(REGEX_ALPHA, mid_name):
        return False, "Name must contain only characters", None
    elif not re.match(REGEX_ALPHA, l_name):
        return False, "Last Name must contain only characters", None
    return (
        True,
        "",
        {
            "ssn": ssn,
            "file": file,
            "f_name": f_name,
            "mid_name": mid_name,
            "l_name": l_name,
            "phone": phone,
            "gender": gender,
            "email": email,
            "age": age,
            "degree": degree,
            "password": password,
        },
    )


def create_doctor(mycursor, doctor_data):
    file = doctor_data["file"]
    if file.filename == "":
        path = ""
    else:
        path = "static/img/doctorsProfile/" + secure_filename(file.filename)
        file.save(path)
    mycursor.execute(
        "INSERT INTO doctors(SSN, FName, MidName, LName, Age, Gender, Phone, Email, Degree, Password, Image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            doctor_data["ssn"],
            doctor_data["f_name"],
            doctor_data["mid_name"],
            doctor_data["l_name"],
            doctor_data["age"],
            doctor_data["gender"],
            doctor_data["phone"],
            doctor_data["email"],
            doctor_data["degree"],
            doctor_data["password"],
            path,
        ),
    )
    mydb.commit()


@app.route("/Admin/Doctors", methods=["GET", "POST"])
def doctors():
    _, mycursor = init_db()
    db_tables = retrive_tables(mycursor)
    if "loggedinAdmin" in session:
        msg = ""
        pass_or_not = "text-danger"  # nosec
        if request.method == "POST":
            valid, msg, doctor_data = validate_doctor_form(request, mycursor)
            if valid:
                create_doctor(mycursor, doctor_data)
                msg = "You have successfully Added Doctor."
                pass_or_not = "text-success"  # nosec
        return render_template(
            "Admin/doctors.html",
            registered=pass_or_not,
            msg=msg,
            DoctorsData=db_tables["doctors"],
            titlePage="Doctors Control Panel",
        )
    return redirect(url_for("login"))


# CSRF protection is enabled globally via Flask-WTF's CSRFProtect
@app.route("/Admin/General", methods=["GET", "POST"])
def general_admin():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    if "loggedinAdmin" in session:
        msg = ""
        if request.method == "POST":
            title = request.form["title"]
            address = request.form["address"]
            email = request.form["email"]
            phone = request.form["phone"]
            short = request.form["short"]
            long = request.form["long"]
            icon = request.files["icon"]

            if icon.filename == "":
                path = ""
            else:
                path = "static/img/icon/icon.png"
                icon.save(path)

            mycursor.execute(
                "UPDATE site_information SET Title=%s, Address=%s, Email=%s, Phone=%s, Short_description=%s, Long_description=%s, Icon=%s",
                (title, address, email, phone, short, long, path),
            )
            mydb.commit()
            msg = "Updated successfully, please restart the app to update the changes."

        return render_template(
            "Admin/general.html",
            msg=msg,
            titlePage="Site Informtion Control Panel",
            siteinfo=db_tables["site_information"],
        )

    return redirect(url_for("login"))


# CSRF protection is enabled globally via Flask-WTF's CSRFProtect
@app.route("/Admin/slider", methods=["GET", "POST"])
def slider_admin():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    if "loggedinAdmin" in session:
        msg = ""
        if request.method == "POST":
            file = request.files["file"]
            title = request.form["title"]
            description = request.form["description"]

            if file.filename == "":
                path = ""
            else:
                path = "static/img/slider/" + secure_filename(file.filename)
                file.save(path)

            mycursor.execute(
                "INSERT INTO slider(Image, Title, Description) VALUES (%s, %s, %s)",
                (path, title, description),
            )
            mydb.commit()

            msg = "Image Uploaded successfully"

        return render_template(
            "Admin/slider.html",
            msg=msg,
            titlePage="Slider Control Panel",
            sliderImg=db_tables["slider"],
        )

    return redirect(url_for("login"))


@app.route("/Admin/users", methods=["GET"])
def users_admin():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    if "loggedinAdmin" in session:
        return render_template(
            "Admin/users.html", titlePage="Users", users=db_tables["users"]
        )

    return redirect(url_for("login"))


# CSRF protection is enabled globally via Flask-WTF's CSRFProtect
@app.route("/Admin/Services", methods=["GET", "POST"])
def services_admin():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    # Check if user is loggedin
    if "loggedinAdmin" in session:
        msg = ""
        pass_or_not = "text-danger"  # nosec
        if request.method == "POST":
            name = request.form["Name"]
            image = request.files["file"]
            cost = request.form["Cost"]
            duration = request.form["Duration"]
            description = request.form["Description"]

            if image.filename == "":
                path = ""
            else:
                path = "static/img/ServicesProfile/" + secure_filename(image.filename)
                image.save(path)

            mycursor.execute(
                "INSERT INTO treatments(Image, Name, cost, Duration, Description) VALUES (%s, %s, %s, %s, %s)",
                (path, name, cost, duration, description),
            )
            mydb.commit()

            msg = "You Have Successfully Added New Service/Treatment."
            pass_or_not = "text-success"  # nosec

        # User is loggedin show them the home page
        return render_template(
            "Admin/services.html",
            titlePage="Doctors Control Panel",
            registered=pass_or_not,
            msg=msg,
            servicesData=db_tables["treatments"],
        )

    # User is not loggedin redirect to login page
    return redirect(url_for("login"))


# CSRF protection is enabled globally via Flask-WTF's CSRFProtect
@app.route("/Admin/Appointemnts", methods=["GET", "POST"])
def appointments_admin():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    if request.method == "POST":
        appointment_id = request.form["id"]
        if request.form["status"] == "Confirm":
            mycursor.execute(
                'UPDATE appointments set Status="Scheduled" WHERE id = %s',
                (appointment_id,),
            )
        elif request.form["status"] == "Reject":
            mycursor.execute(
                'UPDATE appointments set Status="Refused" WHERE id = %s',
                (appointment_id,),
            )

        mydb.commit()

    appointments_list = [
        enrich_appointment(appointment, mycursor)
        for appointment in db_tables["appointments"]
    ]

    return render_template(
        "Admin/appointments.html",
        titlePage="Appointments Control Panel",
        AppointmentsTable=appointments_list,
    )


@app.route("/Admin/Admins", methods=["GET", "POST"])
def admins():
    _, mycursor = init_db()
    # retrive all tables
    db_tables = retrive_tables(mycursor)

    if "loggedinAdmin" in session:
        msg = ""
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            mycursor.execute(
                "INSERT INTO admin(Username, Password) VALUES (%s, %s)",
                (username, password),
            )
            mydb.commit()

            msg = "Addded successfully"

        return render_template(
            "Admin/admins.html",
            msg=msg,
            titlePage="Admins Table Control Panel",
            Admins=db_tables["admin"],
        )
    else:
        return render_template(
            "Admin/admins.html",
            msg="",
            titlePage="Admins Table Control Panel",
            Admins=db_tables["admin"],
        )


# --------------------------------------------------------------------------#


def enrich_appointment(appointment, mycursor):
    appointment = list(appointment)
    mycursor.execute(SQL_SELECT_USERNAME, (appointment[9],))
    appointment[9] = mycursor.fetchall()[0][0]
    mycursor.execute(SQL_SELECT_DOCTOR_NAME, (appointment[10],))
    d_name = mycursor.fetchall()[0]
    appointment[10] = f"{d_name[0]} {d_name[1]} {d_name[2]}"
    mycursor.execute(SQL_SELECT_TREATMENT_NAME, (appointment[11],))
    appointment[11] = mycursor.fetchall()[0][0]
    return appointment


def get_doctor_appointments(mycursor, session):
    mycursor.execute("select * from appointments where DoctorId = %s", (session["id"],))
    appointments_table = mycursor.fetchall()
    mycursor.execute("SELECT * FROM doctors WHERE Email = %s", (session["username"],))
    user_info = mycursor.fetchone()
    appointments_list = []
    appointments_list_json = []
    for appointment in appointments_table:
        enriched = enrich_appointment(appointment, mycursor)
        appointments_list.append(enriched)
        if enriched[8] == "Scheduled":
            enriched[7] = str(enriched[7])
            appointments_list_json.append(enriched)
    return user_info, appointments_list, appointments_list_json


def get_user_appointments(mycursor, session):
    if request.method == "POST":
        appointment_id = request.form["id"]
        if request.form["status"] == "Confirm":
            mycursor.execute(
                'UPDATE appointments set Status="Scheduled" WHERE id = %s',
                (appointment_id,),
            )
        elif request.form["status"] == "Reject":
            mycursor.execute(
                'UPDATE appointments set Status="Refused" WHERE id = %s',
                (appointment_id,),
            )
        mydb.commit()
    mycursor.execute("select * from appointments where UserID = %s", (session["id"],))
    appointments_table = mycursor.fetchall()
    mycursor.execute("SELECT * FROM users WHERE Username = %s", (session["username"],))
    user_info = mycursor.fetchone()
    appointments_list = [
        enrich_appointment(appointment, mycursor) for appointment in appointments_table
    ]
    return user_info, appointments_list


# Run the Website
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=50001)
