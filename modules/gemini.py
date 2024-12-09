# Authors: Branden Bulatao, Matthew Kribs
# Date: 12/2024
# Description: This module handles all Gemini API calls. It handles any theme generations and photo critiques.

import google.generativeai as genai
import os
import json
import datetime
from dotenv import load_dotenv


# https://ai.google.dev/api/files#files_create_image-PYTHON


class Gemini:
    def __init__(self, env_file=".env"):
        """
        Initialize the GeminiFileHandler class.

        :param env_file: Path to the .env file containing API keys
        :type env_file: str
        """
        self._env_file = env_file  # Holds env file
        self._model = None  # Slower Model
        self._model2 = None  # Faster Model

    def configure_api(self):
        """
        Load API keys and configure generative AI and Vision API clients.
        """
        load_dotenv(self._env_file)  # Load the env file to get key
        gemini_api_key = os.getenv("GEMINI_API_KEY")  # Get the key
        if not gemini_api_key:  # Handle if key is not in the env file
            raise ValueError("API key is not set in .env file")
        genai.configure(api_key=gemini_api_key)  # Configure Gemini
        self._model = genai.GenerativeModel("gemini-1.5-flash")  # Main model
        self._model2 = genai.GenerativeModel("gemini-1.5-flash-8b")  # Secondary Model
        print("Gemini API configured successfully")

    def generate_theme(self):
        """
        Generate a photography theme using the Gemini model.

        :return: The generated theme as a Python dictionary
        :rtype: dict
        """
        # Generate response for photography ideas
        prompt = [
            "Can you give me a four unique photography ideas? Make each idea a sentence of what I should shoot and/or how I should shoot something."
            "Provide the response in JSON with keys as the theme title."
        ]
        response = self._model2.generate_content(prompt)

        # Log the number of tokens used
        print(self._model2.count_tokens(prompt))

        # Strip response whitespace
        result = response.text.strip()
        if result.startswith("```json") and result.endswith("```"):
            result = result[7:-3].strip()
        # Parse the response text into a dictionary
        try:
            # Parse returned JSON string into dictionary
            result_dict = json.loads(result)
            result_dict["critique_date"] = datetime.datetime.now()
            return result_dict
        except json.JSONDecodeError:
            # Handle cases where the response is not valid JSON (fallback)
            print("Error parsing the JSON response.")
            return None

    def critique_photo(self, file_path, theme, theme_description):
        """
        Provide critique on the composition of a photo.

        :param file_path: Path to the photo to critique
        :type file_path: str
        :param theme: Theme/photo idea of the picture
        :type theme: str | None
        :param theme_description: More info about the theme
        :type theme_description: str | None

        :return: Critique as a dictionary containing positive feedback and areas of improvement
        :rtype: dict
        """
        # Handle unprovided data
        if not file_path:
            return ValueError("The file_path parameter cannot be empty.")

        print("Filepath: ", file_path)
        print("Theme: ", theme)

        # Upload file into Gemini to critique
        uploaded_file = self.upload_file(file_path)
        try:
            if not theme:
                print("\nGenerating critique...\n")
                # Generate Critique
                response = self._model.generate_content(
                    [
                        uploaded_file,
                        "\n\n",
                        "Can you critique the composition of this photo? Lighting, story, etc?"
                        "Provide the response in JSON format with keys 'positive', 'negative', and 'overview'.",
                    ]
                )
            else:
                print("\nGenerating critique...\n")
                # Generate Critique with theme
                response = self._model.generate_content(
                    [
                        uploaded_file,
                        "\n\n",
                        f"The theme that the image is based off of is: \n{theme}: {theme_description}\n",
                        "Can you critique the composition of this photo (Lighting, story, etc?), and how accurate is the photo from the theme?"
                        "Provide the response in JSON format with keys 'positive', 'negative', and 'overview'.",
                    ]
                )
            # Strip the unnecessary parts of the result
            result = response.text.strip()
            if result.startswith("```json") and result.endswith("```"):
                result = result[7:-3].strip()
            # Parse the response text into a dictionary
            try:
                # Parse returned JSON string into dictionary
                critique = json.loads(result)
                print("Critique parsed and formatted")
                return critique
            except json.JSONDecodeError:
                # Handle cases where the response is not valid JSON (fallback)
                print("Error parsing the JSON response.")
                return None
        finally:
            # Delete file to save space after critique
            uploaded_file.delete()
            print(f"Deleted file: {uploaded_file.name}")

    def upload_file(self, file_path):
        """
        Upload a file to the generative AI service.

        :param file_path: Path to the file to upload
        :type file_path: str
        :return: Uploaded file object
        :rtype: File
        """
        myfile = genai.upload_file(file_path)
        print(f"Uploaded file: {myfile.name}")
        return myfile

    def delete_file(self, filename):
        """
        Delete file stored in the Gemini AI

        :param file: file name stored in gemini
        :type file: string

        :return: Boolean representing if file is deleted or not
        :rtype: boolean
        """
        # Handle unprovided data
        if not filename:
            raise ValueError("Name of file cannot be empty")

        try:
            my_file = genai.get_file(filename)
        except:
            print(f"Error finding file in Gemini")
            return False

        try:
            my_file.delete()
            return True
        except:
            print(f"Error deleting file in Gemini")
            return False

    def list_uploaded_files(self):
        files = genai.list_files()
        return [f.name for f in files]
