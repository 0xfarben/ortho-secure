import os
import mysql.connector
from pathlib import Path

def mysql_connector():
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_PORT = os.getenv('MYSQL_PORT')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=int(MYSQL_PORT),  # Ensure port is an integer
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            auth_plugin='mysql_native_password'  # If using mysql:5.7
        )
        
        print(f"SUCCESS connecting to MySQL")
        mycursor = conn.cursor(buffered=True)
        return conn, mycursor
    except mysql.connector.Error as error:
        print(f"Error connecting to MySQL: {error}")
        return None, None
    

"""Retrive Database Tables"""

def admin(mycursor) :
    'Retrieve all admin data'
    mycursor.execute("SELECT * FROM admin")
    admin_table = mycursor.fetchall()

    return admin_table

def site_information(mycursor) :
    'Retrieve site information data'
    mycursor.execute("SELECT * FROM site_information")
    site_info_table = mycursor.fetchone()
    
    return site_info_table

def slider(mycursor) :
    'Retrieve slider data'
    mycursor.execute("SELECT * FROM slider")
    slider_table = mycursor.fetchall()
    
    return slider_table

def doctors(mycursor) :
    'Retrieve all doctors data'
    mycursor.execute("SELECT * FROM doctors")
    doctors_table = mycursor.fetchall()
    
    return doctors_table

def treatments(mycursor) :
    'Retrieve all treatments data'
    mycursor.execute("SELECT * FROM treatments")
    treatments_table = mycursor.fetchall()
    
    return treatments_table

def appointments(mycursor) :
    'Retrieve all appointments data'
    mycursor.execute("SELECT * FROM appointments")
    appointments_table = mycursor.fetchall()

    return appointments_table

def users(mycursor) :
    'Retrieve all users data'
    mycursor.execute("SELECT * FROM users")
    users_table = mycursor.fetchall()

    return users_table

def rates(mycursor) :
    'Retrieve all rates data'
    mycursor.execute("SELECT * FROM rates limit 10")
    rates_table = mycursor.fetchall()
    
    return rates_table

def retrive_tables(mycursor) :
    tables = dict()

    tables["admin"] = admin(mycursor)
    tables["site_information"] = site_information(mycursor)
    tables["slider"] = slider(mycursor)
    tables["doctors"] = doctors(mycursor)
    tables["treatments"] = treatments(mycursor)
    tables["appointments"] = appointments(mycursor)
    tables["users"] = users(mycursor)
    tables["rates"] = rates(mycursor)

    return tables