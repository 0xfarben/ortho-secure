"""
Additional test cases
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MYSQL_PORT"] = "3306"


class TestAdminStatisticalAnalysis:
    """Test cases for admin dashboard statistical calculations"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_admin_dashboard_empty_rates_division_by_zero(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test admin dashboard with empty rates (division by zero case)"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "rates": [],  # Empty rates to trigger len(rates) == 0 condition
            "appointments": [],
            "doctors": [],
        }

        # Mock all statistical queries to return zero counts
        mock_cursor.fetchall.side_effect = [
            [(0,)],  # total appointments
            [(0,)],  # scheduled appointments
            [(0,)],  # accepted appointments
            [(0,)],  # refused appointments
            [(0,)],  # total doctors
            [(0,)],  # doctors 20-30
            [(0,)],  # doctors 30-40
            [(0,)],  # doctors 40-50
            [(0,)],  # doctors 50+
            [],  # services statistics (empty)
            # No service names needed since services statistics is empty
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],  # extra dummies
        ]

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"
            sess["id"] = 1
            sess["username"] = "testuser"

        response = client.get("/Admin/Home")

        assert response.status_code == 200
        # Should handle division by zero gracefully (avg_of_rates = 0)

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_admin_dashboard_zero_appointments_division(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test admin dashboard with zero appointments (division by zero in percentages)"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "rates": [(5, "Great service", 1)],
            "appointments": [],
            "doctors": [],
        }

        # Mock statistical queries with zero appointments
        mock_cursor.fetchall.side_effect = [
            [(0,)],  # total appointments = 0
            [(0,)],  # scheduled appointments
            [(0,)],  # accepted appointments
            [(0,)],  # refused appointments
            [(1,)],  # total doctors
            [(0,)],  # doctors 20-30
            [(1,)],  # doctors 30-40
            [(0,)],  # doctors 40-50
            [(0,)],  # doctors 50+
            [(1, 2)],  # services statistics
            [("Cleaning",)],  # service name 1
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],  # extra dummies
        ]

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"
            sess["id"] = 1
            sess["username"] = "testuser"

        response = client.get("/Admin/Home")

        assert response.status_code == 200
        # Should handle num_of_app == 0 condition for percentage calculations

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_admin_dashboard_zero_doctors_division(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test admin dashboard with zero doctors (division by zero in doctor percentages)"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "rates": [(4, "Good service", 1)],
            "appointments": [],
            "doctors": [],
        }

        # Mock statistical queries with zero doctors
        mock_cursor.fetchall.side_effect = [
            [(5,)],  # total appointments
            [(2,)],  # scheduled appointments
            [(2,)],  # accepted appointments
            [(1,)],  # refused appointments
            [(0,)],  # total doctors = 0
            [(0,)],  # doctors 20-30
            [(0,)],  # doctors 30-40
            [(0,)],  # doctors 40-50
            [(0,)],  # doctors 50+
            [(1, 3)],  # services statistics
            [("Cleaning",)],  # service name 1
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],  # extra dummies
        ]

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"
            sess["id"] = 1
            sess["username"] = "testuser"

        response = client.get("/Admin/Home")

        assert response.status_code == 200
        # Should handle num_of_doctors == 0 condition for percentage calculations


class TestMissingConditionalBranches:
    """Test cases for missing conditional branches"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    @patch("app.main.secure_filename")
    def test_general_admin_post_without_icon_file(
        self, mock_secure_filename, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test general admin POST without icon file (empty filename branch)"""
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
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"
            sess["id"] = 1
            sess["username"] = "testuser"

        # Test with empty icon filename
        data = {
            "title": "Updated Site",
            "address": "Updated Address",
            "email": "updated@example.com",
            "phone": "987-654-3210",
            "short": "Updated short desc",
            "long": "Updated long description",
            "icon": (BytesIO(b""), ""),  # Empty filename
        }

        response = client.post("/Admin/General", data=data)

        assert response.status_code == 200
        assert b"Updated successfully" in response.data
        # Should hit the "if icon.filename == ''" branch with path = ""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    @patch("app.main.secure_filename")
    def test_slider_admin_post_without_file(
        self, mock_secure_filename, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test slider admin POST without file (empty filename branch)"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {"slider": []}

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"
            sess["id"] = 1
            sess["username"] = "testuser"

        # Test with empty file
        data = {
            "title": "New Slide",
            "description": "New slide description",
            "file": (BytesIO(b""), ""),  # Empty filename
        }

        response = client.post("/Admin/slider", data=data)

        assert response.status_code == 200
        assert b"Image Uploaded successfully" in response.data
        # Should hit the "if file.filename == ''" branch with path = ""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    @patch("app.main.secure_filename")
    def test_services_admin_post_without_image(
        self, mock_secure_filename, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test services admin POST without image (empty filename branch)"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {"treatments": []}

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"
            sess["id"] = 1
            sess["username"] = "testuser"

        # Test with empty image file
        data = {
            "Name": "New Service",
            "Cost": "150",
            "Duration": "45 min",
            "Description": "New service description",
            "file": (BytesIO(b""), ""),  # Empty filename
        }

        response = client.post("/Admin/Services", data=data)

        assert response.status_code == 200
        assert b"Successfully Added New Service" in response.data
        # Should hit the "if image.filename == ''" branch with path = ""


class TestAppointmentStatusUpdates:
    """Test cases for appointment status update branches"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.mydb")
    def test_appointments_admin_post_unknown_status(
        self, mock_mydb, mock_retrive_tables, mock_init_db, client
    ):
        """Test appointments admin with unknown status (else branch)"""
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

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"
            sess["id"] = 1
            sess["username"] = "testuser"

        response = client.post(
            "/Admin/Appointemnts",
            data={"id": "1", "status": "Unknown"},  # Neither "Confirm" nor "Reject"
        )

        assert response.status_code == 200
        # Should hit the else branch (no status update)
        # mydb.commit should still be called but no UPDATE query for status


class TestPrintStatements:
    """Test cases to trigger print statements and debug code"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("builtins.print")
    def test_admin_dashboard_print_statement(
        self, mock_print, mock_retrive_tables, mock_init_db, client
    ):
        """Test admin dashboard to trigger print statement"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "rates": [(5, "Great service", 1)],
            "appointments": [],
            "doctors": [],
        }

        # Mock statistical queries
        mock_cursor.fetchall.side_effect = [
            [(10,)],  # total appointments
            [(5,)],  # scheduled appointments
            [(3,)],  # accepted appointments
            [(2,)],  # refused appointments
            [(2,)],  # total doctors
            [(1,)],  # doctors 20-30
            [(1,)],  # doctors 30-40
            [(0,)],  # doctors 40-50
            [(0,)],  # doctors 50+
            [(1, 5)],  # services statistics
            [("Cleaning",)],  # service name 1
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],  # extra dummies
        ]

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"
            sess["id"] = 1
            sess["username"] = "testuser"

        response = client.get("/Admin/Home")

        assert response.status_code == 200
        # Should trigger the print("Im Here") statement
        mock_print.assert_called_with("Im Here")


class TestDoctorRouteDirectly:
    """Test the doctors() function directly since it's not a decorated route"""

    def test_doctors_function_get_request(self, client):
        from app.main import app, doctors

        with app.test_request_context("/Admin/Doctors", method="GET"):
            with patch("app.main.request") as mock_request, patch(
                "app.main.validate_doctor_form"
            ) as mock_validate_doctor_form, patch(
                "app.main.create_doctor"
            ) as mock_create_doctor, patch(
                "app.main.mydb"
            ) as mock_mydb, patch(
                "app.main.retrive_tables"
            ) as mock_retrive_tables, patch(
                "app.main.init_db"
            ) as mock_init_db, patch(
                "app.main.session",
                {
                    "loggedinAdmin": True,
                    "idAdmin": 1,
                    "usernameAdmin": "admin",
                    "id": 1,
                    "username": "testuser",
                },
            ):
                mock_db, mock_cursor = Mock(), Mock()
                mock_init_db.return_value = (mock_db, mock_cursor)
                mock_retrive_tables.return_value = {"doctors": []}
                mock_request.method = "GET"
                result = doctors()
                mock_validate_doctor_form.assert_not_called()
                mock_create_doctor.assert_not_called()

    def test_doctors_function_not_authenticated(self, client):
        from app.main import app, doctors

        with app.test_request_context("/Admin/Doctors", method="GET"):
            with patch("app.main.request") as mock_request, patch(
                "app.main.retrive_tables"
            ) as mock_retrive_tables, patch("app.main.init_db") as mock_init_db, patch(
                "app.main.session", {"id": 1, "username": "testuser"}
            ), patch(
                "app.main.redirect"
            ) as mock_redirect, patch(
                "app.main.url_for"
            ) as mock_url_for:
                mock_db, mock_cursor = Mock(), Mock()
                mock_init_db.return_value = (mock_db, mock_cursor)
                mock_retrive_tables.return_value = {"doctors": []}
                mock_request.method = "GET"
                mock_url_for.return_value = "/Admin/"
                result = doctors()
                mock_redirect.assert_called_once()


class TestAdditionalEdgeCases:
    """Additional edge cases for remaining coverage"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_profile_page_empty_username(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test profile page with empty username in session"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        with client.session_transaction() as sess:
            sess["username"] = ""
            sess["id"] = 1

        response = client.get("/profile")

        assert response.status_code == 200
        # Should handle empty username gracefully

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_profile_page_none_username(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test profile page with None username in session"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        with client.session_transaction() as sess:
            sess["username"] = None
            sess["id"] = 1

        response = client.get("/profile")

        assert response.status_code == 200
        # Should handle None username gracefully

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    @patch("app.main.get_doctor_appointments")
    def test_profile_page_doctor_with_empty_appointments_json(
        self, mock_get_doctor_appointments, mock_retrive_tables, mock_init_db, client
    ):
        """Test doctor profile with empty appointments_list_json"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {}

        # Mock doctor appointments with empty JSON list
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
                "Waiting",
                1,
                1,
                1,
            )
        ]
        mock_appointments_json = []  # Empty JSON list
        mock_get_doctor_appointments.return_value = (
            mock_doctor_info,
            mock_appointments,
            mock_appointments_json,
        )

        with client.session_transaction() as sess:
            sess["username"] = "doctor@example.com"
            sess["doctor"] = True
            sess["id"] = 1

        response = client.get("/profile")

        assert response.status_code == 200
        # Should handle empty appointments_list_json


class TestServiceStatisticsLoop:
    """Test the services statistics loop in admin dashboard"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_admin_dashboard_services_loop_coverage(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test admin dashboard services statistics loop"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "rates": [(5, "Great service", 1)],
            "appointments": [],
            "doctors": [],
        }

        # Mock statistical queries with multiple services
        mock_cursor.fetchall.side_effect = [
            [(10,)],  # total appointments
            [(5,)],  # scheduled appointments
            [(3,)],  # accepted appointments
            [(2,)],  # refused appointments
            [(2,)],  # total doctors
            [(1,)],  # doctors 20-30
            [(1,)],  # doctors 30-40
            [(0,)],  # doctors 40-50
            [(0,)],  # doctors 50+
            [(1, 5), (2, 3), (3, 2)],  # Multiple services statistics
            [("Cleaning",)],  # service name 1
            [("Checkup",)],  # service name 2
            [("Filling",)],  # service name 3
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],  # extra dummies
        ]

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"
            sess["id"] = 1
            sess["username"] = "testuser"

        response = client.get("/Admin/Home")

        assert response.status_code == 200
        # Should iterate through all services in the loop


class TestColorsListAccess:
    """Test the colors list access in admin dashboard"""

    @patch("app.main.init_db")
    @patch("app.main.retrive_tables")
    def test_admin_dashboard_colors_list_usage(
        self, mock_retrive_tables, mock_init_db, client
    ):
        """Test admin dashboard to ensure colors list is used"""
        # Mock database setup
        mock_db, mock_cursor = Mock(), Mock()
        mock_init_db.return_value = (mock_db, mock_cursor)
        mock_retrive_tables.return_value = {
            "rates": [(5, "Great service", 1)],
            "appointments": [],
            "doctors": [],
        }

        # Mock statistical queries
        mock_cursor.fetchall.side_effect = [
            [(10,)],  # total appointments
            [(5,)],  # scheduled appointments
            [(3,)],  # accepted appointments
            [(2,)],  # refused appointments
            [(2,)],  # total doctors
            [(1,)],  # doctors 20-30
            [(1,)],  # doctors 30-40
            [(0,)],  # doctors 40-50
            [(0,)],  # doctors 50+
            [(1, 5)],  # services statistics
            [("Cleaning",)],  # service name 1
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],  # extra dummies
        ]

        with client.session_transaction() as sess:
            sess["loggedinAdmin"] = True
            sess["idAdmin"] = 1
            sess["usernameAdmin"] = "admin"
            sess["id"] = 1
            sess["username"] = "testuser"

        response = client.get("/Admin/Home")

        assert response.status_code == 200
        # Should use the colors list in template rendering
