# Authors: Branden Bulatao, Matthew Kribs, Hashil Patel
# Description: Test for Gemini file

import google.generativeai as genai
from google.cloud import vision
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
        self._env_file = env_file
        self._model = None
        self._model2 = None

    def configure_api(self):
        """
        Load API keys and configure generative AI and Vision API clients.
        """
        load_dotenv(self._env_file)
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("API key is not set in .env file")
        genai.configure(api_key=gemini_api_key)
        self._model = genai.GenerativeModel("gemini-1.5-flash")
        self._model2 = genai.GenerativeModel("gemini-1.5-flash-8b")
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
        if not file_path:
            return ValueError("The file_path parameter cannot be empty.")

        print(file_path)
        print(theme)
        uploaded_file = self.upload_file(file_path)
        try:
            if not theme:
                print("Generating critique...")
                response = self._model.generate_content(
                    [
                        uploaded_file,
                        "\n\n",
                        "Can you critique the composition of this photo? Lighting, story, etc?"
                        "Provide the response in JSON format with keys 'positive', 'negative', and 'overview'.",
                    ]
                )
            else:
                print("Generating critique...")
                response = self._model.generate_content(
                    [
                        uploaded_file,
                        "\n\n",
                        f"The theme that the image is based off of is: \n{theme}: {theme_description}\n",
                        "Can you critique the composition of this photo (Lighting, story, etc?), and how accurate is the photo from the theme?"
                        "Provide the response in JSON format with keys 'positive', 'negative', and 'overview'.",
                    ]
                )
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


def main():
    gemini = Gemini()

    # Configure the API
    try:
        gemini.configure_api()
    except ValueError as e:
        print(f"Error: {e}")
        return

    while True:
        print("\n=== Gemini Test Menu ===")
        print("1. Generate Photography themes: ")
        print("2. Upload and Critique Photo")
        print("3. Gemini Files")
        print("4. Delete File")
        print("x. Exit")
        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            # Test generate_theme
            try:
                theme = gemini.generate_theme()
                print(f"Generated Photography Theme: {theme}")
            except Exception as e:
                print(f"Error generating theme: {e}")

        elif choice == "2":
            # Test critique_photo
            file_path = input("Enter the path to the photo file: ").strip()
            if not os.path.exists(file_path):
                print("Error: File does not exist. Please try again.")
                continue

            try:
                critique = gemini.critique_photo(file_path)
                print(f"Photo Critique: {critique}")
            except Exception as e:
                print(f"Error critiquing photo: {e}")

        elif choice == "3":
            geminiFiles = gemini.list_uploaded_files()
            print(geminiFiles)

        elif choice == "4":
            filename = input("Enter filename you wanted to delete")
            print(gemini.delete_file(filename))

        elif choice == "x":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter a valid option.")


if __name__ == "__main__":
    main()
