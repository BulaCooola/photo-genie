import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, ttk

# Custom Modules
from modules.dbfuncs import MongoDBHandler
from modules.gemini import Gemini
from modules.GenerateCritiqueTab import GenerateCritiqueTab
from modules.ViewCritiquesTab import ViewCritiquesTab
from modules.ThemesTab import ThemesTab
from ManualSort import ManualSortApp


class ImageCritiqueApp:
    def __init__(self, root, gemini, dbfuncs):
        self.root = root
        self.root.title("Image Critique App")
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
        self.generate_critique_tab = GenerateCritiqueTab(
            self.notebook, self.gemini, self.dbfuncs
        )
        self.view_tab = ViewCritiquesTab(self.notebook, self.dbfuncs)
        self.theme_tab = ThemesTab(self.notebook, self.gemini, self.dbfuncs)
        self.sort_tab = ManualSortApp(self.notebook)

        # Adding our tabs to the notebook
        self.notebook.add(self.generate_critique_tab.frame, text="Upload and Critique")
        self.notebook.add(self.view_tab.frame, text="View Image and Critique")
        self.notebook.add(self.theme_tab.frame, text="Generate Theme")
        self.notebook.add(self.sort_tab.frame, text="Sort and Cull Photos")

        # Log and detect tab changes
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    # TABS

    def on_tab_change(self, event):
        """
        Logs tab changes on the terminal
        """
        # Get the currently selected tab
        selected_tab = self.notebook.index(self.notebook.select())

        # Debugging: Print the selected tab
        print(f"Selected tab index: {selected_tab}")

        # Perform actions based on the selected tab
        if selected_tab == 0:  # Upload & Critique Tab
            print("Upload & Critique Tab Active")
        elif selected_tab == 1:  # View Critique Tab
            self.view_tab.load_images_into_listbox()  # Reload images to listbox
            print("View Critique Tab Active")
        elif selected_tab == 2:  # Settings Tab
            print("Generate Theme Tab Active")


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
