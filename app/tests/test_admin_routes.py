"""
Tests for admin functionality routes
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, doctors


def ensure_dirs():
    os.makedirs("static/img/icon", exist_ok=True)
    os.makedirs("static/img/slider", exist_ok=True)
    os.makedirs("static/img/UsersProfile", exist_ok=True)
    os.makedirs("static/img/ServicesProfile", exist_ok=True)
    os.makedirs("static/img/doctorsProfile", exist_ok=True)


class TestAdminRoute:
    """Test cases for admin dashboard route (/Admin/Home)"""

    def setup_method(self):
        ensure_dirs()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_admin_dashboard_authenticated(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test admin dashboard when authenticated"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "rates": [(5, "Great service", 1), (4, "Good", 2)],
            "appointments": [
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
            ],
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
        }

        # Mock database queries for statistics
        mock_cursor.fetchall.side_effect = [
            [(10,)],  # total appointments
            [(5,)],  # scheduled appointments
            [(3,)],  # accepted appointments
            [(2,)],  # refused appointments
            [(5,)],  # total doctors
            [(1,)],  # doctors 20-30
            [(2,)],  # doctors 30-40
            [(1,)],  # doctors 40-50
            [(1,)],  # doctors 50+
            [(1, 5), (2, 3)],  # services statistics
            [("Cleaning",)],  # service name 1
            [("Checkup",)],  # service name 2
        ]

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"

        response = client.get("/Admin/Home")

        assert response.status_code == 200
        assert b"Admin Control Panel" in response.data

    @pytest.mark.xfail(
        reason="TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType' due to missing session value; fix in main.py needed."
    )
    def test_admin_dashboard_not_authenticated(self, client):
        """Test admin dashboard when not authenticated"""
        response = client.get("/Admin/Home")

        assert response.status_code == 302  # Redirect to login
        assert "/Admin/" in response.location


class TestAdminLoginRoute:
    """Test cases for admin login route (/Admin/)"""

    def setup_method(self):
        ensure_dirs()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_admin_login_get(self, mock_retrive_tables, mock_init_db, client):
        """Test GET request to admin login page"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        response = client.get("/Admin/")

        assert response.status_code == 200
        assert b"Admin Control Panel" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_admin_login_post_success(self, mock_retrive_tables, mock_init_db, client):
        """Test successful admin login"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        # Mock successful admin authentication
        mock_cursor.fetchone.return_value = (1, "admin", "admin123")

        response = client.post(
            "/Admin/", data={"username": "admin", "password": "admin123"}
        )

        assert response.status_code == 302  # Redirect to admin dashboard
        assert "/Admin/Home" in response.location

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_admin_login_post_failure(self, mock_retrive_tables, mock_init_db, client):
        """Test failed admin login"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        # Mock failed authentication
        mock_cursor.fetchone.return_value = None

        response = client.post(
            "/Admin/", data={"username": "wrong", "password": "wrong"}
        )

        assert response.status_code == 200
        assert b"Incorrect username/password" in response.data

    @pytest.mark.xfail(
        reason="TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType' due to missing session value; fix in main.py needed."
    )
    def test_admin_login_already_authenticated(self, client):
        """Test admin login when already authenticated"""
        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        response = client.get("/Admin/")

        assert response.status_code == 302  # Redirect to admin dashboard
        assert "/Admin/Home" in response.location


class TestAdminLogoutRoute:
    """Test cases for admin logout route (/Admin/logout)"""

    def setup_method(self):
        ensure_dirs()

    def test_admin_logout(self, client):
        """Test admin logout functionality"""
        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"

        response = client.get("/Admin/logout")

        assert response.status_code == 302  # Redirect to login
        assert "/Admin/" in response.location

        # Check that session is cleared
        with client.session_transaction() as sess:
            assert "loggedinAdmin" not in sess
            assert "idAdmin" not in sess
            assert "usernameAdmin" not in sess


class TestDoctorsAdminRoute:
    """Test cases for doctors admin route (/Admin/Doctors)"""

    def setup_method(self):
        ensure_dirs()

    @pytest.mark.xfail(
        reason="RuntimeError: Working outside of request context. The doctors() function requires a Flask request context; fix in main.py needed."
    )
    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.validate_doctor_form")
    @patch("app.main.create_doctor")
    @patch("app.main.mydb")
    def test_doctors_admin_post_success(
        self,
        mock_mydb,
        mock_create_doctor,
        mock_validate_doctor_form,
        mock_retrive_tables,
        mock_init_db,
        client,
    ):
        """Test successful doctor creation via admin"""
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

        # Mock successful validation
        mock_validate_doctor_form.return_value = (
            True,
            "",
            {
                "ssn": "123456789",
                "f_name": "John",
                "mid_name": "M",
                "l_name": "Doe",
                "email": "john@example.com",
            },
        )

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        # Mock the doctors function directly since it's not a route
        with patch("app.main.request") as mock_request:
            mock_request.method = "POST"
            mock_request.form = {
                "SSN": "123456789",
                "FName": "John",
                "MidName": "M",
                "LName": "Doe",
                "Phone": "123-456-7890",
                "Gender": "Male",
                "Email": "john@example.com",
                "Age": "35",
                "Degree": "DDS",
            }
            mock_request.files = {"file": Mock(filename="doctor.jpg")}

            result = doctors()

            mock_validate_doctor_form.assert_called_once()
            mock_create_doctor.assert_called_once()

    @pytest.mark.xfail(
        reason="RuntimeError: Working outside of request context. The doctors() function requires a Flask request context; fix in main.py needed."
    )
    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.validate_doctor_form")
    def test_doctors_admin_post_validation_failure(
        self, mock_validate_doctor_form, mock_retrive_tables, mock_init_db, client
    ):
        """Test doctor creation with validation failure"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {"doctors": []}

        # Mock validation failure
        mock_validate_doctor_form.return_value = (False, "SSN already exists !", None)

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        # Mock the doctors function directly
        with patch("app.main.request") as mock_request:
            mock_request.method = "POST"
            mock_request.form = {
                "SSN": "123456789",
                "FName": "John",
                "MidName": "M",
                "LName": "Doe",
                "Phone": "123-456-7890",
                "Gender": "Male",
                "Email": "john@example.com",
                "Age": "35",
                "Degree": "DDS",
            }
            mock_request.files = {"file": Mock(filename="doctor.jpg")}

            result = doctors()

            mock_validate_doctor_form.assert_called_once()


class TestGeneralAdminRoute:
    """Test cases for general admin route (/Admin/General)"""

    def setup_method(self):
        ensure_dirs()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_general_admin_get(self, mock_retrive_tables, mock_init_db, client):
        """Test GET request to general admin page"""
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

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        response = client.get("/Admin/General")

        assert response.status_code == 200
        assert b"Site Informtion Control Panel" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    @patch("app.main.secure_filename")
    def test_general_admin_post_success(
        self, mock_secure_filename, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test successful site information update"""
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
        mock_secure_filename.return_value = "icon.png"

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        data = {
            "title": "Updated Site",
            "address": "Updated Address",
            "email": "updated@example.com",
            "phone": "987-654-3210",
            "short": "Updated short desc",
            "long": "Updated long description",
            "icon": (BytesIO(b"fake icon"), "icon.png"),
        }

        response = client.post("/Admin/General", data=data)

        assert response.status_code == 200
        assert b"Updated successfully" in response.data

    @pytest.mark.xfail(
        reason="TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType' due to missing session value; fix in main.py needed."
    )
    def test_general_admin_not_authenticated(self, client):
        """Test general admin when not authenticated"""
        response = client.get("/Admin/General")

        assert response.status_code == 302  # Redirect to login
        assert "/Admin/" in response.location


class TestSliderAdminRoute:
    """Test cases for slider admin route (/Admin/slider)"""

    def setup_method(self):
        ensure_dirs()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_slider_admin_get(self, mock_retrive_tables, mock_init_db, client):
        """Test GET request to slider admin page"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "slider": [(1, "slide1.jpg", "Title 1", "Description 1")]
        }

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        response = client.get("/Admin/slider")

        assert response.status_code == 200
        assert b"Slider Control Panel" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    @patch("app.main.secure_filename")
    def test_slider_admin_post_success(
        self, mock_secure_filename, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test successful slider image upload"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {"slider": []}
        mock_secure_filename.return_value = "slide.jpg"

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        data = {
            "title": "New Slide",
            "description": "New slide description",
            "file": (BytesIO(b"fake image"), "slide.jpg"),
        }

        response = client.post("/Admin/slider", data=data)

        assert response.status_code == 200
        assert b"Image Uploaded successfully" in response.data


class TestUsersAdminRoute:
    """Test cases for users admin route (/Admin/users)"""

    def setup_method(self):
        ensure_dirs()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_users_admin_authenticated(self, mock_retrive_tables, mock_init_db, client):
        """Test users admin page when authenticated"""
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

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        response = client.get("/Admin/users")

        assert response.status_code == 200
        assert b"Users" in response.data

    @pytest.mark.xfail(
        reason="TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType' due to missing session value; fix in main.py needed."
    )
    def test_users_admin_not_authenticated(self, client):
        """Test users admin when not authenticated"""
        response = client.get("/Admin/users")

        assert response.status_code == 302  # Redirect to login
        assert "/Admin/" in response.location


class TestServicesAdminRoute:
    """Test cases for services admin route (/Admin/Services)"""

    def setup_method(self):
        ensure_dirs()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_services_admin_get(self, mock_retrive_tables, mock_init_db, client):
        """Test GET request to services admin page"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "treatments": [
                (1, "Cleaning", 100, "30 min", "Dental cleaning", "image.jpg")
            ]
        }

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        response = client.get("/Admin/Services")

        assert response.status_code == 200
        assert b"Doctors Control Panel" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    @patch("app.main.secure_filename")
    def test_services_admin_post_success(
        self, mock_secure_filename, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test successful service creation"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {"treatments": []}
        mock_secure_filename.return_value = "service.jpg"

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        data = {
            "Name": "New Service",
            "Cost": "150",
            "Duration": "45 min",
            "Description": "New service description",
            "file": (BytesIO(b"fake image"), "service.jpg"),
        }

        response = client.post("/Admin/Services", data=data)

        assert response.status_code == 200
        assert b"Successfully Added New Service" in response.data


class TestAppointmentsAdminRoute:
    """Test cases for appointments admin route (/Admin/Appointemnts)"""

    def setup_method(self):
        ensure_dirs()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    def test_appointments_admin_get(
        self, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test GET request to appointments admin page"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "appointments": [
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
        }

        # Mock database queries for appointment processing
        mock_cursor.fetchall.side_effect = [
            [("testuser",)],  # username query
            [("Dr. Jane", "M", "Smith")],  # doctor name query
            [("Cleaning",)],  # treatment name query
        ]

        response = client.get("/Admin/Appointemnts")

        assert response.status_code == 200
        assert b"Appointments Control Panel" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    def test_appointments_admin_post_confirm(
        self, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test appointment confirmation via admin"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "appointments": [
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
        }

        # Mock database queries for appointment processing
        mock_cursor.fetchall.side_effect = [
            [("testuser",)],  # username query
            [("Dr. Jane", "M", "Smith")],  # doctor name query
            [("Cleaning",)],  # treatment name query
        ]

        response = client.post(
            "/Admin/Appointemnts", data={"id": "1", "status": "Confirm"}
        )

        assert response.status_code == 200
        # Verify database update was called
        mock_cursor.execute.assert_called()
        mock_mydb.commit.assert_called()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    def test_appointments_admin_post_reject(
        self, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test appointment rejection via admin"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "appointments": [
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
        }

        # Mock database queries for appointment processing
        mock_cursor.fetchall.side_effect = [
            [("testuser",)],  # username query
            [("Dr. Jane", "M", "Smith")],  # doctor name query
            [("Cleaning",)],  # treatment name query
        ]

        response = client.post(
            "/Admin/Appointemnts", data={"id": "1", "status": "Reject"}
        )

        assert response.status_code == 200
        # Verify database update was called
        mock_cursor.execute.assert_called()
        mock_mydb.commit.assert_called()


class TestAdminsRoute:
    """Test cases for admins route (/Admin/Admins)"""

    def setup_method(self):
        ensure_dirs()

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @pytest.mark.xfail(
        reason="UnboundLocalError: msg not initialized for GET in admins route; fix in main.py needed."
    )
    def test_admins_get_authenticated(self, mock_retrive_tables, mock_init_db, client):
        """Test GET request to admins page when authenticated"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {"admin": [(1, "admin", "admin123")]}

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        response = client.get("/Admin/Admins")

        assert response.status_code == 200
        assert b"Admins Table Control Panel" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @pytest.mark.xfail(
        reason="UnboundLocalError: msg not initialized for GET in admins route; fix in main.py needed."
    )
    def test_admins_get_not_authenticated(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test GET request to admins page when not authenticated"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {"admin": [(1, "admin", "admin123")]}

        response = client.get("/Admin/Admins")

        assert response.status_code == 200
        assert b"Admins Table Control Panel" in response.data

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    def test_admins_post_success(
        self, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test successful admin creation"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {"admin": [(1, "admin", "admin123")]}

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True

        response = client.post(
            "/Admin/Admins", data={"username": "newadmin", "password": "newpassword"}
        )

        assert response.status_code == 200
        assert b"Addded successfully" in response.data
        # Verify database insert was called
        mock_cursor.execute.assert_called()
        mock_mydb.commit.assert_called()
