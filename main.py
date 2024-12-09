# Authors: Branden Bulatao, Matthew Kribs
# Date: 12/2024
# Description: The main program that runs Photo Genie. This program initializes a tkinter application and configures necessary backend modules.


import tkinter as tk
from tkinter import ttk

# Custom Modules
from modules.dbfuncs import MongoDBHandler
from modules.gemini import Gemini
from modules.GenerateCritiqueTab import GenerateCritiqueTab
from modules.ViewCritiquesTab import ViewCritiquesTab
from modules.ThemesTab import ThemesTab
from modules.ManualSortTab import ManualSortTab
from modules.BlurSortTab import BlurSortApp
from modules.HomeTab import HomeTab


class ImageCritiqueApp:
    def __init__(self, root, gemini, dbfuncs):
        self.root = root
        self.root.title("Photo Genie")
        self.root.geometry("600x400")

        # Get instances of our modules
        self.gemini = gemini
        self.dbfuncs = dbfuncs

        # Variables for storing currnent images and critiques
        self.current_image_path = None
        self.current_critique = None

        # Create Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Get Tab Modules
        self.home_tab = HomeTab(self.notebook)
        self.generate_critique_tab = GenerateCritiqueTab(
            self.notebook, self.gemini, self.dbfuncs
        )
        self.view_tab = ViewCritiquesTab(self.notebook, self.dbfuncs)
        self.theme_tab = ThemesTab(self.notebook, self.gemini, self.dbfuncs)
        self.sort_tab = ManualSortTab(self.notebook)
        self.blur_tab = BlurSortApp(self.notebook)

        # Adding our tabs to the notebook
        self.notebook.add(self.home_tab.frame, text="Home")
        self.notebook.add(self.generate_critique_tab.frame, text="Upload and Critique")
        self.notebook.add(self.view_tab.frame, text="View Image and Critique")
        self.notebook.add(self.theme_tab.frame, text="Generate Theme")
        self.notebook.add(self.sort_tab.frame, text="Manual Sort and Cull Photos")
        self.notebook.add(self.blur_tab.root, text="Blur Sort and Cull Photos")

        # Log and detect tab changes
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    # TABS changes
    def on_tab_change(self, event):
        """
        Logs tab changes on the terminal
        """
        # Get the currently selected tab
        selected_tab = self.notebook.index(self.notebook.select())

        # Perform actions based on the selected tab
        if selected_tab == 0:  # Home Tab
            print("Home Tab Active")
        elif selected_tab == 1:  # Upload & Critique Tab
            print("Upload & Critique Tab Active")
        elif selected_tab == 2:  # View Critique Tab
            self.view_tab.load_images_into_listbox()  # Reload images to listbox
            print("View Critique Tab Active")
        elif selected_tab == 3:  # Theme Tab
            print("Generate Theme Tab Active")
        elif selected_tab == 4:  # Manual Sort Tab
            print("Manual Sort Tab Active")
        elif selected_tab == 5:  # Blur Sort Tab
            print("Blur Sort Tab Active")


def configure_Gemini():
    """
    Initializes and configures Gemini before launching app
    """
    gemini = Gemini()

    # Configure API
    try:
        gemini.configure_api()
        return gemini
    except ValueError as e:
        print(f"Error: {e}")
        return


if __name__ == "__main__":
    root = tk.Tk()
    gemini = configure_Gemini()
    dbfuncs = MongoDBHandler()
    app = ImageCritiqueApp(root, gemini, dbfuncs)
    style = ttk.Style()
    print(style.theme_names())  # View available themes
    style.theme_use("clam")  # Use a specific theme
    root.state("zoomed")
    root.mainloop()
    dbfuncs.close_connection()  # Close db connection when program ends
