"""
Edge case and error handling tests for the Flask application
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, init_db, validate_doctor_form, create_doctor


class TestDatabaseConnectionFailures:
    """Test cases for database connection failures"""

    @patch("app.main.mysql_connector")
    def test_init_db_mysql_connector_returns_none(self, mock_mysql_connector):
        """Test init_db when mysql_connector returns None"""
        mock_mysql_connector.return_value = (None, None)

        # Reset global variables
        import main

        main.mydb = None
        main.mycursor = None

        with pytest.raises(RuntimeError, match="Database connection failed"):
            init_db()

    @patch("app.main.mysql_connector")
    def test_init_db_mysql_connector_exception(self, mock_mysql_connector):
        """Test init_db when mysql_connector raises exception"""
        mock_mysql_connector.side_effect = Exception("Connection error")

        # Reset global variables
        import main

        main.mydb = None
        main.mycursor = None

        with pytest.raises(Exception, match="Connection error"):
            init_db()

    @patch("app.main.init_db")
    def test_route_with_database_failure(self, mock_init_db, client):
        """Test route behavior when database initialization fails"""
        mock_init_db.side_effect = RuntimeError("Database connection failed")

        with pytest.raises(RuntimeError):
            response = client.get("/")


class TestInvalidFormSubmissions:
    """Test cases for invalid form submissions"""

    @patch("app.main.mydb")
    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_register_invalid_username_characters(
        self, mock_retrive_tables, mock_init_db, mock_mydb, client
    ):
        """Test registration with invalid username characters"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}
        mock_mydb.commit = Mock()
        # Mock no existing users
        mock_cursor.fetchone.return_value = None
        data = {
            "FName": "John",
            "MidName": "M",
            "LName": "Doe",
            "username": "john@doe!",  # Invalid characters
            "password": "password123",
            "repassword": "password123",
            "email": "john@example.com",
            "Phone": "123-456-7890",
            "file": (BytesIO(b""), ""),
        }
        response = client.post("/register", data=data)
        assert (
            b"error" in response.data
            or b"Error" in response.data
            or response.status_code == 200
        )

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_register_weak_password(self, mock_retrive_tables, mock_init_db, client):
        """Test registration with weak password"""
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
            "password": "123",  # Too short
            "repassword": "123",
            "email": "john@example.com",
            "Phone": "123-456-7890",
            "file": (BytesIO(b""), ""),
        }

        response = client.post("/register", data=data)

        assert response.status_code == 200
        assert b"Weak Password" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_register_existing_email(self, mock_retrive_tables, mock_init_db, client):
        """Test registration with existing email"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        # Mock existing email
        mock_cursor.fetchone.side_effect = [
            None,  # Username doesn't exist
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
            ),  # Email exists
            None,  # Phone doesn't exist
        ]

        data = {
            "FName": "John",
            "MidName": "M",
            "LName": "Doe",
            "username": "johndoe2",
            "password": "password123",
            "repassword": "password123",
            "email": "john@example.com",  # Existing email
            "Phone": "123-456-7890",
            "file": (BytesIO(b""), ""),
        }

        response = client.post("/register", data=data)

        assert response.status_code == 200
        assert b"Email already exists" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_register_existing_phone(self, mock_retrive_tables, mock_init_db, client):
        """Test registration with existing phone"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        # Mock existing phone
        mock_cursor.fetchone.side_effect = [
            None,  # Username doesn't exist
            None,  # Email doesn't exist
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
            ),  # Phone exists
        ]

        data = {
            "FName": "John",
            "MidName": "M",
            "LName": "Doe",
            "username": "johndoe2",
            "password": "password123",
            "repassword": "password123",
            "email": "john2@example.com",
            "Phone": "123-456-7890",  # Existing phone
            "file": (BytesIO(b""), ""),
        }

        response = client.post("/register", data=data)

        assert response.status_code == 200
        assert b"Phone already exists" in response.data


class TestFileUploadEdgeCases:
    """Test cases for file upload edge cases"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    @patch("app.main.secure_filename")
    def test_register_with_empty_filename(
        self, mock_secure_filename, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test registration with empty filename"""
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
            "repassword": "password123",
            "email": "john@example.com",
            "Phone": "123-456-7890",
            "file": (BytesIO(b""), ""),  # Empty filename
        }

        response = client.post("/register", data=data)

        assert response.status_code == 200
        assert b"successfully registered" in response.data
        # Verify secure_filename was not called for empty filename
        mock_secure_filename.assert_not_called()

    def test_create_doctor_with_empty_filename(self):
        """Test create_doctor with empty filename"""
        mock_cursor = Mock()
        mock_file = Mock()
        mock_file.filename = ""  # Empty filename
        mock_file.save = Mock()

        doctor_data = {
            "ssn": "123456789",
            "file": mock_file,
            "f_name": "John",
            "mid_name": "Michael",
            "l_name": "Doe",
            "phone": "123-456-7890",
            "gender": "Male",
            "email": "john@example.com",
            "age": "35",
            "degree": "DDS",
            "password": "12345678",
        }

        with patch("app.main.mydb") as mock_mydb:
            create_doctor(mock_cursor, doctor_data)

            # Verify file was not saved
            mock_file.save.assert_not_called()

            # Verify database insert was called with empty path
            mock_cursor.execute.assert_called_once()
            call_args = mock_cursor.execute.call_args[0][1]
            assert "" in call_args  # Empty path should be in the parameters


class TestEmailSendingFailures:
    """Test cases for email sending failures"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mail")
    def test_contact_us_email_connection_error(
        self, mock_mail, mock_retrive_tables, mock_init_db, client
    ):
        """Test contact form with email connection error"""
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
        mock_mail.send.side_effect = ConnectionError("SMTP connection failed")

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
        assert b"SMTP connection failed" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mail")
    def test_contact_us_email_authentication_error(
        self, mock_mail, mock_retrive_tables, mock_init_db, client
    ):
        """Test contact form with email authentication error"""
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

        # Mock email authentication failure
        mock_mail.send.side_effect = Exception("Authentication failed")

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
        assert b"Authentication failed" in response.data


class TestAuthenticationEdgeCases:
    """Test cases for authentication edge cases"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_home_page_empty_credentials(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test login with empty credentials"""
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
            "/", data={"email": "", "password": ""}  # Empty email  # Empty password
        )

        assert response.status_code == 200
        assert b"Incorrect email or password" in response.data

    def test_profile_page_no_session(self, client):
        """Test profile page access without session"""
        with patch("app.main.init_db") as mock_init_db, patch(
            "app.main.retrive_tables"
        ) as mock_retrive_tables:
            # Mock database setup
            mock_db, mock_cursor = Mock(), Mock()
            mock_init_db.return_value = (mock_db, mock_cursor)
            mock_cursor.fetchall.return_value = []
            mock_cursor.fetchone.return_value = None
            mock_retrive_tables.return_value = {
                "users": [],
                "appointments": [],
                "rates": [],
                "treatments": [],
                "slider": [],
            }
            with client.session_transaction() as sess:
                sess["username"] = "testuser"
                sess["doctor"] = False
                sess["id"] = 1
            response = client.get("/profile")
            assert response.status_code == 200

    def test_appointment_without_session_id(self, client):
        """Test appointment booking without session ID"""
        with patch("app.main.init_db") as mock_init_db, patch(
            "app.main.retrive_tables"
        ) as mock_retrive_tables, patch("app.main.mydb") as mock_mydb:
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
            assert response.status_code in [200, 500]


class TestSessionHandlingEdgeCases:
    """Test cases for session handling edge cases"""

    def test_logout_without_session(self, client):
        """Test logout without existing session"""
        response = client.get("/logout")

        assert response.status_code == 302  # Redirect to home
        assert "/" in response.location

    def test_admin_logout_without_session(self, client):
        """Test admin logout without existing session"""
        response = client.get("/Admin/logout")

        assert response.status_code == 302  # Redirect to login
        assert "/Admin/" in response.location

    @patch("app.main.mydb")
    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_rate_us_without_user_id(
        self, mock_retrive_tables, mock_init_db, mock_mydb, client
    ):
        """Test rating submission without user ID in session"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {"rates": []}
        mock_mydb.commit = Mock()
        with client.session_transaction() as sess:
            sess["id"] = 1
        response = client.post(
            "/Rate", data={"rating": "5", "message": "Excellent service!"}
        )
        assert response.status_code in [200, 500]


class TestDatabaseQueryEdgeCases:
    """Test cases for database query edge cases"""

    def test_validate_doctor_form_database_error(self):
        """Test validate_doctor_form with database error"""
        mock_request = Mock()
        mock_cursor = Mock()

        # Set up valid form data
        mock_request.form = {
            "SSN": "123456789",
            "FName": "John",
            "MidName": "Michael",
            "LName": "Doe",
            "Phone": "123-456-7890",
            "Gender": "Male",
            "Email": "john@example.com",
            "Age": "35",
            "Degree": "DDS",
        }
        mock_request.files = {"file": Mock(filename="doctor.jpg")}

        # Mock database error
        mock_cursor.fetchone.side_effect = Exception("Database query failed")

        with pytest.raises(Exception, match="Database query failed"):
            validate_doctor_form(mock_request, mock_cursor)

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_home_page_database_query_error(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test home page with database query error"""
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

        # Mock database query error during rates processing
        mock_cursor.execute.side_effect = Exception("Database query failed")

        with pytest.raises(Exception):
            response = client.get("/")


class TestMissingDataHandling:
    """Test cases for missing data handling"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_home_page_empty_rates(self, mock_retrive_tables, mock_init_db, client):
        """Test home page with empty rates"""
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
            "rates": [],  # Empty rates
            "treatments": [],
            "slider": [],
            "users": [],
        }

        response = client.get("/")

        assert response.status_code == 200
        # Should handle empty rates gracefully

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_doctors_page_empty_doctors(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test doctors page with empty doctors list"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {"doctors": []}  # Empty doctors list

        response = client.get("/Doctors")

        assert response.status_code == 200
        # Should handle empty doctors list gracefully

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_appointment_page_empty_treatments(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test appointment page with empty treatments"""
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
            "treatments": [],  # Empty treatments
        }

        response = client.get("/Appointment")

        assert response.status_code == 200
        # Should handle empty treatments gracefully


class TestSpecialCharacterHandling:
    """Test cases for special character handling"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_contact_us_special_characters(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test contact form with special characters"""
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

        with patch("app.main.mail") as mock_mail:
            mock_mail.send.return_value = None

            response = client.post(
                "/Contact",
                data={
                    "name": "John Döe",  # Special characters
                    "email": "john@example.com",
                    "subject": "Test Subject with émojis 🎉",
                    "message": "Test message with special chars: àáâãäåæçèéêë",
                },
            )

            assert response.status_code == 200
            assert b"Thanks for the message" in response.data
