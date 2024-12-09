# Authors: Branden Bulatao, Matthew Kribs
# Date: 12/2024
# Description: This module handles part of the frontend, and enables users to review a folder of images and sort them in order to cull through
# photos that they want to keep or delete.

# keyboard shortcuts:
# 1,2,3 for keep, dicard, maybe
# arrow keys for displaying the next or previous picture

# this app creates folders (Keep, Discard, Maybe) inside the folder you're sorting.
# maybe there should be a file dialog to chose where you want to put those folders

import tkinter as tk

# from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog, messagebox
import os
from shutil import copy2  # copy2 preserves more metadata

# image not appearing - problem solved - need: self.imgLabel.image = img
# Branden did the same thing - "to avoid garbage collection"
# https://stackoverflow.com/questions/57244479/how-to-display-an-image-in-tkinter-using-grid

WIDTH = 800
HEIGHT = 600


class ManualSortTab:
    # def __init__(self, root):
    def __init__(self, notebook):

        self.frame = tk.Frame(notebook)
        self.folder_path = None
        self.current_img = None
        self.no_picture_label = None
        self.picturesList = []
        self.sortDict = {}
        self.currImageIndex = 0
        self.imageCount = 0

        # image display, initialized in init_vars
        # self.imgLabel = tk.Label(self.root)

        # Configure collumns
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)

        self.manualSort_label = tk.Label(
            self.frame, text="Manual Sort", height=2, font=("Helvetica", 14)
        )
        self.manualSort_label.grid(row=0, column=1)
        # self.manualSort_label.pack(pady=10)

        # select folder
        self.select_button = tk.Button(
            self.frame,
            text="Select Folder",
            command=self.select_folder,
            font=("Helvetica", 12),
        )
        self.select_button.grid(row=1, column=1)

    def select_folder(self):
        """
        By Branden. Helper function for select button for the user to select a folder
        """
        # Handle no_picture_label if that had been triggered
        if self.no_picture_label:
            self.no_picture_label.grid_forget()

        # If a different folder is loaded already
        if self.folder_path:
            # Reset initialized variables
            self.picturesList.clear()
            self.sortDict.clear()
            self.currImageIndex = 0
            self.imageCount = 0

            self.folder_path = filedialog.askdirectory()
            self.select_button.grid_forget()
            self.canvas.grid_forget()
            self.init_vars()
            # which will display an image for the first time\
        # If no folders are loaded yet
        else:
            # Open file dialog
            self.folder_path = filedialog.askdirectory()
            self.select_button.grid_forget()
            self.init_vars()

    # only do this once we get a folder path via the select button / select_folder function
    def init_vars(self):  # initialize some member variables
        """
        Initialize some new member variables for the images. Loads images as well.
        """
        try:
            for filename in os.listdir(self.folder_path):
                if filename.lower().endswith(("png", "jpg", "jpeg", "bmp")):
                    image_path = os.path.join(self.folder_path, filename)
                    self.picturesList.append(image_path)

            if len(self.picturesList) == 0:
                self.no_picture_label = tk.Label(
                    self.frame,
                    text="There are no pictures in this folder. Pick another folder.",
                    font=("Helvetica", 12),
                )
                self.no_picture_label.grid(row=2, column=1)

                # select folder
                self.select_button = tk.Button(
                    self.frame,
                    text="Select Folder",
                    command=self.select_folder,
                    font=("Helvetica", 12),
                )
                self.select_button.grid(row=3, column=1, pady=10)
            else:
                # Record last index
                self.lastIndex = len(self.picturesList) - 1

                # Create a scrollable canvas
                self.canvas = tk.Canvas(self.frame, width=WIDTH, height=HEIGHT)
                self.canvas.grid(row=1, column=1, pady=10)

                # Load Image (one for analyze dimensions, one for loading to GUI)
                fullImg = Image.open(self.picturesList[self.currImageIndex])
                resizedImg = self.resize_image(fullImg, WIDTH, HEIGHT)  # Resize image
                tkImg = ImageTk.PhotoImage(resizedImg)

                # Add the image to the canvas
                self.canvas.create_image(0, 0, anchor=tk.CENTER, image=tkImg)
                self.canvas.image = tkImg

                # select folder
                self.select_button = tk.Button(
                    self.frame,
                    text="Select Folder",
                    command=self.select_folder,
                    font=("Helvetica", 12),
                )
                self.select_button.grid(row=0, column=2, pady=10)

                self.init_navigation()
                self.init_sort_buttons()
                self.init_finish_button()
        except FileNotFoundError as e:
            messagebox.showerror(
                "Error", "Server Error. System cannot find the path specified"
            )

    def updatePic(self, index):
        """
        Updates the picture whenever user presses left, right or keep, maybe, delete

        :param index: Next image index
        :type index: int
        """
        # print(picturesList)
        # Load Image (one for analyze dimensions, one for loading to GUI)
        fullImg = Image.open(self.picturesList[index])
        resizedImg = self.resize_image(fullImg, WIDTH, HEIGHT)  # Resize image
        tkImg = ImageTk.PhotoImage(resizedImg)

        # self.imgLabel.config(image=current_img)
        # self.imgLabel.image = current_img
        self.canvas.create_image(0, 0, anchor=tk.NW, image=tkImg)
        self.canvas.image = tkImg  # Prevent garbage collection

    def resize_image(self, image, screen_height, screen_width):
        """
        Resizes the image to a formattable and readable way for the GUI

        :param image: image file
        :type image: ImageFile
        :param screen_height: preferred height of image
        :type screen_height: int
        :type screen_width: preferred width of image
        :type screen_width: int

        :return: Resized ImageFile
        :rtype: ImageFile
        """
        image_width, image_height = image.size

        # Adjust image dimensions to fit the screen size
        if (image_width / image_height) > (screen_width / screen_height):
            new_width = screen_width
            new_height = int(screen_width / (image_width / image_height))
        else:
            new_height = screen_height
            new_width = int(screen_height * (image_width / image_height))

        # Resize the image
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized_image

    # display next pic
    def moveForward(self, event=None):
        print(self.currImageIndex)
        if self.currImageIndex == self.lastIndex:
            self.currImageIndex = 0
        else:
            self.currImageIndex += 1
        self.updatePic(self.currImageIndex)

    def moveBackward(self, event=None):
        if self.currImageIndex == 0:
            self.currImageIndex = self.lastIndex
            print(self.currImageIndex)
        else:
            self.currImageIndex -= 1
        self.updatePic(self.currImageIndex)

    # ---------------
    # forward and back buttons
    def init_navigation(self):
        # backwardImg = ImageTk.PhotoImage(Image.open("Screenshots/backward.ico"))
        self.backButton = tk.Button(
            self.frame,
            text="<",
            borderwidth=1,
            relief="solid",
            command=self.moveBackward,
            font=("Helvetica", 20),
        )
        self.backButton.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
        # self.backButton.pack(fill=tk.BOTH)

        # forwardImg = ImageTk.PhotoImage(Image.open("Screenshots/forward.ico"))
        self.forwardButton = tk.Button(
            self.frame,
            text=">",
            borderwidth=1,
            relief="solid",
            command=self.moveForward,
            font=("Helvetica", 20),
        )
        # self.backButton.pack(fill=tk.BOTH)
        self.forwardButton.grid(row=1, column=2, padx=10, pady=10, sticky=tk.W)

        self.canvas.bind("<Left>", self.moveBackward)
        self.canvas.bind("<Right>", self.moveForward)

    # ------------
    # keep, discard, maybe - functions

    def keepPic(self, event=None):
        self.sortDict[self.picturesList[self.currImageIndex]] = "Keep"
        self.moveForward()
        self.check_sorting_complete()

    def discardPic(self, event=None):
        self.sortDict[self.picturesList[self.currImageIndex]] = "Discard"
        self.moveForward()
        self.check_sorting_complete()

    def maybePic(self, event=None):
        self.sortDict[self.picturesList[self.currImageIndex]] = "Maybe"
        self.moveForward()
        self.check_sorting_complete()

    def init_sort_buttons(self):
        # ------------
        # keep, discard, maybe - buttons

        w = 5
        h = 2
        # width=w, height=h,
        f1 = tk.Frame(self.frame, width=w, height=h)  # borderwidth=1, relief="solid")

        # Make buttons
        keepButton = tk.Button(
            f1,
            text="Keep",
            width=w,
            height=h,
            command=self.keepPic,
            font=("Helvetica", 15),
        )

        discardButton = tk.Button(
            f1,
            text="Discard",
            borderwidth=1,
            command=self.discardPic,
            font=("Helvetica", 15),
        )

        maybeButton = tk.Button(
            f1,
            text="Maybe",
            borderwidth=1,
            command=self.maybePic,
            font=("Helvetica", 15),
        )

        # Place buttons
        keepButton.grid(row=3, column=0, pady=10, sticky=tk.E)
        maybeButton.grid(row=3, column=1, pady=10)
        discardButton.grid(row=3, column=2, pady=10, sticky=tk.W)

        f1.grid(row=2, column=1)
        self.frame.grid_rowconfigure(2, minsize=100)

        # ------------
        # keep, discard, maybe - keyboard shortcuts

        self.canvas.bind("1", self.keepPic)
        self.canvas.bind("2", self.discardPic)
        self.canvas.bind("3", self.maybePic)
        self.canvas.focus_set()

    def init_finish_button(self):
        """
        Initializes a button to finish culling
        """
        finish_button = tk.Button(
            self.frame,
            text="Finish Sorting",
            command=self.cull,
            font=("Helvetica", 14),
        )
        finish_button.grid(row=0, column=0, pady=20)

    # execute keep, dicard, maybe
    def cull(self, output_folders=None):
        """
        Organizes images into Keep, Discard, and Maybe folders based on user's sorting preferences

        :param output_folders: Dictionary containing custom folder names for each category
        :type output_folders: Dict | None
        """
        # Default folder names
        if output_folders is None:
            output_folders = {"Keep": "Keep", "Discard": "Discard", "Maybe": "Maybe"}

        # Create Folders if they don't exist
        for category, folder_name in output_folders.items():
            folder_path = os.path.join(self.folder_path, folder_name)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

        # execute
        for pic in self.sortDict:
            if self.sortDict[pic] == "Keep":
                self.copy_photo(pic, self.folder_path + "/Keep")
            elif self.sortDict[pic] == "Discard":
                self.copy_photo(pic, self.folder_path + "/Discard")
                # os.remove()
            elif self.sortDict[pic] == "Maybe":
                self.copy_photo(pic, self.folder_path + "/Maybe")

        messagebox.showinfo(
            "Sorting Complete", "All images have been sorted successfully!"
        )

    def copy_photo(self, pic, dest_folder):
        """
        Handles any issues with the files (permission errors, empty folders)
        """
        try:
            copy2(pic, dest_folder)
        except PermissionError:
            print(f"Permission denied: Unable to copy {pic}")
        except FileNotFoundError:
            print(f"File not found: {pic}")

    def check_sorting_complete(self):
        """
        Check if all images have been sorted. If so, alert the user and prompt for culling.
        """
        if len(self.sortDict) == len(self.picturesList):  # All images are sorted
            response = messagebox.askyesno(
                "Sorting Complete",
                "All images are sorted. Would you like to proceed with culling?",
            )
            if response:  # User chose "Yes"
                self.cull()
