import os
import re
import json
import string
import random
from pathlib import Path
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from database import mysql_connector, retrive_tables
from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_wtf.csrf import CSRFProtect
#--------------------------------------------------------------------------#

"""Functions"""
# Generate random password
def get_random_number():
    length = random.randint(8,10)
    # choose from all lowercase letter
    numbers = string.digits
    result_str = ''.join(random.choice(numbers) for i in range(length))
    return result_str

#--------------------------------------------------------------------------#
# Connecting with Database
mydb, mycursor = mysql_connector()

"""Retrive Database Tables"""
db_tables = retrive_tables(mycursor)

#--------------------------------------------------------------------------#
"""The Website"""
app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key = os.getenv('SECRET_KEY')

# Initilize contact us information
app.config.update(dict(
    MAIL_SERVER = 'smtp.googlemail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'contact@orthosecure.com',
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
))
mail = Mail(app)

#--------------------------------------------------------------------------#

  
""" Routes of Pages """
  
# Home Page
@app.route("/", methods =['GET'])
def HomePage():

  # retrive all tables
  db_tables = retrive_tables(mycursor)

  # Identify site's information
  session['title'] = db_tables["site_information"][0]
  session['address'] = db_tables["site_information"][1]
  session['email'] = db_tables["site_information"][2]
  session['phone'] = db_tables["site_information"][3]
  session['short'] = db_tables["site_information"][4]
  session['long'] = db_tables["site_information"][5]


  RatesList = []
  for rate in db_tables["rates"] :
    rate = list(rate)
    mycursor.execute("SELECT * FROM users where id=%s",(rate[2],))
    rate[2] = mycursor.fetchall()[0][1]
    RatesList.append(rate)

  msg = ""
  # If login
  if request.method == 'POST' :
    
    doctor = request.form.get('doctor')
    email = request.form['email']
    password = request.form['password']

    if doctor == 'on' :
      # If doctor
      mycursor.execute('SELECT * FROM doctors WHERE Email = %s AND password = %s', (email, password, ))
      doctor = mycursor.fetchone()
      
      if doctor:
        # If info of doctor is right
          session['loggedin'] = True
          session['id'] = doctor[0]
          session['ssn'] = doctor[1]
          session['username'] = doctor[8]
          session['doctor'] = True
          msg = 'Logged in successfully !'
          
          return redirect(url_for('ProfilePage'))

      else:
        # If info is Wrong
          msg = 'Incorrect email or password !'
          return render_template(r'index.html',
                          titlePage="Homepage", 
                          ActiveHome="active", 
                          msg = msg, 
                          TreatData=db_tables["treatments"],
                          sliderImg=db_tables["slider"],
                          RatesTable=RatesList,
                          users=db_tables["users"])
    else :
      # If normal user
      mycursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password, ))
      user = mycursor.fetchone()
      if user:
                session['loggedin'] = True
                session['id'] = user[0]
                session['username'] = user[5]
                session['doctor'] = False

                msg = 'Logged in successfully !'
                return redirect(url_for('ProfilePage'))

      else:
          msg = 'Incorrect email or password !'
          return render_template(r"index.html",
                          titlePage="Homepage", 
                          ActiveHome="active", 
                          msg = msg, 
                          TreatData=db_tables["treatments"],
                          sliderImg=db_tables["slider"],
                          RatesTable=RatesList,
                          users=db_tables["users"])

  else:
    return render_template(r'index.html',
                        titlePage="Homepage", 
                        ActiveHome="active", 
                        msg = msg, 
                        TreatData=db_tables["treatments"],
                        sliderImg=db_tables["slider"],
                        RatesTable=RatesList,
                        users=db_tables["users"])


# About Us
@app.route("/About")
def AboutUsPage():
  # retrive all tables
  db_tables = retrive_tables(mycursor)

  # Retrieve all information about app
  return render_template("about.html", 
                          titlePage="About Us", 
                          ActiveAbout="active",
                          users=db_tables["users"])

# Doctors
@app.route("/Doctors")
def DoctorsPage():
  # retrive all tables
  db_tables = retrive_tables(mycursor)

  return render_template("doctors.html", 
                          titlePage="Our Dentists", 
                          ActiveDoctors="active",
                          DoctorsData=db_tables["doctors"])

# Appointments
@app.route("/Appointment", methods=['GET'])
def Appointment():
    # retrive all tables
    db_tables = retrive_tables(mycursor)
  
    msg = ""
    Tcost = 0
    PassOrNot = "text-danger"

    if request.method == 'POST' :
        SSN = request.form['SSN']
        FName = request.form['FName']
        MidName = request.form['MidName']
        LName = request.form['LName']
        Age = request.form['Age']
        Gender = request.form['Gender']
        userId = session['id']
        Doctor = request.form['Doctor']
        DoctorName = Doctor.split()
        Service = request.form['Service']
        

        # Display Cost
        mycursor.execute('SELECT cost FROM treatments where Name = %s',(Service,))
        Tcost = mycursor.fetchone()

        mycursor.execute('SELECT Id FROM doctors where FName = %s and MidName = %s and LName = %s',(DoctorName[0],DoctorName[1],DoctorName[2]))
        D_Id = mycursor.fetchone()

        mycursor.execute('SELECT id FROM treatments where Name = %s',(Service,))
        ServiceId = mycursor.fetchone()
        
        mycursor.execute("INSERT INTO appointments(SSN, FName, MidName, LName, Age, Gender,  Status  , userId, DoctorID, ServiceID ) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s)", 
                                                  (SSN, FName, MidName, LName, Age, Gender, "Waiting", userId, D_Id[0] , ServiceId[0] ))
        mydb.commit()
        msg = 'You have successfully booked an appointment!'
        PassOrNot = "text-success"
    
    return render_template("appointment.html", 
                          titlePage="Book an appointment", 
                          DoctorsData=db_tables["doctors"], 
                          TreatData=db_tables["treatments"],
                          cost=Tcost,
                          msg=msg,
                          PassOrNot=PassOrNot)

# Register
@app.route('/register', methods =['GET'])
def register():
    # retrive all tables
    db_tables = retrive_tables(mycursor)
  
    msg = ''
    PassOrNot = "text-danger"
    if request.method == 'POST' :
        FName = request.form['FName']
        MidName = request.form['MidName']
        LName = request.form['LName']
        Image = request.files["file"]
        username = request.form['username']
        password = request.form['password']
        repassword = request.form['repassword']
        email = request.form['email']
        phone = request.form['Phone']

        mycursor.execute('SELECT * FROM users WHERE UserName = %s', (username, ))
        NewUser = mycursor.fetchone()
        
        mycursor.execute('SELECT * FROM users WHERE Email = %s', (email, ))
        NewEmail = mycursor.fetchone()

        mycursor.execute('SELECT * FROM users WHERE Phone = %s', (phone, ))
        NewPhone = mycursor.fetchone()
        
        if NewUser:
            msg = 'Username already exists !'
        elif NewEmail :
            msg = 'Email already exists !'
        elif NewPhone :
            msg = 'Phone already exists !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not repassword == password :
            msg = 'Please Enter the same password !'
        elif len(password) < 5 :
            msg = 'Weak Password !'
        else:

            if Image.filename == '':
              path = ""
            else :
              path = "static/img/UsersProfile/" + secure_filename(Image.filename)
              Image.save(path)

            mycursor.execute("INSERT INTO users(FName, MidName, LName, Image, UserName, Password, Email, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                                               (FName, MidName, LName, path, username, password, email, phone))
            mydb.commit()
            msg = 'Congratulation !! You have successfully registered.'
            PassOrNot = "text-success"

    return render_template('register.html', 
                            titlePage="Sign Up",
                            msg=msg,
                            registered=PassOrNot, 
                            hidden="d-none")

# Profile
@app.route("/profile", methods =['GET'])
def ProfilePage():
  # retrive all tables
  db_tables = retrive_tables(mycursor)

  AppointmentsList = []
  AppointmentsListJson = []
  if session['username']:
    if session['doctor'] :
      # If doctor
      mycursor.execute("select * from appointments where DoctorId = %s",(session['id'],))
      AppointmentsTable = mycursor.fetchall()

      mycursor.execute('SELECT * FROM doctors WHERE Email = %s', (session['username'], ))
      UserInfo = mycursor.fetchone()

      for Appointment in AppointmentsTable :
        Appointment = list(Appointment)
        mycursor.execute("select UserName from users where id = %s",(Appointment[9],))
        App_UserName = mycursor.fetchall()[0][0]
        Appointment[9] = App_UserName

        mycursor.execute("select FName, MidName, LName from doctors where id = %s",(Appointment[10],))
        App_DName = mycursor.fetchall()[0]
        Appointment[10] = App_DName[0]  + " " + App_DName[1] + " " + App_DName[2]  

        mycursor.execute("select Name from treatments where id = %s",(Appointment[11],))
        TreatName = mycursor.fetchall()[0][0]
        Appointment[11] = TreatName
        
        AppointmentsList.append(Appointment)
        if Appointment[8] == "Scheduled" :
          Appointment[7] = str(Appointment[7])
          AppointmentsListJson.append(Appointment)

    else:
      # If normal user
      if request.method == 'POST' :
        id = request.form['id']
        if request.form['status'] == 'Confirm':
          mycursor.execute('UPDATE appointments set Status="Scheduled" WHERE id = %s', (id, ))
        elif request.form['status'] == 'Reject':
          mycursor.execute('UPDATE appointments set Status="Refused" WHERE id = %s', (id, ))
      
        mydb.commit()
      
      mycursor.execute("select * from appointments where UserID = %s",(session['id'],))
      AppointmentsTable = mycursor.fetchall()

      mycursor.execute('SELECT * FROM users WHERE Username = %s', (session['username'], ))
      UserInfo = mycursor.fetchone()

      for Appointment in AppointmentsTable :
        Appointment = list(Appointment)
        mycursor.execute("select UserName from users where id = %s",(Appointment[9],))
        App_UserName = mycursor.fetchall()[0][0]
        Appointment[9] = App_UserName

        mycursor.execute("select FName, MidName, LName from doctors where id = %s",(Appointment[10],))
        App_DName = mycursor.fetchall()[0]
        Appointment[10] = App_DName[0]  + " " + App_DName[1] + " " + App_DName[2]  

        mycursor.execute("select Name from treatments where id = %s",(Appointment[11],))
        TreatName = mycursor.fetchall()[0][0]
        Appointment[11] = TreatName
        
        AppointmentsList.append(Appointment)

  return render_template("profile.html",
                        titlePage=session['username'],
                        Info=UserInfo,
                        AppointmentsTable=AppointmentsList,
                        AppointmentsListJson=json.dumps(AppointmentsListJson))

# Contact Us
@app.route("/Contact", methods=['GET'])
def ContactUs():
    db_tables = retrive_tables(mycursor) 
    msg = ""

    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        try:
            msg = Message(subject=subject, sender=email, recipients=[db_tables["site_information"][2]])
            msg.body = f"From: {email}\n{name} says:\n{message}" 
            mail.send(msg)
            msg = "Thanks for the message!!" 
        except Exception as e: 
            msg = f"An error occurred while sending the email: {str(e)}" 
            # Log the error for debugging (optional)
            app.logger.error(f"Email sending failed: {str(e)}") 

    return render_template("contact.html", 
                            titlePage="Contact Us", 
                            ActiveContact="active",
                            msg=msg)
  
# Rate Us
@app.route("/Rate", methods=['GET'])
def RateUs():
    # retrive all tables
    db_tables = retrive_tables(mycursor)
  
    msg = ""
    PassOrNot = "text-danger"

    if request.method == 'POST' :
        rating = request.form['rating']
        message = request.form['message']
        userId = session['id']
        
        mycursor.execute("INSERT INTO rates(rating, Review, UserID) VALUES (%s, %s, %s)", 
                                           (rating, message, userId))
        mydb.commit()

        msg = 'Thanks for you!'
        PassOrNot = "text-success"
    
    return render_template("rate.html", 
                          titlePage="Rate Us", 
                          RateData=db_tables["rates"],
                          msg=msg, 
                          PassOrNot=PassOrNot)

# Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('doctor', None)

    return redirect(url_for('HomePage'))

#--------------------------------------------------------------------------#

"""Admin Control Panal"""
# Admin Page
@app.route('/Admin/Home')
def Admin():
    # retrive all tables
    db_tables = retrive_tables(mycursor)
  
    # Check if Admin is loggedin
    if 'loggedinAdmin' in session:

      """ Statistical Analysis """
      # Average of ratings
      Rates = [rate[0] for rate in db_tables["rates"]]
      if len(Rates) == 0 :
        AvgOfRates = 0
      else :
        AvgOfRates = sum(Rates)/len(Rates)
      print("Im Here")
      # Statistical Analysis Appointments
      mycursor.execute('SELECT Count(id) FROM appointments')
      numOfApp = mycursor.fetchall()[0][0]
      
      mycursor.execute('SELECT Count(id) FROM appointments where Status="Scheduled"')
      numOfAppSucc = mycursor.fetchall()[0][0]
      
      mycursor.execute('SELECT Count(id) FROM appointments where Status="Accepted"')
      numOfAppAcc = mycursor.fetchall()[0][0]

      mycursor.execute('SELECT Count(id) FROM appointments where Status="Refused"')
      numOfAppRef = mycursor.fetchall()[0][0]

      AppointmentsList = [numOfApp,numOfAppSucc,numOfAppAcc,numOfAppRef]
      if numOfApp == 0 :
        AppointmentsListPrecentage = [0,0,0]
      else :
        AppointmentsListPrecentage = [numOfAppSucc/numOfApp,numOfAppAcc/numOfApp,numOfAppRef/numOfApp]
      
      # Statistical Analysis Doctors
      mycursor.execute('SELECT Count(id) FROM doctors')
      numOfDoctors = mycursor.fetchall()[0][0]

      mycursor.execute('SELECT Count(id) FROM doctors where Age>=20 and Age<30')
      numOfDoctors20 = mycursor.fetchall()[0][0]

      mycursor.execute('SELECT Count(id) FROM doctors where Age>=30 and Age<40')
      numOfDoctors30 = mycursor.fetchall()[0][0]

      mycursor.execute('SELECT Count(id) FROM doctors where Age>=40 and Age<50')
      numOfDoctors40 = mycursor.fetchall()[0][0]

      mycursor.execute('SELECT Count(id) FROM doctors where Age>=50')
      numOfDoctors50 = mycursor.fetchall()[0][0]

      DoctorsList = [numOfDoctors, numOfDoctors20, numOfDoctors30, numOfDoctors40, numOfDoctors50]
      if numOfDoctors == 0 :
        DoctorsListPrecentage = [0, 0, 0, 0]
      else :
        DoctorsListPrecentage = [numOfDoctors20/numOfDoctors, numOfDoctors30/numOfDoctors, numOfDoctors40/numOfDoctors, numOfDoctors50/numOfDoctors]

      # Statistical Analysis Services
      mycursor.execute('select ServiceID, COUNT(id) from appointments group by ServiceID order by ServiceID')
      ServicesListItems = mycursor.fetchall()

      ServicesDict = dict()
      for service in ServicesListItems:
        mycursor.execute('select Name from treatments where id = %s', (service[0],))
        ServicesDict[mycursor.fetchall()[0][0]] = service[1]

      colors = ["color-brown","color-black","color-blue","color-green","color-yellow","color-orange","color-red"]
      
      # Admin is loggedin show them the home page  
      return render_template('Admin/home.html',
                            titlePage="Admin Control Panel",
                            AvgOfRates=AvgOfRates,
                            AppointmentsList=AppointmentsList,
                            AppointmentsListPrecentage=AppointmentsListPrecentage,
                            DoctorsList=DoctorsList,
                            DoctorsListPrecentage=DoctorsListPrecentage,
                            ServicesDict=ServicesDict,
                            colors=colors)

    # Admin is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/Admin/', methods=['GET'])
def login():
  # retrive all tables
  db_tables = retrive_tables(mycursor)

  if 'loggedinAdmin' in session:
    return redirect(url_for('Admin'))
  else :
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        
        # Check if account exists using MySQL
        mycursor.execute('SELECT * FROM admin WHERE UserName = %s AND Password = %s', (username, password,))
        
        # Fetch one record and return result
        account = mycursor.fetchone()
        
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedinAdmin'] = True
            session['idAdmin'] = account[0]
            session['usernameAdmin'] = account[1]
            # Redirect to home page
            return redirect(url_for('Admin'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template(r'Admin/index.html', 
                            msg=msg, 
                            titlePage="Admin Control Panel",
                            hide="d-none",
                            login=True)

@app.route('/Admin/logout')
def logoutAdmin():
  # Remove session data, this will log the user out
  session.pop('loggedinAdmin', None)
  session.pop('idAdmin', None)
  session.pop('usernameAdmin', None)
  # Redirect to login page
  return redirect(url_for('login'))

@app.route('/Admin/doctors', methods=['GET'])
def doctors():
  # retrive all tables
  db_tables = retrive_tables(mycursor)

  # Check if user is loggedin
  if 'loggedinAdmin' in session:
    msg = ''
    PassOrNot = "text-danger"
    if request.method == 'POST' :
        SSN = request.form['SSN']
        file = request.files['file']
        FName = request.form['FName']
        MidName = request.form['MidName']
        LName = request.form['LName']
        Phone = request.form['Phone']
        Gender = request.form['Gender']
        Email = request.form['Email']
        Age = request.form['Age']
        Degree = request.form['Degree']
        Password = get_random_number()

        mycursor.execute('SELECT * FROM doctors WHERE SSN = %s', (SSN, ))
        D_SSN = mycursor.fetchone()
        mycursor.execute('SELECT * FROM doctors WHERE Email = %s', (Email, ))
        emailAdd = mycursor.fetchone()

        # Check if SSN is repeated
        if D_SSN:
            msg = 'SSN already exists !'
        # Check if Email is repeated
        elif emailAdd :
            msg = 'Email already exists !'
        # Check if name contains only characters
        elif not re.match(r'[A-Za-z]+', FName):
            msg = 'First Name must contain only characters'
        elif not re.match(r'[A-Za-z]+', MidName):
            msg = 'Name must contain only characters'
        elif not re.match(r'[A-Za-z]+', LName):
            msg = 'Last Name must contain only characters'
        else:
            if file.filename == '':
              path = ""
            else :
              path = "static/img/doctorsProfile/" + secure_filename(file.filename)
              file.save(path)
            
            mycursor.execute("INSERT INTO doctors(SSN, FName, MidName, LName, Age, Gender, Phone, Email, Degree, Password, Image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                                  (SSN, FName, MidName, LName, Age, Gender, Phone, Email, Degree, Password, path))
            mydb.commit()
            
            msg = 'You have successfully Added Doctor.'
            PassOrNot = "text-success"
    
    # User is loggedin show them the home page  
    return render_template('Admin/doctors.html',
                          registered=PassOrNot, 
                          msg=msg, 
                          DoctorsData=db_tables["doctors"],
                          titlePage="Doctors Control Panel")

  # User is not loggedin redirect to login page
  return redirect(url_for('login'))

@app.route('/Admin/General', methods=['GET'])
def generalAdmin():
  # retrive all tables
  db_tables = retrive_tables(mycursor)

  if 'loggedinAdmin' in session:
    msg = ''
    if request.method == 'POST':
        title = request.form['title']
        address = request.form['address']
        email = request.form['email']
        phone = request.form['phone']
        short = request.form['short']
        long = request.form['long']
        icon = request.files['icon']

        if icon.filename == '':
          path = ""
        else :
          path = "static/img/icon/icon.png" 
          icon.save(path)

        mycursor.execute("UPDATE site_information SET Title=%s, Address=%s, Email=%s, Phone=%s, Short_description=%s, Long_description=%s, Icon=%s", (title, address, email, phone, short, long, path))
        mydb.commit()
        msg = 'Updated successfully, please restart the app to update the changes.'
    
    return render_template('Admin/general.html', 
                          msg=msg,
                          titlePage="Site Informtion Control Panel",
                          siteinfo=db_tables["site_information"])

  return redirect(url_for('login'))

@app.route('/Admin/slider', methods=['GET'])
def sliderAdmin():
  # retrive all tables
  db_tables = retrive_tables(mycursor)

  if 'loggedinAdmin' in session:
    msg = ''
    if request.method == 'POST':
        file = request.files['file']
        title = request.form['title']
        Description = request.form['description']

        if file.filename == '':
          path = ""
        else :
          path = "static/img/slider/" + secure_filename(file.filename)
          file.save(path)
        
        mycursor.execute("INSERT INTO slider(Image, Title, Description) VALUES (%s, %s, %s)", 
                                            (path,  title, Description))
        mydb.commit()

        msg = 'Image Uploaded successfully'

    return render_template('Admin/slider.html', 
                          msg=msg, 
                          titlePage="Slider Control Panel",
                          sliderImg=db_tables["slider"])

  return redirect(url_for('login'))

@app.route('/Admin/users', methods=['GET'])
def usersAdmin():
  # retrive all tables
  db_tables = retrive_tables(mycursor)

  if 'loggedinAdmin' in session:    
    return render_template('Admin/users.html', 
                          titlePage="Users", 
                          users=db_tables["users"])

  return redirect(url_for('login'))

@app.route('/Admin/Services', methods=['GET', 'POST'])
def servicesAdmin():
  # retrive all tables
  db_tables = retrive_tables(mycursor)

  # Check if user is loggedin
  if 'loggedinAdmin' in session:
    msg = ''
    PassOrNot = "text-danger"
    if request.method == 'POST' :
        Name = request.form['Name']
        Image = request.files['file']
        Cost = request.form['Cost']
        Duration = request.form['Duration']
        Description = request.form['Description']

        if Image.filename == '':
            path = ""
        else :
          path = "static/img/ServicesProfile/" + secure_filename(Image.filename)
          Image.save(path)

        mycursor.execute("INSERT INTO treatments(Image, Name, cost, Duration, Description) VALUES (%s, %s, %s, %s, %s)", 
                                                (path,  Name, Cost, Duration, Description))
        mydb.commit()

        msg = 'You Have Successfully Added New Service/Treatment.'
        PassOrNot = "text-success"
    
    # User is loggedin show them the home page  
    return render_template('Admin/services.html',
                          titlePage="Doctors Control Panel",
                          registered=PassOrNot, 
                          msg=msg, 
                          servicesData=db_tables["treatments"])

  # User is not loggedin redirect to login page
  return redirect(url_for('login'))

@app.route('/Admin/Appointemnts', methods=['GET'])
def appointmentsAdmin():
  # retrive all tables
  db_tables = retrive_tables(mycursor)

  if request.method == 'POST' :
      id = request.form['id']
      date = request.form['date']
      if request.form['status'] == 'Accept':
        mycursor.execute('update appointments set Status="Accepted", date=%s WHERE id = %s', (date, id, ))
      else:
        mycursor.execute('update appointments set Status="Refused" WHERE id = %s', (id, ))
    
      mydb.commit()
  
  AppointmentsList = []
  for Appointment in db_tables["appointments"]:
    Appointment = list(Appointment)
    mycursor.execute("select UserName from users where id = %s",(Appointment[9],))
    App_UserName = mycursor.fetchall()[0][0]
    Appointment[9] = App_UserName

    mycursor.execute("select FName, MidName, LName from doctors where id = %s",(Appointment[10],))
    App_DName = mycursor.fetchall()[0]
    Appointment[10] = App_DName[0]  + " " + App_DName[1] + " " + App_DName[2]  

    mycursor.execute("select Name from treatments where id = %s",(Appointment[11],))
    TreatName = mycursor.fetchall()[0][0]
    Appointment[11] = TreatName

    AppointmentsList.append(Appointment)

  return render_template('Admin/appointments.html',
                          titlePage="Appointments Control Panel",
                          AppointmentsTable=AppointmentsList)


@app.route('/Admin/Admins', methods=['GET'])
def Admins():
  # retrive all tables
  db_tables = retrive_tables(mycursor)

  if 'loggedinAdmin' in session:
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repassword = request.form['repassword']

        if password == repassword :
          msg = "Please, Enter the same password"
        
        mycursor.execute("INSERT INTO admin(Username, Password) VALUES (%s, %s)", 
                                            (username, password))
        mydb.commit()

        msg = 'Addded successfully'

    return render_template('Admin/admins.html', 
                          msg=msg, 
                          titlePage="Admins Table Control Panel",
                          Admins=db_tables["admin"])

  return redirect(url_for('login'))


#--------------------------------------------------------------------------#

# Run the Website 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)