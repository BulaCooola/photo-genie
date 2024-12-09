import tkinter as tk


class HomeTab:
    def __init__(self, notebook):
        """
        Creates a home tab with instructions
        """
        # Create frame with parent notebook
        self.frame = tk.Frame(notebook)

        # Welcome title
        welcome_label = tk.Label(
            self.frame, text="Welcome to Photo Genie!", font=("Helvetica", 18, "bold")
        )
        welcome_label.pack(pady=20)

        # Instructions
        instructions = (
            "This application is a photographer toolkit "
            "to help get feedback on their photos, generate themes to expand their creativity, and sort through images. \n \n"
            "To use the 'Upload and Critique' tab, click the 'Upload File' button and select an image file. "
            "If you want to critique the image with a theme, select the drop down 'Select Theme' which are themes you can save in the 'Generate Theme' Tab. "
            "Once you upload the image file, the critiquing process powered by Gemini AI starts. After a few seconds, a critique should appear in the box. "
            "Any displayed errors on the box is a parse error from Gemini which we cannot control. \n \n"
            "Viewing saved images and critiques is easy. In the 'View Image and Critique' Tab, there will be a list of files that you have saved which are stored in a database."
            "You can select and view any image along with its critique. \n \n"
            "The app offers two ways to sort: Manual and Blur Sort. These sorting tabs aim to help photographers quickly cull through photos they want to keep or delete. \n \n"
            "To manual sort, click on the 'Manual Sort' tab and click on 'Select Folder'. The folder must have images in it (.jpg, .png). "
            "You can tag each photo by tags 'Keep', 'Maybe', and 'Discard'. After you are done tagging, you can click 'Finish Sorting' which will copy all images and put them in folders respective to their tag."
            "\n \n"
            "To blur sort, simply select a folder with images. When a folder is selected, it will compute a blur value for each image which will be used to filter out blurry images. "
            "This will also sort into folders 'Keep' and 'Delete'."
        )
        instructions_label = tk.Label(
            self.frame,
            text=instructions,
            wraplength=500,
            justify="left",
            font=("Helvetica", 12),
        )
        instructions_label.pack(pady=10)

        # Footer
        footer_label = tk.Label(
            self.frame,
            text="Powered by OpenCV, GeminiAI, and Python",
            font=("Helvetica", 10, "italic"),
        )
        footer_label.pack(side="bottom", pady=10)
