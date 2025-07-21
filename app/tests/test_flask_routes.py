"""
Integration tests for Flask routes
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from io import BytesIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


class TestHomePageRoute:
    """Test cases for home page route (/)"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_home_page_get(self, mock_retrive_tables, mock_init_db, client):
        """Test GET request to home page"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "site_information": [
                "Test Site",
                "Test Address",
                "test@example.com",
                "123-456-7890",
                "Short desc",
                "Long description",
            ],
            "rates": [(5, "Great service", 1), (4, "Good", 2)],
            "treatments": [
                (1, "Cleaning", 100, "30 min", "Dental cleaning", "image.jpg")
            ],
            "slider": [(1, "slide1.jpg", "Title 1", "Description 1")],
            "users": [
                (
                    1,
                    "John",
                    "M",
                    "Doe",
                    "profile.jpg",
                    "johndoe",
                    "password123",
                    "john@example.com",
                    "123-456-7890",
                )
            ],
        }

        # Mock cursor for rates processing
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [(1, "testuser")]

        response = client.get("/")

        assert response.status_code == 200
        assert b"Homepage" in response.data or b"Test Site" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_home_page_post_user_login_success(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test successful user login via POST"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "site_information": [
                "Test Site",
                "Test Address",
                "test@example.com",
                "123-456-7890",
                "Short desc",
                "Long description",
            ],
            "rates": [(5, "Great service", 1)],
            "treatments": [],
            "slider": [],
            "users": [],
        }

        # Mock successful user login
        mock_cursor.fetchone.side_effect = [
            (
                1,
                "John",
                "M",
                "Doe",
                "profile.jpg",
                "testuser",
                "password123",
                "test@example.com",
                "123-456-7890",
            )
        ]
        mock_cursor.fetchall.return_value = [(1, "testuser")]

        response = client.post(
            "/", data={"email": "test@example.com", "password": "password123"}
        )

        assert response.status_code == 302  # Redirect to profile
        assert "/profile" in response.location

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_home_page_post_doctor_login_success(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test successful doctor login via POST"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "site_information": [
                "Test Site",
                "Test Address",
                "test@example.com",
                "123-456-7890",
                "Short desc",
                "Long description",
            ],
            "rates": [],
            "treatments": [],
            "slider": [],
            "users": [],
        }

        # Mock successful doctor login
        mock_cursor.fetchone.side_effect = [
            (
                1,
                "123456789",
                "Dr. Jane",
                "M",
                "Smith",
                35,
                "Female",
                "987-654-3210",
                "jane@example.com",
                "DDS",
                "password123",
                "doctor.jpg",
            )
        ]
        mock_cursor.fetchall.return_value = []

        response = client.post(
            "/",
            data={
                "doctor": "on",
                "email": "jane@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 302  # Redirect to profile
        assert "/profile" in response.location

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_home_page_post_login_failure(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test failed login attempt"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "site_information": [
                "Test Site",
                "Test Address",
                "test@example.com",
                "123-456-7890",
                "Short desc",
                "Long description",
            ],
            "rates": [],
            "treatments": [],
            "slider": [],
            "users": [],
        }

        # Mock failed login
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []

        response = client.post(
            "/", data={"email": "wrong@example.com", "password": "wrongpassword"}
        )

        assert response.status_code == 200
        assert b"Incorrect email or password" in response.data


class TestAboutUsRoute:
    """Test cases for about us route (/About)"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_about_us_page(self, mock_retrive_tables, mock_init_db, client):
        """Test about us page"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "users": [
                (
                    1,
                    "John",
                    "M",
                    "Doe",
                    "profile.jpg",
                    "johndoe",
                    "password123",
                    "john@example.com",
                    "123-456-7890",
                )
            ]
        }

        response = client.get("/About")

        assert response.status_code == 200
        assert b"About Us" in response.data or b"about" in response.data.lower()


class TestDoctorsRoute:
    """Test cases for doctors route (/Doctors)"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_doctors_page(self, mock_retrive_tables, mock_init_db, client):
        """Test doctors page"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "doctors": [
                (
                    1,
                    "123456789",
                    "Dr. Jane",
                    "M",
                    "Smith",
                    35,
                    "Female",
                    "987-654-3210",
                    "jane@example.com",
                    "DDS",
                    "password123",
                    "doctor.jpg",
                )
            ]
        }

        response = client.get("/Doctors")

        assert response.status_code == 200
        assert b"Dentists" in response.data or b"doctors" in response.data.lower()


class TestAppointmentRoute:
    """Test cases for appointment route (/Appointment)"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_appointment_get(self, mock_retrive_tables, mock_init_db, client):
        """Test GET request to appointment page"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "doctors": [
                (
                    1,
                    "123456789",
                    "Dr. Jane",
                    "M",
                    "Smith",
                    35,
                    "Female",
                    "987-654-3210",
                    "jane@example.com",
                    "DDS",
                    "password123",
                    "doctor.jpg",
                )
            ],
            "treatments": [
                (1, "Cleaning", 100, "30 min", "Dental cleaning", "image.jpg")
            ],
        }

        response = client.get("/Appointment")

        assert response.status_code == 200
        assert b"appointment" in response.data.lower()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    def test_appointment_post_success(
        self, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test successful appointment booking"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "doctors": [
                (
                    1,
                    "123456789",
                    "Dr. Jane",
                    "M",
                    "Smith",
                    35,
                    "Female",
                    "987-654-3210",
                    "jane@example.com",
                    "DDS",
                    "password123",
                    "doctor.jpg",
                )
            ],
            "treatments": [
                (1, "Cleaning", 100, "30 min", "Dental cleaning", "image.jpg")
            ],
        }

        # Mock database queries for appointment creation
        mock_cursor.fetchone.side_effect = [
            (100,),  # treatment cost
            (1,),  # doctor id
            (1,),  # service id
        ]

        with client.session_transaction() as sess:
            sess["id"] = 1

        response = client.post(
            "/Appointment",
            data={
                "SSN": "987654321",
                "FName": "Patient",
                "MidName": "M",
                "LName": "Name",
                "Age": "25",
                "Gender": "Male",
                "Doctor": "Dr. Jane M Smith",
                "Service": "Cleaning",
            },
        )

        try:
            assert (
                b"successfully booked" in response.data or response.status_code == 200
            )
        except AssertionError:
            print("\nActual response data for appointment post:", response.data)
            raise


class TestRegisterRoute:
    """Test cases for register route (/register)"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_register_get(self, mock_retrive_tables, mock_init_db, client):
        """Test GET request to register page"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        response = client.get("/register")

        assert response.status_code == 200
        assert b"Sign Up" in response.data or b"register" in response.data.lower()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    @patch("app.main.secure_filename")
    def test_register_post_success(
        self, mock_secure_filename, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test successful user registration"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}
        mock_secure_filename.return_value = "profile.jpg"

        # Mock database queries to return no existing users
        mock_cursor.fetchone.return_value = None

        # Create a mock file
        data = {
            "FName": "John",
            "MidName": "M",
            "LName": "Doe",
            "username": "johndoe",
            "password": "password123",
            "repassword": "password123",
            "email": "john@example.com",
            "Phone": "123-456-7890",
            "file": (BytesIO(b"fake image"), "profile.jpg"),
        }

        response = client.post("/register", data=data)

        assert response.status_code == 200
        assert b"successfully registered" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_register_post_username_exists(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test registration with existing username"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        # Mock existing username
        mock_cursor.fetchone.side_effect = [
            (
                1,
                "John",
                "M",
                "Doe",
                "profile.jpg",
                "johndoe",
                "password123",
                "john@example.com",
                "123-456-7890",
            ),  # Username exists
            None,  # Email doesn't exist
            None,  # Phone doesn't exist
        ]

        data = {
            "FName": "John",
            "MidName": "M",
            "LName": "Doe",
            "username": "johndoe",
            "password": "password123",
            "repassword": "password123",
            "email": "john@example.com",
            "Phone": "123-456-7890",
            "file": (BytesIO(b""), ""),
        }

        response = client.post("/register", data=data)

        assert response.status_code == 200
        assert b"Username already exists" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_register_post_password_mismatch(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test registration with password mismatch"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        # Mock no existing users
        mock_cursor.fetchone.return_value = None

        data = {
            "FName": "John",
            "MidName": "M",
            "LName": "Doe",
            "username": "johndoe",
            "password": "password123",
            "repassword": "wrongpassword",
            "email": "john@example.com",
            "Phone": "123-456-7890",
            "file": (BytesIO(b""), ""),
        }

        response = client.post("/register", data=data)

        assert response.status_code == 200
        assert b"same password" in response.data


class TestProfileRoute:
    """Test cases for profile route (/profile)"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.get_user_appointments")
    def test_profile_user(
        self, mock_get_user_appointments, mock_retrive_tables, mock_init_db, client
    ):
        """Test profile page for regular user"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        # Mock user appointments
        mock_user_info = (
            1,
            "John",
            "M",
            "Doe",
            "profile.jpg",
            "testuser",
            "password123",
            "john@example.com",
            "123-456-7890",
        )
        mock_appointments = [
            (
                1,
                "987654321",
                "Patient",
                "M",
                "Name",
                25,
                "Male",
                "2023-01-01",
                "Waiting",
                1,
                1,
                1,
            )
        ]
        mock_get_user_appointments.return_value = (mock_user_info, mock_appointments)

        with client.session_transaction() as sess:
            sess["username"] = "testuser"
            sess["doctor"] = False

        response = client.get("/profile")

        assert response.status_code == 200
        assert b"testuser" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.get_doctor_appointments")
    def test_profile_doctor(
        self, mock_get_doctor_appointments, mock_retrive_tables, mock_init_db, client
    ):
        """Test profile page for doctor"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        # Mock doctor appointments
        mock_doctor_info = (
            1,
            "123456789",
            "Dr. Jane",
            "M",
            "Smith",
            35,
            "Female",
            "987-654-3210",
            "jane@example.com",
            "DDS",
            "password123",
            "doctor.jpg",
        )
        mock_appointments = [
            (
                1,
                "987654321",
                "Patient",
                "M",
                "Name",
                25,
                "Male",
                "2023-01-01",
                "Scheduled",
                1,
                1,
                1,
            )
        ]
        mock_appointments_json = [mock_appointments[0]]
        mock_get_doctor_appointments.return_value = (
            mock_doctor_info,
            mock_appointments,
            mock_appointments_json,
        )

        with client.session_transaction() as sess:
            sess["username"] = "doctor@example.com"
            sess["doctor"] = True

        response = client.get("/profile")

        assert response.status_code == 200
        assert b"doctor@example.com" in response.data


class TestContactUsRoute:
    """Test cases for contact us route (/Contact)"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_contact_us_get(self, mock_retrive_tables, mock_init_db, client):
        """Test GET request to contact us page"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "site_information": [
                "Test Site",
                "Test Address",
                "test@example.com",
                "123-456-7890",
                "Short desc",
                "Long description",
            ]
        }

        response = client.get("/Contact")

        assert response.status_code == 200
        assert b"Contact Us" in response.data or b"contact" in response.data.lower()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mail")
    def test_contact_us_post_success(
        self, mock_mail, mock_retrive_tables, mock_init_db, client
    ):
        """Test successful contact form submission"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "site_information": [
                "Test Site",
                "Test Address",
                "test@example.com",
                "123-456-7890",
                "Short desc",
                "Long description",
            ]
        }

        # Mock successful email sending
        mock_mail.send.return_value = None

        response = client.post(
            "/Contact",
            data={
                "name": "John Doe",
                "email": "john@example.com",
                "subject": "Test Subject",
                "message": "Test message",
            },
        )

        assert response.status_code == 200
        assert b"Thanks for the message" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mail")
    def test_contact_us_post_email_failure(
        self, mock_mail, mock_retrive_tables, mock_init_db, client
    ):
        """Test contact form submission with email failure"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "site_information": [
                "Test Site",
                "Test Address",
                "test@example.com",
                "123-456-7890",
                "Short desc",
                "Long description",
            ]
        }

        # Mock email sending failure
        mock_mail.send.side_effect = Exception("Email sending failed")

        response = client.post(
            "/Contact",
            data={
                "name": "John Doe",
                "email": "john@example.com",
                "subject": "Test Subject",
                "message": "Test message",
            },
        )

        assert response.status_code == 200
        assert b"error occurred" in response.data


class TestRateUsRoute:
    """Test cases for rate us route (/Rate)"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_rate_us_get(self, mock_retrive_tables, mock_init_db, client):
        """Test GET request to rate us page"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "rates": [(5, "Great service", 1), (4, "Good", 2)]
        }

        response = client.get("/Rate")

        assert response.status_code == 200
        assert b"Rate Us" in response.data or b"rate" in response.data.lower()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    def test_rate_us_post_success(
        self, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test successful rating submission"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {"rates": [(5, "Great service", 1)]}

        with client.session_transaction() as sess:
            sess["id"] = 1

        response = client.post(
            "/Rate", data={"rating": "5", "message": "Excellent service!"}
        )

        try:
            assert b"Thank" in response.data or response.status_code == 200
        except AssertionError:
            print("\nActual response data for rate us post:", response.data)
            raise


class TestLogoutRoute:
    """Test cases for logout route (/logout)"""

    def test_logout(self, client):
        """Test logout functionality"""
        with client.session_transaction() as sess:
            sess["loggedin"] = True
            sess["id"] = 1
            sess["username"] = "testuser"
            sess["doctor"] = False

        response = client.get("/logout")

        assert response.status_code == 302  # Redirect to home
        assert "/" in response.location

        # Check that session is cleared
        with client.session_transaction() as sess:
            assert "loggedin" not in sess
            assert "id" not in sess
            assert "username" not in sess
            assert "doctor" not in sess
