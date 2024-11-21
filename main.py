import tkinter as tk
import datetime
import threading
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk


# Custom Modules
from dbfuncs import MongoDBHandler
from gemini import Gemini


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
        self.upload_tab = tk.Frame(self.notebook)
        self.view_tab = tk.Frame(self.notebook)

        self.notebook.add(self.upload_tab, text="Upload and Critique")
        self.notebook.add(self.view_tab, text="View Image and Critique")

        # Initialize tabs
        self.init_critique_tab()
        self.init_view_tab()

        # Log and detect tab changes
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    # TABS
    def init_critique_tab(self):
        # Label for instructions
        self.label = tk.Label(
            self.upload_tab,
            text="Upload an image to receive a critique",
            font=("Helvetica", 14),
        )
        self.label.pack(pady=10)

        # Upload Button
        self.upload_button = tk.Button(
            self.upload_tab,
            text="Upload File",
            command=self.upload_file,
            font=("Helvetica", 12),
        )
        self.upload_button.pack(pady=10)

        # Save Button
        self.save_button = tk.Button(
            self.upload_tab,
            text="Save Image and Critique",
            command=self.save_image_and_critique,
            font=("Helvetica", 12),
            state=tk.DISABLED,  # Initially Disabled (until critique generated)
        )
        self.save_button.pack(pady=10)

        # Display Area for the Image
        self.image_label = tk.Label(self.upload_tab)
        self.image_label.pack(pady=10)

        # Display Area for the Critique
        self.critique_text = tk.Text(self.upload_tab, wrap=tk.WORD, height=10, width=60)
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

        # # Entry field for file ID
        # self.file_id_entry = tk.Entry(self.view_tab, font=("Helvetica", 12), width=30)
        # self.file_id_entry.pack(pady=10)

        # # View Button
        # self.view_button = tk.Button(
        #     self.view_tab, text="View", command=self.view_file, font=("Helvetica", 12)
        # )
        # self.view_button.pack(pady=10)

        # Listbox (for all images)
        self.image_listbox = tk.Listbox(
            self.view_tab, font=("Helvetica", 12), height=10, width=50
        )
        self.image_listbox.pack(pady=10)

        # Button to load the selected image and critique
        self.load_button = tk.Button(
            self.view_tab,
            text="Load Image and Critique",
            command=self.load_selected_image,
            font=("Helvetica", 12),
        )
        self.load_button.pack(pady=10)

        # Display Area for the selected image
        self.view_image_label = tk.Label(self.view_tab)
        self.view_image_label.pack(pady=10)

        # Display Area for the selected image's critique
        self.view_critique_text = tk.Text(
            self.view_tab, wrap=tk.WORD, height=10, width=60
        )
        self.view_critique_text.pack(pady=20)
        self.view_critique_text.insert(tk.END, "Critique will appear here...")
        self.view_critique_text.config(state=tk.DISABLED)

        self.load_images_into_listbox()

    def on_tab_change(self, event):
        # Get the currently selected tab
        selected_tab = self.notebook.index(self.notebook.select())

        # Debugging: Print the selected tab
        print(f"Selected tab index: {selected_tab}")

        # Perform actions based on the selected tab
        if selected_tab == 0:  # Upload & Critique Tab
            print("Upload & Critique Tab Active")
        elif selected_tab == 1:  # View Critique Tab
            print("View Critique Tab Active")
        elif selected_tab == 2:  # Settings Tab
            print("Settings Tab Active")

    def upload_file(self):
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

            # Get critique for the image in a different thread running concurrently (to prevent non-responsiveness)
            threading.Thread(target=self.process_image, args=(file_path,)).start()

    def process_image(self, file_path):
        try:
            # Get critique for image
            critique = self.gemini.critique_photo(
                file_path=file_path, theme="Wrestling"
            )
            # update critique in text box (call display_critique)
            self.root.after(0, lambda: self.display_critique(critique))

            # Save filepath and critique
            self.current_image_path = file_path
            self.current_critique = critique
        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error", f"Error generating critique: {e}"
                ),
            )
        finally:
            # Re-enable upload button
            self.root.after(0, lambda: self.upload_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.save_button.config(state=tk.NORMAL))

    def display_image(self, file_path):
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
        if not self.current_image_path or not self.current_critique:
            messagebox.showerror(
                "Error",
                "No image or critique loaded/saved. Please upload an image to save.",
            )
            return

        try:
            image_id = self.dbfuncs.add_image(self.current_image_path)
            print(self.current_critique)
            inserted_data = self.dbfuncs.add_critique(image_id, self.current_critique)
            print(inserted_data)
            messagebox.showinfo(
                "Success",
                f"Critique and Image saved to database",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image or critique: {e}")

    def display_critique(self, critique):
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

    def view_tab(self):
        pass

    def load_images_into_listbox(self):
        try:
            # Fetch images from db
            images = self.dbfuncs.getAllImages()

            # Clear listbox
            self.image_listbox.delete(0, tk.END)

            # Populate Listbox
            for image in images:
                imageid = image["filename"]
                uploadDate = image["uploadDate"]

                if isinstance(uploadDate, str):
                    uploadDate = datetime.fromisoformat(uploadDate)

                # Format the timestamp as a string (e.g., "2024-11-21 10:30:00")
                uploadDate = uploadDate.strftime("%Y-%m-%d %H:%M:%S")

                list_item = f"{imageid} - Uploaded: {uploadDate}"
                self.image_listbox.insert(tk.END, list_item)

            self.all_images = {image["_id"]: image for image in images}

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load images: {e}")

    def load_selected_image(self):
        # ! TODO
        try:
            selection = self.image_listbox.curselection()
            if not selection:
                messagebox.showerror("Error", "No image selected.")
                return

            file_id = self.image_listbox.get(selection[0])

            # Retrieve image data

            # Display image

            # Display Critique

        except Exception as e:
            messagebox.showerror("Error", f"Failed to laod image and critique: {e}")


def configure_Gemini():
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
    root.mainloop()
    dbfuncs.close_connection()  # Close db connection when program ends
