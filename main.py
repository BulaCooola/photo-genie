import tkinter as tk
import datetime
import threading
from io import BytesIO
from tkinter import filedialog, messagebox, Scrollbar, ttk
from PIL import Image, ImageTk

# Custom Modules
from modules.dbfuncs import MongoDBHandler
from modules.gemini import Gemini


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

        # Tabs
        self.generate_critique_tab = tk.Frame(self.notebook)
        self.view_tab = tk.Frame(self.notebook)
        self.theme_tab = tk.Frame(self.notebook)

        self.notebook.add(self.generate_critique_tab, text="Upload and Critique")
        self.notebook.add(self.view_tab, text="View Image and Critique")
        self.notebook.add(self.theme_tab, text="Generate Theme")

        # Initialize tabs
        self.init_critique_tab()
        self.init_view_tab()
        self.init_theme_tab()

        # Log and detect tab changes
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    # TABS
    def init_critique_tab(self):
        # Label for instructions
        self.critique_label = tk.Label(
            self.generate_critique_tab,
            text="Upload an image to receive a critique",
            font=("Helvetica", 14),
        )
        self.critique_label.pack(pady=10)

        # Upload Button
        self.upload_button = tk.Button(
            self.generate_critique_tab,
            text="Upload File",
            command=self.upload_file,
            font=("Helvetica", 12),
        )
        self.upload_button.pack(pady=10)

        # Save Button
        self.save_button = tk.Button(
            self.generate_critique_tab,
            text="Save Image and Critique",
            command=self.save_image_and_critique,
            font=("Helvetica", 12),
            state=tk.DISABLED,  # Initially Disabled (until critique generated)
        )
        self.save_button.pack(pady=10)

        # Label for selecting a theme
        self.theme_select_label = tk.Label(
            self.generate_critique_tab, text="Select a saved theme: "
        )
        self.theme_select_label.pack(anchor="w", padx=10, pady=5)

        # Load saved themes for dropdown (with a "Custom Theme" option)
        saved_themes = self.dbfuncs.getAllThemes()
        self.themes_objs = {
            theme["theme_name"]: [theme["_id"], theme["description"]]
            for theme in saved_themes
        }
        saved_theme_names = (
            ["Select Theme"] + list(self.themes_objs.keys()) + ["Custom Theme"]
        )

        # String var for dropdown selection
        self.theme_var = tk.StringVar(value=saved_theme_names[0])

        # Dropdown menu of themes
        self.theme_dropdown = ttk.Combobox(
            self.generate_critique_tab,
            textvariable=self.theme_var,
            values=saved_theme_names,
            state="readonly",
        )
        self.theme_dropdown.pack(fill="x", padx=10, pady=5)

        # Display Area for the Image
        self.image_label = tk.Label(self.generate_critique_tab)
        self.image_label.pack(pady=10)

        # Display Area for the Critique
        self.critique_text = tk.Text(
            self.generate_critique_tab, wrap=tk.WORD, height=10, width=60
        )
        self.critique_text.pack(pady=20)
        self.critique_text.insert(tk.END, "Critique will appear here...")
        self.critique_text.config(state=tk.DISABLED)

    def init_view_tab(self):
        # Label for file ID entry
        self.id_label = tk.Label(
            self.view_tab,
            text="Click to view Image and Critique",
            font=("Helvetica", 14),
        )
        self.id_label.pack(pady=10)

        # Listbox (for all images)
        self.image_listbox = tk.Listbox(
            self.view_tab, font=("Helvetica", 12), height=10, width=50
        )
        # self.image_listbox.pack(pady=10)
        self.image_listbox.pack(
            pady=10, padx=10, side=tk.LEFT, fill=tk.BOTH, expand=True
        )

        # Scrollbar for the Listbox
        scrollbarLB = Scrollbar(self.image_listbox)
        scrollbarLB.pack(side="right", fill="both")
        self.image_listbox.config(yscrollcommand=scrollbarLB.set)
        scrollbarLB.config(command=self.image_listbox.yview)

        # ? Scrollbar for tab
        scrollbar = Scrollbar(self.view_tab)
        # scrollbar.pack(side="right", fill="both")
        # self.view_tab.config(yscrollcommand=scrollbar.set)

        # Button to load the selected image and critique
        self.load_button = tk.Button(
            self.view_tab,
            text="Load Image and Critique",
            command=self.load_selected_image,
            font=("Helvetica", 12),
        )
        self.load_button.pack(pady=10)

        # Fullscreen Button
        self.fullscreen_button = tk.Button(
            self.view_tab,
            text="View Fullscreen",
            command=self.view_image_fullscreen,
            font=("Helvetica", 12),
        )
        self.fullscreen_button.pack(pady=10)

        # Display Area for the selected image
        self.view_image_label = tk.Label(self.view_tab)
        self.view_image_label.pack(pady=10)

        # Display Area for the selected image's critique
        self.view_critique_text = tk.Text(
            self.view_tab, wrap=tk.WORD, height=20, width=60
        )
        self.view_critique_text.pack(pady=20)
        self.view_critique_text.insert(tk.END, "Critique will appear here...")
        self.view_critique_text.config(state=tk.DISABLED)

        self.load_images_into_listbox()

    def init_theme_tab(self):
        # Label for Title
        label = ttk.Label(
            self.theme_tab,
            text="Generate Photography Theme",
            font=("Helvetica", 14),
        )
        label.pack(pady=10)

        # Canvas setup
        self.theme_canvas = tk.Canvas(self.theme_tab)
        self.theme_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.theme_inner_frame = tk.Frame(self.theme_canvas)

        # Add a vertical scrollbar
        theme_scrollbar = Scrollbar(self.theme_inner_frame, orient="vertical")
        self.theme_canvas.config(yscrollcommand=theme_scrollbar.set)
        theme_scrollbar.config(command=self.theme_canvas.yview)
        theme_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.theme_canvas.pack(side=tk.LEFT)
        self.theme_canvas.create_window(
            0, 0, window=self.theme_inner_frame, anchor="nw"
        )
        self.theme_inner_frame.bind(
            "<Configure>",
            lambda e: self.theme_canvas.configure(
                scrollregion=self.theme_canvas.bbox("all")
            ),
        )

        # Button to generate theme
        self.theme_button = ttk.Button(
            self.theme_canvas,
            text="Generate Theme",
            command=self.process_generate_theme,
        )
        self.theme_button.pack(pady=5)

        # Frame where generated themes will go
        self.theme_container = tk.Frame(self.theme_inner_frame)
        self.theme_container.pack(fill=tk.BOTH, expand=True)

        # Add a button to load saved themes
        self.load_button = tk.Button(
            self.theme_canvas,
            text="Load Saved Themes",
            command=self.load_saved_themes,
        )
        self.load_button.pack(pady=5)

        # Frame where saved themes go
        self.saved_themes_frame = tk.Frame(self.theme_inner_frame)
        self.saved_themes_frame.pack(fill=tk.BOTH, expand=True, pady=60)

    def process_generate_theme(self):
        """
        Generate a photography theme using the provided function
        and display it in the output text widget.
        """
        # Clear the existing theme frame (if any)
        for widget in self.theme_container.winfo_children():
            widget.destroy()

        try:
            # Call gemimi function to generate themes
            themes = self.gemini.generate_theme()

            # Validate themes and type
            if themes and isinstance(themes, dict):
                # Iterate through all themes
                for key, theme in themes.items():
                    if key != "critique_date":
                        # Create frame for each theme
                        theme_frame = tk.Frame(self.theme_container)
                        theme_frame.pack(fill=tk.X, pady=5)

                        # Display theme text
                        theme_label = tk.Label(
                            theme_frame,
                            text=f"{key}: {theme}",
                            wraplength=400,
                            justify=tk.LEFT,
                        )
                        theme_label.pack(side=tk.LEFT, padx=10)

                        # Save button for theme
                        save_button = tk.Button(theme_frame, text="Save Theme")
                        save_button.config(
                            command=lambda b=save_button, k=key, t=theme: self.save_theme_to_db(
                                b, k, t
                            )
                        )
                        save_button.pack(side=tk.RIGHT)

        except Exception as e:
            print(f"Error generating themes: {e}")
            messagebox.showerror("Error", "An error occurred while generating themes.")

    def load_saved_themes(self):
        """
        Load saved themes from database and display them
        """
        # Clear frame
        for widget in self.saved_themes_frame.winfo_children():
            widget.destroy()

        try:
            saved_themes = self.dbfuncs.getAllThemes()
            if not saved_themes:
                messagebox.showinfo("Info", "No saved themes found")
                return

            # Title for saved themes section
            saved_themes_label = tk.Label(
                self.saved_themes_frame,
                text="Saved Themes",
                font=("Ariel", 14, "bold"),
                pady=5,
            )
            saved_themes_label.pack()

            # Add each theme
            for theme in saved_themes:
                print(theme)
                # Make another frame to house both theme name and description separately
                theme_row_frame = tk.Frame(self.saved_themes_frame)
                theme_row_frame.pack(fill=tk.BOTH, pady=5)

                # Theme name label
                theme_name_label = tk.Label(
                    theme_row_frame,
                    text=theme["theme_name"],
                    font=("Arial", 10, "bold"),
                    anchor="w",
                    width=20,
                )
                theme_name_label.pack(side=tk.LEFT, padx=10)

                # Description label
                description_label = tk.Label(
                    theme_row_frame,
                    text=theme["description"],
                    anchor="w",  # Align text to the left
                    wraplength=400,  # Allow text wrapping
                )
                description_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        except Exception as e:
            print(f"Error loading saved themes: {e}")
            messagebox.showerror("Error", f"Error loading saved themes: {e}")

    def save_theme_to_db(self, button, theme_name, theme_description):
        """
        Save the selected theme to the database.

        :param button: button widget for respective theme
        :type button: Button
        :param theme_name: The name of the theme
        :type theme_name: str
        :param theme_description: Description of what the theme is
        :type theme_description: str
        """
        try:
            # Call your database save function (adjust as needed)
            self.dbfuncs.add_theme(theme_name, theme_description)
            print(theme_name, theme_description)
            button.config(state=tk.DISABLED)  # Disable the button after saving
            messagebox.showinfo("Success", f"Theme saved: {theme_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save theme: {e}")

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
            self.load_images_into_listbox()  # Reload images to listbox
            print("View Critique Tab Active")
        elif selected_tab == 2:  # Settings Tab
            print("Generate Theme Tab Active")

    def upload_file(self):
        """
        Helper function for upload button for the user to upload file
        """
        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            # Display the image
            self.display_image(file_path)

            # Disable the upload button temporarily
            self.upload_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)

            # Get critique for the image in a different thread running concurrently (to prevent window non-responsiveness)
            threading.Thread(target=self.process_image, args=(file_path,)).start()

    def process_image(self, file_path):
        """
        Helper function to process the critique

        :param file_path: Filepath of the image selected by user
        :type file_path: str
        """
        try:
            # Get critique for image
            theme = self.theme_var.get()

            if theme == "Select Theme":
                critique = self.gemini.critique_photo(
                    file_path=file_path, theme=None, theme_description=None
                )
            else:
                theme_description = self.themes_objs.get(theme)[1]
                critique = self.gemini.critique_photo(
                    file_path=file_path,
                    theme=theme,
                    theme_description=theme_description,
                )
            # update critique in text box (call display_critique)
            self.root.after(0, lambda: self.display_critique(critique))

            # Save filepath and critique
            self.current_image_path = file_path
            self.current_critique = critique
        except Exception as e:
            self.root.after(
                0,
                lambda error=e: messagebox.showerror(
                    "Error", f"Error generating critique: {error}"
                ),
            )
        finally:
            # Re-enable upload button
            self.root.after(0, lambda: self.upload_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.save_button.config(state=tk.NORMAL))

    def display_image(self, file_path):
        """
        Helper function to display image to GUI

        :param file_path: Filepath of the image selected by user
        :type file_path: str
        """
        try:
            image = Image.open(file_path)
            image.thumbnail((400, 300))  # Resize to fit in the window
            photo = ImageTk.PhotoImage(image)

            self.image_label.config(image=photo)
            self.image_label.image = (
                photo  # Keep a reference to prevent garbage collection
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

    def save_image_and_critique(self):
        """
        Helper function for save image and critique button. Saves the
        image and critique to the database
        """
        if not self.current_image_path or not self.current_critique:
            messagebox.showerror(
                "Error",
                "No image or critique loaded/saved. Please upload an image to save.",
            )
            return

        # Select theme
        selected_theme = self.theme_var.get()

        # Make theme_id None if a theme is not selected
        theme_id = None
        if selected_theme != "Select Theme":
            theme_id = self.themes_objs.get(selected_theme)[0]

        try:
            # Add Image to database
            image_id = self.dbfuncs.add_image(self.current_image_path)

            # Add critique to the database
            self.dbfuncs.add_critique(image_id, self.current_critique, theme_id)

            # Update user that save is a success
            messagebox.showinfo(
                "Success",
                f"Critique and Image saved to database",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image or critique: {e}")

    def display_critique(self, critique):
        """
        Displays critique to the GUI

        :param critique: image critique info
        :type critique: dict
        """
        # Clear the text box and insert the critique
        self.critique_text.config(state=tk.NORMAL)
        self.critique_text.delete("1.0", tk.END)
        if isinstance(critique, dict):
            self.critique_text.insert(
                tk.END,
                f"Positive:\n- " + "\n- ".join(critique["positive"]) + "\n\n"
                f"Negative:\n- " + "\n- ".join(critique["negative"]) + "\n\n"
                f"Overview:\n{critique['overview']}",
            )
        else:
            self.critique_text.insert(
                tk.END, "Error generating critique. Please insert image again."
            )
        self.critique_text.config(state=tk.DISABLED)

    def load_images_into_listbox(self):
        """
        Loads image to the listbox in the GUI
        """
        try:
            # Fetch images from db
            images = self.dbfuncs.getAllImages()

            # Clear listbox
            self.image_listbox.delete(0, tk.END)

            # Populate Listbox
            for image in images:
                filename = image["filename"]
                uploadDate = image["uploadDate"]

                if isinstance(uploadDate, str):
                    uploadDate = datetime.fromisoformat(uploadDate)

                # Format the timestamp as a string (e.g., "2024-11-21 10:30:00")
                uploadDate = uploadDate.strftime("%Y-%m-%d %H:%M:%S")

                list_item = f"{filename} - Uploaded: {uploadDate}"
                self.image_listbox.insert(tk.END, list_item)

            self.all_images = {image["filename"]: image for image in images}

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load images: {e}")

    def load_selected_image(self):
        """
        Loads selected image from the database. Includes the critiue data
        """
        try:
            selection = self.image_listbox.curselection()
            if not selection:
                messagebox.showerror("Error", "No image selected.")
                return

            selection_title = self.image_listbox.get(selection[0])
            filename = selection_title.split("-")[0].strip()

            # Retrieve image data
            image_data = self.dbfuncs.getImageByFilename(filename)
            critique = image_data["metadata"]["critique"]

            # Display image
            self.display_image_view_tab(image_data["_id"])

            # Display Critique
            self.view_critique_text.config(state=tk.NORMAL)
            self.view_critique_text.delete("1.0", tk.END)
            formatted_critique = (
                f"Positive:\n- " + "\n- ".join(critique["positive"]) + "\n\n"
                f"Areas of Improvement:\n- "
                + "\n- ".join(critique["improvement"])
                + "\n\n"
                f"Overview:\n{critique['overview']}"
            )
            self.view_critique_text.insert(tk.END, formatted_critique)
            self.view_critique_text.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image and critique: {e}")

    def display_image_view_tab(self, file_id):
        """
        Helper function for load_selected_image(). Used to load actual image
        """
        try:
            # Retrieve the image binary data from the database
            stored_file = self.dbfuncs.getImageByFileID(file_id)
            image_data = BytesIO(
                stored_file.read()
            )  # Convert binary data to BytesIO object

            image = Image.open(image_data)
            image.thumbnail((400, 300))  # Resize to fit the label
            photo = ImageTk.PhotoImage(image)

            self.view_image_label.config(image=photo)
            self.view_image_label.image = photo

            image = Image.open(image_data)
            self.view_image_label.fullImage = image
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image {e}")

    def view_image_fullscreen(self):
        """
        Open the selected image in fullscreen mode.
        """
        try:
            # Check if an image is loaded in the view tab
            if (
                not hasattr(self.view_image_label, "image")
                or self.view_image_label.fullImage is None
            ):
                raise ValueError("No image is currently loaded for fullscreen view.")

            # Create a new Toplevel window for fullscreen
            fullscreen_window = tk.Toplevel(self.view_tab)
            fullscreen_window.attributes("-fullscreen", True)  # Enable fullscreen

            # Get the screen dimensions
            screen_width = fullscreen_window.winfo_screenwidth()
            screen_height = fullscreen_window.winfo_screenheight()

            # Get stored image dimensions
            print(self.view_image_label.fullImage)
            image = self.view_image_label.fullImage
            image_width, image_height = image.size

            if (image_width / image_height) > (screen_width / screen_height):
                new_width = screen_width
                new_height = int(screen_width / (image_width / image_height))
            else:
                new_height = screen_height
                new_width = int(screen_height * (image_width / image_height))

            resized_image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )

            # Convert photo to tkinter PhotoImage
            photo = ImageTk.PhotoImage(resized_image)

            # Display the image in fullscreen
            fullscreen_label = tk.Label(fullscreen_window)
            fullscreen_label.config(image=photo)
            fullscreen_label.image = photo
            fullscreen_label.pack(expand=True, fill=tk.BOTH)

            # Exit fullscreen with 'Escape' key or close button
            def exit_fullscreen(event=None):
                fullscreen_window.destroy()

            # Add an "Exit Fullscreen" button to the fullscreen window
            exit_button = tk.Button(
                fullscreen_window, text="Exit Fullscreen", command=exit_fullscreen
            )
            exit_button.pack(side=tk.RIGHT, padx=10, pady=10)

            fullscreen_window.bind("<Escape>", exit_fullscreen)

        except Exception as e:
            print(e)
            messagebox.showerror("Error", f"Could not open fullscreen view: {e}")


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
    root.state("zoomed")
    root.mainloop()
    dbfuncs.close_connection()  # Close db connection when program ends
