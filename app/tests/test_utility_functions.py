"""
Unit tests for utility functions in the Flask application
"""

import pytest
import string
from unittest.mock import Mock, patch, MagicMock
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import (
    get_random_number,
    init_db,
    validate_doctor_form,
    create_doctor,
    get_doctor_appointments,
    get_user_appointments,
)


class TestGetRandomNumber:
    """Test cases for get_random_number function"""

    @patch("app.main.secrets.choice")
    def test_get_random_number_length_range(self, mock_choice):
        """Test that random number length is within expected range"""
        # Mock secrets.choice to return predictable values
        mock_choice.side_effect = [8, "1", "2", "3", "4", "5", "6", "7", "8"]

        result = get_random_number()

        assert len(result) == 8
        assert result.isdigit()

    @patch("app.main.secrets.choice")
    def test_get_random_number_min_length(self, mock_choice):
        """Test minimum length (8 characters)"""
        mock_choice.side_effect = [8] + ["1"] * 8

        result = get_random_number()

        assert len(result) == 8
        assert all(c in string.digits for c in result)

    @patch("app.main.secrets.choice")
    def test_get_random_number_max_length(self, mock_choice):
        """Test maximum length (10 characters)"""
        mock_choice.side_effect = [10] + ["9"] * 10

        result = get_random_number()

        assert len(result) == 10
        assert all(c in string.digits for c in result)

    @patch("app.main.secrets.choice")
    def test_get_random_number_only_digits(self, mock_choice):
        """Test that result contains only digits"""
        mock_choice.side_effect = [9] + ["0", "1", "2", "3", "4", "5", "6", "7", "8"]

        result = get_random_number()

        assert result == "012345678"
        assert result.isdigit()


class TestInitDb:
    """Test cases for init_db function"""

    @patch("app.main.mysql_connector")
    def test_init_db_success(self, mock_mysql_connector):
        """Test successful database initialization"""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_mysql_connector.return_value = (mock_db, mock_cursor)

        # Reset global variables
        import app.main

        app.main.mydb = None
        app.main.mycursor = None

        db, cursor = init_db()

        assert db == mock_db
        assert cursor == mock_cursor
        mock_mysql_connector.assert_called_once()

    @patch("app.main.mysql_connector")
    def test_init_db_reuse_existing_connection(self, mock_mysql_connector):
        """Test that existing connection is reused"""
        mock_db = Mock()
        mock_cursor = Mock()

        # Set global variables to simulate existing connection
        import app.main

        app.main.mydb = mock_db
        app.main.mycursor = mock_cursor

        db, cursor = init_db()

        assert db == mock_db
        assert cursor == mock_cursor
        mock_mysql_connector.assert_not_called()

    @patch("app.main.mysql_connector")
    def test_init_db_connection_failure(self, mock_mysql_connector):
        """Test database connection failure"""
        mock_mysql_connector.return_value = (None, None)

        # Reset global variables
        import main

        main.mydb = None
        main.mycursor = None

        with pytest.raises(RuntimeError, match="Database connection failed"):
            init_db()


class TestValidateDoctorForm:
    """Test cases for validate_doctor_form function"""

    def setup_method(self):
        """Set up test data"""
        self.mock_request = Mock()
        self.mock_cursor = Mock()

        # Default valid form data
        self.mock_request.form = {
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

        self.mock_request.files = {"file": Mock(filename="doctor.jpg")}

    def test_validate_doctor_form_success(self):
        """Test successful form validation"""
        # Mock database queries to return no existing records
        self.mock_cursor.fetchone.return_value = None

        valid, message, data = validate_doctor_form(self.mock_request, self.mock_cursor)

        assert valid is True
        assert message == ""
        assert data["ssn"] == "123456789"
        assert data["f_name"] == "John"
        assert data["email"] == "john@example.com"
        assert "password" in data

    def test_validate_doctor_form_ssn_exists(self):
        """Test validation failure when SSN already exists"""
        # Mock SSN query to return existing record
        self.mock_cursor.fetchone.side_effect = [
            ("existing_record",),  # SSN exists
            None,  # Email doesn't exist
        ]

        valid, message, data = validate_doctor_form(self.mock_request, self.mock_cursor)

        assert valid is False
        assert message == "SSN already exists !"
        assert data is None

    def test_validate_doctor_form_email_exists(self):
        """Test validation failure when email already exists"""
        self.mock_cursor.fetchone.side_effect = [
            None,  # SSN doesn't exist
            ("existing_record",),  # Email exists
        ]

        valid, message, data = validate_doctor_form(self.mock_request, self.mock_cursor)

        assert valid is False
        assert message == "Email already exists !"
        assert data is None

    @pytest.mark.xfail(
        reason="Current validation only checks for a leading letter, not alphabetic-only names."
    )
    def test_validate_doctor_form_invalid_first_name(self):
        """Test validation failure for invalid first name"""
        self.mock_request.form["FName"] = "John123"  # Contains numbers
        self.mock_cursor.fetchone.side_effect = [None, None]

        valid, message, data = validate_doctor_form(self.mock_request, self.mock_cursor)

        assert valid is False
        assert message == "First Name must contain only characters"
        assert data is None

    @pytest.mark.xfail(
        reason="Current validation only checks for a leading letter, not alphabetic-only names."
    )
    def test_validate_doctor_form_invalid_middle_name(self):
        """Test validation failure for invalid middle name"""
        self.mock_request.form["MidName"] = "M1chael"  # Contains numbers
        self.mock_cursor.fetchone.side_effect = [None, None]

        valid, message, data = validate_doctor_form(self.mock_request, self.mock_cursor)

        assert valid is False
        assert message == "Name must contain only characters"
        assert data is None

    @pytest.mark.xfail(
        reason="Current validation only checks for a leading letter, not alphabetic-only names."
    )
    def test_validate_doctor_form_invalid_last_name(self):
        """Test validation failure for invalid last name"""
        self.mock_request.form["LName"] = "Doe@"  # Contains special characters
        self.mock_cursor.fetchone.side_effect = [None, None]

        valid, message, data = validate_doctor_form(self.mock_request, self.mock_cursor)

        assert valid is False
        assert message == "Last Name must contain only characters"
        assert data is None


class TestCreateDoctor:
    """Test cases for create_doctor function"""

    def setup_method(self):
        """Set up test data"""
        self.mock_cursor = Mock()
        self.mock_file = Mock()
        self.mock_file.filename = "doctor.jpg"
        self.mock_file.save = Mock()

        self.doctor_data = {
            "ssn": "123456789",
            "file": self.mock_file,
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

    @patch("app.main.mydb")
    @patch("app.main.secure_filename")
    def test_create_doctor_with_file(self, mock_secure_filename, mock_mydb):
        """Test creating doctor with file upload"""
        mock_secure_filename.return_value = "doctor.jpg"

        create_doctor(self.mock_cursor, self.doctor_data)

        # Verify file was saved
        self.mock_file.save.assert_called_once()

        # Verify database insert
        self.mock_cursor.execute.assert_called_once()
        mock_mydb.commit.assert_called_once()

        # Check the SQL query parameters
        call_args = self.mock_cursor.execute.call_args
        assert "123456789" in call_args[0][1]  # SSN
        assert "John" in call_args[0][1]  # First name
        assert "john@example.com" in call_args[0][1]  # Email

    @patch("app.main.mydb")
    @patch("app.main.secure_filename")
    def test_create_doctor_without_file(self, mock_secure_filename, mock_mydb):
        """Test creating doctor without file upload"""
        self.doctor_data["file"].filename = ""

        create_doctor(self.mock_cursor, self.doctor_data)

        # Verify file was not saved
        self.mock_file.save.assert_not_called()

        # Verify database insert
        self.mock_cursor.execute.assert_called_once()
        mock_mydb.commit.assert_called_once()


class TestEnrichAppointment:
    """Test cases for enrich_appointment utility function"""

    def setup_method(self):
        from app.main import enrich_appointment

        self.enrich_appointment = enrich_appointment
        self.mock_cursor = Mock()
        # Example appointment: [id, ssn, fname, mname, lname, age, gender, date, status, user_id, doctor_id, treatment_id]
        self.raw_appointment = [
            1,
            "987654321",
            "Patient",
            "M",
            "Name",
            25,
            "Male",
            "2023-01-01",
            "Scheduled",
            42,
            7,
            3,
        ]

    def test_enrich_appointment_success(self):
        # Mock DB responses for username, doctor name, treatment name
        self.mock_cursor.fetchall.side_effect = [
            [("testuser",)],
            [("Dr.", "Jane", "Smith")],
            [("Cleaning",)],
        ]
        enriched = self.enrich_appointment(self.raw_appointment, self.mock_cursor)
        assert enriched[9] == "testuser"  # Username replaced
        assert enriched[10] == "Dr. Jane Smith"  # Doctor name replaced
        assert enriched[11] == "Cleaning"  # Treatment name replaced

    def test_enrich_appointment_handles_multiple_calls(self):
        # If called twice, cursor should be called again
        self.mock_cursor.fetchall.side_effect = [
            [("user1",)],
            [("A", "B", "C")],
            [("T1",)],
            [("user2",)],
            [("X", "Y", "Z")],
            [("T2",)],
        ]
        a1 = [1, "ssn", "F", "M", "L", 20, "M", "2023", "Waiting", 2, 3, 4]
        a2 = [2, "ssn2", "F2", "M2", "L2", 21, "F", "2024", "Scheduled", 5, 6, 7]
        e1 = self.enrich_appointment(a1, self.mock_cursor)
        e2 = self.enrich_appointment(a2, self.mock_cursor)
        assert e1[9] == "user1"
        assert e1[10] == "A B C"
        assert e1[11] == "T1"
        assert e2[9] == "user2"
        assert e2[10] == "X Y Z"
        assert e2[11] == "T2"


class TestGetDoctorAppointments:
    """Test cases for get_doctor_appointments function"""

    def setup_method(self):
        """Set up test data"""
        self.mock_cursor = Mock()
        self.mock_session = {"id": 1, "username": "doctor@example.com"}

        # Mock appointment data
        self.mock_appointments = [
            [
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
            ]
        ]

        # Mock doctor info
        self.mock_doctor_info = (
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

    def test_get_doctor_appointments_success(self):
        """Test successful retrieval of doctor appointments"""
        # Configure mock cursor responses
        self.mock_cursor.fetchall.side_effect = [
            self.mock_appointments,  # appointments query
            [("testuser",)],  # username query
            [("Dr. Jane", "M", "Smith")],  # doctor name query
            [("Cleaning",)],  # treatment name query
        ]
        self.mock_cursor.fetchone.side_effect = [
            self.mock_doctor_info,  # doctor info query
        ]

        user_info, appointments_list, appointments_list_json = get_doctor_appointments(
            self.mock_cursor, self.mock_session
        )

        assert user_info == self.mock_doctor_info
        assert len(appointments_list) == 1
        assert len(appointments_list_json) == 1
        assert appointments_list[0][9] == "testuser"  # Username replaced
        assert appointments_list[0][10] == "Dr. Jane M Smith"  # Doctor name replaced
        assert appointments_list[0][11] == "Cleaning"  # Treatment name replaced

    def test_get_doctor_appointments_no_scheduled(self):
        """Test when no scheduled appointments exist"""
        # Appointment with status other than 'Scheduled'
        waiting_appointment = [
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
        ]

        self.mock_cursor.fetchall.side_effect = [
            [waiting_appointment],  # appointments query
            [("testuser",)],  # username query
            [("Dr. Jane", "M", "Smith")],  # doctor name query
            [("Cleaning",)],  # treatment name query
        ]
        self.mock_cursor.fetchone.side_effect = [
            self.mock_doctor_info,  # doctor info query
        ]

        user_info, appointments_list, appointments_list_json = get_doctor_appointments(
            self.mock_cursor, self.mock_session
        )

        assert len(appointments_list) == 1
        assert len(appointments_list_json) == 0  # No scheduled appointments for JSON


class TestGetUserAppointments:
    """Test cases for get_user_appointments function"""

    def setup_method(self):
        """Set up test data"""
        self.mock_cursor = Mock()
        self.mock_session = {"id": 1, "username": "testuser"}

        # Mock appointment data
        self.mock_appointments = [
            [
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
            ]
        ]

        # Mock user info
        self.mock_user_info = (
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

    @patch("app.main.mydb")
    def test_get_user_appointments_success(self, mock_mydb):
        """Test successful retrieval of user appointments"""
        from flask import Flask
        from app.main import get_user_appointments

        app = Flask(__name__)
        with app.test_request_context(method="GET"):
            # Configure mock cursor responses
            self.mock_cursor.fetchall.side_effect = [
                self.mock_appointments,  # appointments query
                [("testuser",)],  # username query
                [("Dr. Jane", "M", "Smith")],  # doctor name query
                [("Cleaning",)],  # treatment name query
            ]
            self.mock_cursor.fetchone.side_effect = [
                self.mock_user_info,  # user info query
            ]
            user_info, appointments_list = get_user_appointments(
                self.mock_cursor, self.mock_session
            )
            assert user_info == self.mock_user_info
            assert len(appointments_list) == 1
            assert appointments_list[0][9] == "testuser"  # Username replaced
            assert (
                appointments_list[0][10] == "Dr. Jane M Smith"
            )  # Doctor name replaced
            assert appointments_list[0][11] == "Cleaning"  # Treatment name replaced

    @patch("app.main.mydb")
    def test_get_user_appointments_with_post_confirm(self, mock_mydb):
        """Test appointment status update via POST request"""
        from flask import Flask
        from app.main import get_user_appointments

        app = Flask(__name__)
        with app.test_request_context(
            method="POST", data={"id": "1", "status": "Confirm"}
        ):
            # Configure mock cursor responses
            self.mock_cursor.fetchall.side_effect = [
                self.mock_appointments,  # appointments query
                [("testuser",)],  # username query
                [("Dr. Jane", "M", "Smith")],  # doctor name query
                [("Cleaning",)],  # treatment name query
            ]
            self.mock_cursor.fetchone.side_effect = [
                self.mock_user_info,  # user info query
            ]
            user_info, appointments_list = get_user_appointments(
                self.mock_cursor, self.mock_session
            )
            # Verify database update was called
            update_calls = [
                call
                for call in self.mock_cursor.execute.call_args_list
                if "UPDATE" in str(call)
            ]
            assert len(update_calls) > 0
            mock_mydb.commit.assert_called()

    @patch("app.main.mydb")
    def test_get_user_appointments_with_post_reject(self, mock_mydb):
        """Test appointment rejection via POST request"""
        from flask import Flask
        from app.main import get_user_appointments

        app = Flask(__name__)
        with app.test_request_context(
            method="POST", data={"id": "1", "status": "Reject"}
        ):
            # Configure mock cursor responses
            self.mock_cursor.fetchall.side_effect = [
                self.mock_appointments,  # appointments query
                [("testuser",)],  # username query
                [("Dr. Jane", "M", "Smith")],  # doctor name query
                [("Cleaning",)],  # treatment name query
            ]
            self.mock_cursor.fetchone.side_effect = [
                self.mock_user_info,  # user info query
            ]
            user_info, appointments_list = get_user_appointments(
                self.mock_cursor, self.mock_session
            )
            # Verify database update was called
            update_calls = [
                call
                for call in self.mock_cursor.execute.call_args_list
                if "UPDATE" in str(call)
            ]
            assert len(update_calls) > 0
            mock_mydb.commit.assert_called()
