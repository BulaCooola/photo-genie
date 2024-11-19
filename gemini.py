# Authors: Branden Bulatao, Matthew Kribs, Hashil Patel
# Description: Test for Gemini file

import google.generativeai as genai
from google.cloud import vision
import os
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
        print("Gemini API configured successfully")

    def generate_theme(self):
        """
        Generate a photography theme using the Gemini model.

        :return: The generated theme as a Python dictionary
        :rtype: dict
        """
        response = self._model.generate_content(
            [
                {
                    "text": "Can you give me a four photography ideas? Make each idea a sentence of what I should shoot and/or how I should shoot something."
                }
            ]
        )
        print(response.text)
        response_text = response.text.strip()
        return response_text

    def upload_file(self, file_path):
        """
        Upload a file to the generative AI service.

        :param file_path: Path to the file to upload
        :type file_path: str
        :return: Uploaded file object
        :rtype: genai.File
        """
        myfile = genai.upload_file(file_path)
        print(f"Uploaded file: {myfile.name}")
        return myfile

    def critique_photo(self, file_path):
        """
        Provide critique on the composition of a photo.

        :param file_path: Path to the photo to critique
        :type file_path: str
        :return: Critique as a dictionary containing positive and negative feedback
        :rtype: dict
        """
        # myfile = genai.upload_file("_DSC3940.JPG")
        uploaded_file = self.upload_file(file_path)
        try:
            result = self._model.generate_content(
                [
                    uploaded_file,
                    "\n\n",
                    "Can you critique the composition of this photo? Lighting, story, etc? Give me a positive and a negative.",
                ]
            )
            return result.text.strip()
        finally:
            # Delete file to save space after critique
            # uploaded_file.delete()
            print(f"Deleted file: {uploaded_file.name}")

    def list_uploaded_files(self):
        pass


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
        print("1. Generate Photography Theme")
        print("2. Upload and Critique Photo")
        print("3. Exit")
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
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter a valid option.")


if __name__ == "__main__":
    main()

# def critique_image(image_path):
#     with open(image_path, "rb") as image_file:
#         content = image_file.read()
#     image = vision.Image(content=content)

#     # Perform label detection to get image composition features
#     response = vision_client.label_detection(image=image)
#     labels = [label.description for label in response.label_annotations]
#     print("Image Composition Features:", labels)

#     # Step 2: Formulate a prompt for Gemini using these labels
#     prompt_text = (
#         f"I have an image with the following elements: {', '.join(labels)}. "
#         "Can you critique its composition and suggest any improvements?"
#     )

#     # Step 3: Send the prompt to Gemini for critique
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content([{"text": prompt_text}])

#     # Display the critique
#     print("Gemini Critique:", response.text)
