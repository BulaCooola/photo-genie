# Authors: Branden Bulatao, Matthew Kribs
# Date: 12/2024
# Description: This python file is a test file that tests database functions such as adding and fetching images and themes.

import pytest
from pymongo import MongoClient
from dbfuncs import MongoDBHandler  # Replace with the correct import


@pytest.fixture(scope="module")
def db_handler():
    """Fixture to initialize MongoDBHandler and connect to test database."""
    # Create a MongoDBHandler instance for testing
    test_db_handler = MongoDBHandler(
        uri="mongodb://localhost:27017/", database_name="test_images_db"
    )

    # Yield the db_handler instance to the tests
    yield test_db_handler

    # Clean up the database after all tests in the module are finished
    test_db_handler.client.drop_database("test_images_db")
    print("Test database dropped.")


def test_add_image(db_handler):
    """
    Test add_image method
    """
    file_id = db_handler.add_image("imgs/test_image1.jpg")

    # Assert the expected return value to exist
    assert file_id is not None

    # Check if the method was called with the correct argument
    image_in_db = db_handler.getImageByFilename("test_image1.jpg")
    assert image_in_db is not None


def test_get_all_images(db_handler):
    """
    Test getAllImages method
    """
    db_handler.add_image("imgs/test_image2.jpg")

    images = db_handler.getAllImages()

    # Assert the expected return value
    assert len(images) >= 2
    assert any(img["filename"] == "test_image2.jpg" for img in images)


def test_delete_image(db_handler):
    """
    Test delete_image method.
    """
    file = db_handler.getImageByFilename("test_image2.jpg")

    print(file["_id"])
    # Delete the image by its file_id
    deletion_result = db_handler.delete_image(file["_id"])

    # Assert the image was deleted successfully
    assert deletion_result is True

    # Try retrieving the image, which should not be found
    try:
        check = db_handler.getImageByFileID(file["_id"])
        print(check)
        assert check is False, "Expected FileNotFoundError, but the file was found."
    except FileNotFoundError:
        # Assert that FileNotFoundError was raised because the image no longer exists
        pass


def test_add_theme(db_handler):
    """
    Test add_theme method
    """
    theme_response = db_handler.add_theme("Test theme", "test description")

    print(theme_response)
    # Assert the expected return value
    assert theme_response is not None


def test_get_theme(db_handler):
    """
    Test if the added theme can be retrieved.
    """
    theme_name = "Another Test Theme"
    theme_description = "Description for the second test theme."

    # Add the theme
    theme = db_handler.add_theme(theme_name, theme_description)
    print("id -->", theme)

    # Retrieve themes from the database
    retrieved_theme = db_handler.getThemeById(theme)
    print(retrieved_theme)

    # Assert that the theme is present
    assert retrieved_theme
    assert retrieved_theme["theme_name"] == theme_name


if __name__ == "__main__":
    pytest.main()
