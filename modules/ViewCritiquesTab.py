import tkinter as tk
from tkinter import Scrollbar, messagebox, ttk
from PIL import Image, ImageTk
from io import BytesIO
import datetime


class ViewCritiquesTab:
    def __init__(self, notebook, dbfuncs):
        self.dbfuncs = dbfuncs

        self.frame = tk.Frame(notebook)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # self.window = tk.Toplevel(notebook)
        # self.window.title("View Image")

        # Label for file ID entry
        self.id_label = tk.Label(
            self.frame,
            text="Click to view Image and Critique",
            font=("Helvetica", 14),
        )
        self.id_label.pack(pady=10)

        # Listbox (for all images)
        self.image_listbox = tk.Listbox(
            self.frame, font=("Helvetica", 12), height=10, width=50
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
        scrollbar = Scrollbar(self.frame)
        # scrollbar.pack(side="right", fill="both")
        # self.frame.config(yscrollcommand=scrollbar.set)

        # Button to load the selected image and critique
        self.load_button = tk.Button(
            self.frame,
            text="Load Image and Critique",
            command=self.load_selected_image,
            font=("Helvetica", 12),
        )
        self.load_button.pack(pady=10)

        # Fullscreen Button
        self.fullscreen_button = tk.Button(
            self.frame,
            text="View Fullscreen",
            command=self.view_image_fullscreen,
            font=("Helvetica", 12),
        )
        self.fullscreen_button.pack(pady=10)

        # Display Area for the selected image
        self.view_image_label = tk.Label(self.frame)
        self.view_image_label.pack(pady=10)

        # Display Area for the selected image's critique
        self.view_critique_text = tk.Text(self.frame, wrap=tk.WORD, height=20, width=60)
        self.view_critique_text.pack(pady=20)
        self.view_critique_text.insert(tk.END, "Critique will appear here...")
        self.view_critique_text.config(state=tk.DISABLED)

        self.load_images_into_listbox()

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

                # Date formatting
                if isinstance(uploadDate, str):
                    uploadDate = datetime.fromisoformat(uploadDate)
                # Format the timestamp as a string (e.g., "2024-11-21 10:30:00")
                uploadDate = uploadDate.strftime("%Y-%m-%d %H:%M:%S")

                list_item = f"{filename} - \t \t \t \t \t \t Uploaded: {uploadDate}"
                self.image_listbox.insert(tk.END, list_item)

            self.all_images = {image["filename"]: image for image in images}

            print("Successfully loaded images into box")

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

            # Get the selected image
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

            print("Successfully Loaded Image and Critique")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image and critique: {e}")

    def display_image_view_tab(self, file_id):
        """
        Helper function for load_selected_image(). Used to load actual image
        """
        try:
            # Retrieve the image binary data from the database
            stored_file = self.dbfuncs.getImageByFileID(file_id)
            # Convert binary data to BytesIO object
            image_data = BytesIO(stored_file.read())

            # https://www.w3resource.com/python-exercises/tkinter/python-tkinter-basic-exercise-12.php#google_vignette
            image = Image.open(image_data)
            image.thumbnail((400, 300))  # Resize to fit the label
            photo = ImageTk.PhotoImage(image)

            self.view_image_label.config(image=photo)
            self.view_image_label.image = photo

            image_data.seek(0)
            self.view_image_label.fullImage = Image.open(image_data)

            print("Successfully displayed image")

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
                raise ValueError("No image is loaded for fullscreen view.")

            # Create a new Toplevel window for fullscreen
            fullscreen_window = tk.Toplevel(self.frame)
            fullscreen_window.attributes("-alpha", True)  # Enable fullscreen

            # Get the screen dimensions
            screen_width = fullscreen_window.winfo_screenwidth()
            screen_height = fullscreen_window.winfo_screenheight()

            # Get stored image dimensions
            image = self.view_image_label.fullImage
            image_width, image_height = image.size

            # Adjust image dimensions to fit the screen size
            if (image_width / image_height) > (screen_width / screen_height):
                new_width = screen_width
                new_height = int(screen_width / (image_width / image_height))
            else:
                new_height = screen_height
                new_width = int(screen_height * (image_width / image_height))

            # Resize the image
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
