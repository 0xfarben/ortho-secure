"""
Pytest configuration and fixtures for Flask application testing
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from werkzeug.datastructures import FileStorage
import io

# Import the Flask app (assuming main.py is the module)
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.main import app, init_db
except ImportError:
    # Fallback for CI/CD environment
    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    from app.main import app, init_db


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing
    app.config["SECRET_KEY"] = "test-secret-key"

    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_db():
    """Mock database connection and cursor"""
    mock_db = Mock()
    mock_cursor = Mock()

    # Mock common database operations
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.execute.return_value = None
    mock_db.commit.return_value = None

    return mock_db, mock_cursor


@pytest.fixture
def mock_db_tables():
    """Mock database tables data"""
    return {
        "site_information": [
            "Test Site",
            "Test Address",
            "test@example.com",
            "123-456-7890",
            "Short desc",
            "Long description",
        ],
        "rates": [(5, "Great service", 1), (4, "Good", 2)],
        "treatments": [(1, "Cleaning", 100, "30 min", "Dental cleaning", "image.jpg")],
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
        "admin": [(1, "admin", "admin123")],
    }


@pytest.fixture
def mock_session():
    """Mock Flask session"""
    return {
        "loggedin": False,
        "id": None,
        "username": None,
        "doctor": False,
        "loggedinAdmin": False,
        "idAdmin": None,
        "usernameAdmin": None,
    }


@pytest.fixture
def mock_file_upload():
    """Mock file upload for testing"""

    def create_mock_file(filename="test.jpg", content=b"fake image content"):
        return FileStorage(
            stream=io.BytesIO(content), filename=filename, content_type="image/jpeg"
        )

    return create_mock_file


@pytest.fixture
def mock_mail():
    """Mock Flask-Mail"""
    with patch("app.main.mail") as mock_mail:
        mock_mail.send.return_value = None
        yield mock_mail


@pytest.fixture
def mock_secure_filename():
    """Mock secure_filename function"""
    with patch("app.main.secure_filename") as mock_secure:
        mock_secure.side_effect = lambda x: x  # Return filename as-is
        yield mock_secure


@pytest.fixture
def mock_retrive_tables():
    """Mock retrive_tables function"""

    def mock_retrive_tables_func(cursor):
        return {
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
            "admin": [(1, "admin", "admin123")],
        }

    with patch("app.main.retrive_tables", side_effect=mock_retrive_tables_func):
        yield mock_retrive_tables_func


@pytest.fixture
def mock_mysql_connector():
    """Mock mysql_connector function"""

    def mock_connector():
        mock_db = Mock()
        mock_cursor = Mock()

        # Configure common return values
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_cursor.execute.return_value = None
        mock_db.commit.return_value = None

        return mock_db, mock_cursor

    with patch("app.main.mysql_connector", side_effect=mock_connector):
        yield mock_connector


@pytest.fixture
def authenticated_user_session():
    """Mock authenticated user session"""
    return {
        "loggedin": True,
        "id": 1,
        "username": "testuser",
        "doctor": False,
        "title": "Test Site",
        "address": "Test Address",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "short": "Short desc",
        "long": "Long description",
    }


@pytest.fixture
def authenticated_doctor_session():
    """Mock authenticated doctor session"""
    return {
        "loggedin": True,
        "id": 1,
        "ssn": "123456789",
        "username": "doctor@example.com",
        "doctor": True,
        "title": "Test Site",
        "address": "Test Address",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "short": "Short desc",
        "long": "Long description",
    }


@pytest.fixture
def authenticated_admin_session():
    """Mock authenticated admin session"""
    return {"loggedinAdmin": True, "idAdmin": 1, "usernameAdmin": "admin"}


@pytest.fixture
def mock_os_getenv():
    """Mock os.getenv for environment variables"""

    def mock_getenv(key, default=None):
        env_vars = {
            "SECRET_KEY": "test-secret-key",
            "MAIL_PASSWORD": "test-mail-password",
        }
        return env_vars.get(key, default)

    with patch("os.getenv", side_effect=mock_getenv):
        yield mock_getenv


@pytest.fixture
def mock_secrets():
    """Mock secrets module for predictable random generation"""
    with patch("app.main.secrets") as mock_secrets:
        mock_secrets.choice.return_value = 8  # Fixed length for testing
        mock_secrets.choice.side_effect = lambda x: (
            x[0] if hasattr(x, "__getitem__") else 8
        )
        yield mock_secrets


@pytest.fixture(autouse=True)
def reset_global_db():
    """Reset global database variables before each test"""
    import app.main

    app.main.mydb = None
    app.main.mycursor = None
