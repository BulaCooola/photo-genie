import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os


class ImageBrowser(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Browser")
        self.geometry("800x600")

        # List to hold images and index for current image
        self.image_list = []
        self.current_index = 0

        # Load images from a folder
        self.load_images()

        # Create label to display images
        self.image_label = tk.Label(self)
        self.image_label.pack(expand=True)

        # Create navigation buttons
        self.prev_button = tk.Button(
            self, text="Previous", command=self.show_prev_image
        )
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = tk.Button(self, text="Next", command=self.show_next_image)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Show the first image if available
        if self.image_list:
            self.show_image(0)

    def load_images(self):
        """Load images from a folder chosen by the user."""
        folder_path = filedialog.askdirectory(title="Select a folder with images")
        if not folder_path:
            return  # Exit if no folder was selected

        # Load all images in the folder
        for filename in os.listdir(folder_path):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                image_path = os.path.join(folder_path, filename)
                self.image_list.append(image_path)

    def show_image(self, index):
        """Display the image at the given index."""
        image_path = self.image_list[index]
        image = Image.open(image_path)
        image = image.resize((900, 600), Image.LANCZOS)  # Resize to fit the window
        photo = ImageTk.PhotoImage(image)

        # Update the label with the new image
        self.image_label.config(image=photo)
        self.image_label.image = photo

    def show_next_image(self):
        """Display the next image."""
        if self.image_list:
            self.current_index = (self.current_index + 1) % len(self.image_list)
            self.show_image(self.current_index)

    def show_prev_image(self):
        """Display the previous image."""
        if self.image_list:
            self.current_index = (self.current_index - 1) % len(self.image_list)
            self.show_image(self.current_index)


if __name__ == "__main__":
    app = ImageBrowser()
    app.mainloop()
