import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from PIL import Image, ImageTk


class GenerateCritiqueTab:
    def __init__(self, notebook, gemini, dbfuncs):
        self.gemini = gemini
        self.dbfuncs = dbfuncs

        self.frame = tk.Frame(notebook)

        # Variables for storing currnent images and critiques
        self.current_image_path = None
        self.current_critique = None

        # Label for instructions
        self.critique_label = tk.Label(
            self.frame,
            text="Upload an image to receive a critique",
            font=("Helvetica", 14),
        )
        self.critique_label.pack(pady=10)

        # Upload Button
        self.upload_button = tk.Button(
            self.frame,
            text="Upload File",
            command=self.upload_file,
            font=("Helvetica", 12),
        )
        self.upload_button.pack(pady=10)

        # Save Button
        self.save_button = tk.Button(
            self.frame,
            text="Save Image and Critique",
            command=self.save_image_and_critique,
            font=("Helvetica", 12),
            state=tk.DISABLED,
        )
        self.save_button.pack(pady=10)

        # Label for selecting a theme
        self.theme_select_label = tk.Label(self.frame, text="Select a saved theme: ")
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
            self.frame,
            textvariable=self.theme_var,
            values=saved_theme_names,
            state="readonly",
        )
        self.theme_dropdown.pack(fill="x", padx=10, pady=5)

        # Display Area for the Image
        self.image_label = tk.Label(self.frame)
        self.image_label.pack(pady=10)

        # Display Area for the Critique
        self.critique_text = tk.Text(self.frame, wrap=tk.WORD, height=10, width=60)
        self.critique_text.pack(pady=20)
        self.critique_text.insert(tk.END, "Critique will appear here...")
        self.critique_text.config(state=tk.DISABLED)

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
            self.frame.after(0, lambda: self.display_critique(critique))

            # Save filepath and critique
            self.current_image_path = file_path
            self.current_critique = critique
        except Exception as e:
            self.frame.after(
                0,
                lambda error=e: messagebox.showerror(
                    "Error", f"Error generating critique: {error}"
                ),
            )
        finally:
            # Re-enable upload button
            self.frame.after(0, lambda: self.upload_button.config(state=tk.NORMAL))
            self.frame.after(0, lambda: self.save_button.config(state=tk.NORMAL))

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
