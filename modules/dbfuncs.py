import pymongo
from pymongo import MongoClient
from bson import Binary
import base64
import gridfs
import datetime
import os


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

    def encode_image(self, image):
        """
        Encodes an image from binary to Base64 string

        :param image: image name
        :type image: image

        :return: encoded image
        :type: base64
        """
        # Read the image file and encode it to Base64
        with open(image, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        return base64_image

    def decode_image(self, image):
        """
        Decodes an image from Base64 to binary

        :param image: image name
        :type image: image

        :return: decoded image
        :type: binary
        """
        binary_image = base64.b64decode(image)

        # Save the image to a file
        with open("retrieved_example.jpg", "wb") as output_file:
            output_file.write(binary_image)

        return output_file

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
        stored_file = self.fs.get(file_id)  # Get the file by its ID
        with open("output_image.jpg", "wb") as output_file:
            output_file.write(stored_file.read())

    def getImageByFilename(self, filename):
        """
        Retrieves the image file with its associated filename or gemini-generated filename

        :param filename: Filename or Gemini Filename
        :type filename: string

        :return: image
        :rtype: image
        """
        # Validate if filename exists
        if not filename:
            raise ValueError("Filename cannot be empty")

        # Strip whitespace
        filename = filename.strip()

        # Find image within the collection
        try:
            # Find file by original filename
            file = self.fs.find_one({"file_path": filename})
            if not file:
                # Fine file by gemini filename
                file = self.fs.find_one({"metadata.geminiFilename": filename})
            if file:
                # Return image if file is found
                return file.read()
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
            return (
                f"Theme '{theme_name}' added successfully with ID: {result.inserted_id}"
            )
        except Exception as e:
            return f"Error adding theme: {e}"

    def add_critique(self, file_id, critique):
        """
        Add the critique to the database with the associated image

        :param file_id: ObjectId of the image
        :type file_id: string
        :param critique: critique generated from Gemini AI
        :type critique: dict

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


# FOR TESTING PURPOSES (DELETE AFTER)
if __name__ == "__main__":
    # Initialize the MongoDBHandler
    db_handler = MongoDBHandler()

    # # # Drop the database
    # db_name = "my_database"
    # db_handler.client.drop_database(db_name)
    # print(f"Database '{db_name}' has been deleted.")

    while True:
        print("\n=== Image Functions Test Menu ===")
        print("1. Store image")
        print("2. Encode Image")
        print("3. Decode Image")
        print("4. Store Image with GridFS")
        print("5. Retrieve Image with GridFS")
        print("6. Add theme")
        print("7. Get all images")
        print("x. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            try:
                stored_image = db_handler.add_critique(
                    "_DSC3940.JPG",
                    "This is the test critique",
                    "This is the test theme",
                )
            except Exception as e:
                print(f"Error storing image: {e}")
        elif choice == "2":
            try:
                encoded_image = db_handler.encode_image("_DSC3940.JPG")
            except Exception as e:
                print(f"Error encoding image: {e}")
        elif choice == "3":
            try:
                decoded_image = db_handler.decode_image(encoded_image)
                print(decoded_image)
            except Exception as e:
                pass

        elif choice == "4":
            try:
                img = input("Enter filename: ")
                file_id = db_handler.add_image(img, "file/iamtestingthis")
            except Exception as e:
                print(f"Error storing image: {e}")

        elif choice == "5":
            try:
                file_id = db_handler.retreive_image(file_id)
            except Exception as e:
                print(f"Error storing image: {e}")

        elif choice == "6":
            try:
                addedTheme = db_handler.add_theme("Test theme", "test description")
                print(addedTheme)
            except Exception as e:
                print(f"Error adding theme: {e}")

        elif choice == "7":
            try:
                allImages = db_handler.getAllImages()
                print(allImages)
            except Exception as e:
                print(f"Error fetching all images: {e}")
        elif choice == "x":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter a valid option.")

    # Close the connection
    db_handler.close_connection()
