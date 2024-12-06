import pymongo
import gridfs
import datetime
import os
from io import BytesIO
from pymongo import MongoClient


class MongoDBHandler:
    def __init__(self, uri="mongodb://localhost:27017/", database_name="images_db"):
        """
        Initialize the MongoDBHandler class.

        :param uri: MongoDB connection URI
        :type uri: str
        :param database_name: Name of the database to connect to
        :type database_name: str
        """
        self.client = MongoClient(uri)
        self.database = self.client[database_name]
        self.themesCollection = self.database["themes"]  # Collection to store themes
        self.fs = gridfs.GridFS(
            self.database
        )  # Collection to store images (and critiques)
        print(
            f"Connected to MongoDB at {uri}, database: {database_name} with a collection: images"
        )

    def find_documents(self, collection_name, query=None):
        """
        Find documents in a collection.

        :param collection_name: Name of the collection
        :type collection_name: str
        :param query: Query to filter documents (default is None, which returns all documents)
        :type query: dict, optional
        :return: List of matching documents
        :rtype: list
        """
        collection = self.database[collection_name]
        return list(collection.find(query or {}))

    def list_collections(self):
        """
        List all collections in the database.

        :return: List of collection names
        :rtype: list
        """
        return self.database.list_collection_names()

    def add_image(self, image_path):
        file = self.fs.find_one({"file_path": image_path})

        if file:
            print(f"File already exists")
            return file_id

        with open(image_path, "rb") as file:
            file_id = self.fs.put(
                file,
                filename=os.path.basename(image_path),
                file_path=image_path,
                metadata={
                    "critique": {
                        "positive": None,
                        "improvement": None,
                        "overview": None,
                    },
                    "theme_id": None,
                },
            )

        print(file_id)
        return file_id

    def getAllImages(self):
        filesCollection = self.database["fs.files"]
        return list(
            filesCollection.find({}, {"_id": 1, "filename": 1, "uploadDate": 1})
        )

    def getImageByFileID(self, file_id):
        # Initilalize variable for collection
        fileCollection = self.database["fs.files"]
        # Find in the collection
        file = fileCollection.find_one({"_id": file_id})
        if not file:
            raise FileNotFoundError("File does not exist in the database")

        stored_file = self.fs.get(file_id)  # Get the file by its ID
        image_data = BytesIO(stored_file.read())  # Create in-memory file
        return image_data

    def getImageByFilename(self, filename):
        """
        Retrieves the image file with its associated filename or gemini-generated filename

        :param filename: Filename or Gemini Filename
        :type filename: string

        :return: image metadata
        :rtype: Any | None
        """
        # Validate if filename exists
        if not filename:
            raise ValueError("Filename cannot be empty")

        # Strip whitespace
        filename = filename.strip()

        # Find image within the collection
        fileCollection = self.database["fs.files"]
        try:
            # Find file by original filename
            file = fileCollection.find_one({"filename": filename})
            if file:
                # Return image if file is found
                return file
            else:
                print(f"No file found with filename {filename}")
                return None
        except Exception as e:
            print(f"Error retrieving image: {e}")
            return None

    def delete_image(self, file_id):
        """
        Finds and deletes image with provided file_id

        :param file_id: File ID image is associated with
        :type file_id: string

        :return: Boolean if the file was deleted or not
        :rtype: boolean
        """
        try:
            self.fs.delete(file_id)
            print(f"File with file_id {file_id} deleted successfully")
            return True
        except gridfs.errors.NoFile:
            print(f"File with file_id {file_id} not found.")
            return False
        except Exception as e:
            print(f"Error deleting image with file_id {file_id}")
            return False

    def add_theme(self, theme_name, description):
        """
        Adds a generated theme from Gemini into the database

        :param theme: A theme that Gemini AI generated that user wants to save for future
        :type theme: string

        :return: Response saying the theme added successfully
        :rtype: string
        """
        if not theme_name or not description:
            raise ValueError("Theme name and description cannot be empty")

        theme_data = {
            "theme_name": theme_name.strip(),
            "description": description.strip(),
            "time_added": datetime.datetime.now(),
        }

        try:
            # insert theme into themes collection
            result = self.themesCollection.insert_one(theme_data)
            # return (
            #     f"Theme '{theme_name}' added successfully with ID: {result.inserted_id}"
            # )
            return result.inserted_id
        except Exception as e:
            raise Exception(f"Error adding theme: {e}")

    def getAllThemes(self):
        """
        Gives a list of objects containing theme data (id, theme_name, theme_description)

        :return: List of objects containing theme data
        :rtype: list | None
        """
        themeCollection = self.themesCollection
        return list(
            themeCollection.find({}, {"_id": 1, "theme_name": 1, "description": 1})
        )

    def getThemeById(self, theme_id):
        """
        Finds a specified theme by ID

        :param theme_id: object id for the theme
        :type theme_id: string

        :return: theme data
        :rtype: object
        """
        if not theme_id:
            raise ValueError("Theme ID must be provided.")
        themeCollection = self.themesCollection

        try:
            # Find file by original filename
            file = themeCollection.find_one({"_id": theme_id})
            if file:
                # Return image if file is found
                return file
            else:
                print(f"No file found with theme id {theme_id}")
                return None
        except Exception as e:
            print(f"Error retrieving image: {e}")
            return None

    def add_critique(self, file_id, critique, theme_id=None):
        """
        Add the critique to the database with the associated image

        :param file_id: ObjectId of the image
        :type file_id: string
        :param critique: critique generated from Gemini AI
        :type critique: dict
        :param theme_id: theme id critique is based off
        :type theme_id: string | None

        :return: Result of insert_one function to fs.files
        :rtype: InsertOneResult
        """
        # validate if data is not empty
        if not file_id or not critique:
            raise ValueError("file_id, critique, and rating cannot be empty.")

        # validate if the file_id exists (find it in database)
        try:
            # Fetch the database
            fileCollection = self.database["fs.files"]
            # Find the stored image in database
            filename = fileCollection.find_one({"_id": file_id})
            # Handle if document is not found
            if not filename:
                raise LookupError("File_id not found in database")
        except FileNotFoundError as e:
            return f"Error finding file in database: {e}"

        try:
            # Insert critique data into the correct file
            result = fileCollection.update_one(
                {"_id": file_id},
                {
                    "$set": {
                        "metadata.critique.positive": critique["positive"],
                        "metadata.critique.improvement": critique["negative"],
                        "metadata.critique.overview": critique["overview"],
                        "metadata.theme_id": theme_id,
                    }
                },
            )

            return result
        except pymongo.errors.OperationFailure as e:
            print(f"Error adding critique data to file: {e}")

    def edit_critique(self, file_id, critique, rating):
        pass

    def close_connection(self):
        """
        Close the connection to MongoDB.
        """
        self.client.close()
        print("MongoDB connection closed.")
