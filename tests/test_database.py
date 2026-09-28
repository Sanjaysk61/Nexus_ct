from backend.database import test_database_connection as check_database_connection


def test_database_connection():
    database_name = check_database_connection()

    assert database_name == "nexus"