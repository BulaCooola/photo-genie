# Blurriness metric = variance of Laplacian of grayscale image.
# Slider sets threshold below which pictures are considered too blurry.
# Blurry pictures are copied to Discard folder, the rest are copied to Keep folder.
# The Discard and Keep folders are created inside the folder being sorted.

import tkinter as tk
from tkinter import filedialog, ttk
import cv2
import os
import threading
from shutil import copy2  # copy2 preserves more metadata


class BlurSortApp:
    def __init__(self, notebook):
        self.root = tk.Frame(notebook)

        # Initialize Variables
        self.folder_path = None
        self.sort_progress_bar = None
        self.picturesList = []
        self.blurValues = []  # blur vals
        self.num_blurry = 0

        # select folder
        self.select_button = tk.Button(
            self.root,
            text="Select Folder",
            command=self.select_folder,
            font=("Helvetica", 12),
        )
        self.select_button.pack()

        # Threshold Options
        self.init_threshold_options()

        # maybe just a label that says "Done!" would be better
        # self.blurry_label = tk.Label(self.root, font=('Helvetica',10))
        # will only display this once the sort button has been pressed

    def init_threshold_options(self):
        self.threshold_frame1 = tk.Frame(self.root)

        self.threshold_label = tk.Label(
            self.threshold_frame1, text="Set Threshold:", font=("Helvetica", 12)
        )
        self.threshold_label.pack(side="left")  # grid(row=0,column=0)

        # current_value = tk.DoubleVar()
        self.slider = tk.Scale(
            self.threshold_frame1,
            from_=0,
            to=100,
            orient="horizontal",
            # variable=current_value
        )
        self.slider.set(100)
        self.slider.pack(side="right")  # .grid(row=0,column=1)

        self.threshold_frame1.pack()
        self.threshold_frame2 = tk.Frame(self.root)

        self.default_label = tk.Label(
            self.threshold_frame2, text="Set Default Threshold:", font=("Helvetica", 12)
        )
        self.default_label.pack(side="left")

        self.checkbox_value = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(
            self.threshold_frame2,
            variable=self.checkbox_value,
            command=self.set_default_threshold,
        )
        self.checkbox.pack(side="right")

        self.threshold_frame2.pack()

        # Sort Button
        self.sort_button = tk.Button(
            self.root, text="Sort", command=self.sort, font=("Helvetica", 12)
        )
        self.sort_button.pack(pady=10)
        self.sort_button.config(state=tk.DISABLED)  # Set disabled as default

    def set_default_threshold(self):
        if self.checkbox_value.get():  # self.checkbox.get() == True:
            self.slider.set(100)
            self.slider.config(state=tk.DISABLED)
        else:
            self.slider.config(state=tk.NORMAL)

    def select_folder(self):
        """
        Handles folder selections
        """
        # If a different folder is loaded already
        if self.folder_path:
            # Reset initialized variables or any packed widgets
            self.picturesList.clear()
            self.blurValues.clear()
            self.sort_progress_bar.pack_forget()
            self.sort_progress_label.pack_forget()
            self.completion_label.pack_forget()
            self.result_label.pack_forget()
            self.sort_button.config(state=tk.DISABLED)
            self.num_blurry = 0

            self.folder_path = filedialog.askdirectory()
            self.init_vars()  # which will display an image for the first time
        # If no folders are loaded yet
        else:
            self.folder_path = filedialog.askdirectory()
            self.init_vars()

    def init_vars(self):
        """
        Starts the process of the computing blur values
        """
        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith(("png", "jpg", "jpeg", "bmp")):
                image_path = os.path.join(self.folder_path, filename)
                self.picturesList.append(image_path)

        # Compute blur values for each image
        # self.blurValues = list(map(self.compute_blurVal, self.picturesList))
        threading.Thread(target=self.process_images, daemon=True).start()

        self.select_button.config(state=tk.DISABLED)

        # Let user know that blur analysis is in progress
        self.result_label = tk.Label(
            self.root,
            text="Blur Analysis in progress!",
            font=("Helvetica", 12),
        )
        self.result_label.pack()

    def process_images(self):
        """
        Applies laplacian to compute a blur value to a list of images using map and a thread
        """
        # Progress bar for computing blur values per image
        self.blur_progress_label = tk.Label(
            self.root, text="Progress:", font=("Helvetica", 12)
        )
        self.blur_progress_label.pack()
        self.blur_progress_bar = ttk.Progressbar(
            self.root, orient=tk.HORIZONTAL, length=300, maximum=len(self.picturesList)
        )
        self.blur_progress_bar.pack(pady=10)

        # Compute the blur values for each image
        for pic in self.picturesList:
            self.blurValues.append(self.compute_blurVal(pic))
            self.blur_progress_bar["value"] += 1

        # End thread and update the gui
        self.root.after(0, self.update_gui)

    def compute_blurVal(self, image_path):
        """
        Computes the laplacian blur value of one image

        :param image_path: path to the image file
        :type image_path: str
        """
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        print(cv2.Laplacian(image, cv2.CV_64F).var())
        return cv2.Laplacian(image, cv2.CV_64F).var()

    def update_gui(self):
        """
        Updates gui after blur values of images are computed
        """
        print("Image processing complete!")

        # Notify user of finished blur analysis
        self.result_label.config(text="Blur Analysis complete!")
        self.result_label.pack()

        self.sort_button.config(state=tk.NORMAL)  # Set sort button normal

        # Remove blur progress bar
        self.blur_progress_label.pack_forget()
        self.blur_progress_bar.pack_forget()

        # Progress bar
        self.sort_progress_label = tk.Label(
            self.root, text="Progress:", font=("Helvetica", 12)
        )
        self.sort_progress_label.pack()
        self.sort_progress_bar = ttk.Progressbar(
            self.root, orient=tk.HORIZONTAL, length=300, maximum=len(self.picturesList)
        )
        self.sort_progress_bar.pack(pady=10)

        # Completion label
        self.completion_label = tk.Label(self.root, text="", font=("Helvetica", 12))
        self.completion_label.pack()

    # execute keep, dicard, maybe
    def sort(self):
        if self.folder_path:
            # create folders
            if not os.path.exists(self.folder_path + "/Keep"):
                os.mkdir(self.folder_path + "/Keep")
            if not os.path.exists(self.folder_path + "/Discard"):
                os.mkdir(self.folder_path + "/Discard")

            # execute
            # self.num_blurry = 0
            for i in range(len(self.picturesList)):
                # print(self.slider.get())
                if self.blurValues[i] < self.slider.get():
                    copy2(self.picturesList[i], self.folder_path + "/Discard")
                    self.num_blurry += 1
                else:
                    copy2(self.picturesList[i], self.folder_path + "/Keep")

                # Update the progress bar
                self.sort_progress_bar["value"] += 1
                self.root.update_idletasks()

            self.completion_label.config(
                text=f"Sorting Complete! There were {self.num_blurry} blurry images"
            )

            self.select_button.config(state=tk.NORMAL)
            self.sort_button.config(state=tk.DISABLED)

            # self.blurry_label.config(text=str(self.num_blurry)+" pictures are too blurry and have been removed.")
            # self.blurry_label.pack()


# -------------

if __name__ == "__main__":
    root = tk.Tk()
    app = BlurSortApp(root)
    root.mainloop()
