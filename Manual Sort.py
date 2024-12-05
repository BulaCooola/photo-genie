# keyboard shortcuts:
# 1,2,3 for keep, dicard, maybe
# arrow keys for displaying the next or previous picture

# this app creates folders (Keep, Discard, Maybe) inside the folder you're sorting.
# maybe there should be a file dialog to chose where you want to put those folders

import tkinter as tk

# from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
import os
from shutil import copy2  # copy2 preserves more metadata

# image not appearing - problem solved - need: self.imgLabel.image = img
# Branden did the same thing - "to avoid garbage collection"
# https://stackoverflow.com/questions/57244479/how-to-display-an-image-in-tkinter-using-grid


class ManualSortApp:
    def __init__(self, root):
        self.root = root
        self.root.resizable(width=True, height=True)

        self.folder_path = None
        self.current_img = None
        self.picturesList = []
        self.sortDict = {}
        self.currImageIndex = 0

        # image display, initialized in init_vars
        # self.imgLabel = tk.Label(self.root)

        title = tk.Label(text="Manual Sort", height=2, font=("Helvetica", 15))
        title.grid(row=0, column=1)

        # select folder
        self.select_button = tk.Button(
            self.root,
            text="Select Folder",
            command=self.select_folder,
            font=("Helvetica", 12),
        )
        self.select_button.grid(row=1, column=1)

    # only do this once we get a folder path via the select button / select_folder function
    def init_vars(self):  # initialize some member variables
        print("hello")
        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith(("png", "jpg", "jpeg", "bmp")):
                image_path = os.path.join(self.folder_path, filename)
                print(image_path)
                self.picturesList.append(image_path)
            print(filename)

        print(self.picturesList)

        img = ImageTk.PhotoImage(
            Image.open(self.picturesList[self.currImageIndex]).resize((500, 500))
        )
        self.imgLabel = tk.Label(self.root, image=img)
        self.imgLabel.image = img
        self.imgLabel.grid(row=1, column=1)

        self.init_navigation()
        self.init_sort_buttons()

    def select_folder(self):
        """
        By Branden. Helper function for select button for the user to select a folder
        """
        # Open file dialog
        self.folder_path = filedialog.askdirectory()
        # print(folder_path)

        if self.folder_path:  # is if statement necessary?
            self.init_vars()
            # which will display an image for the first time

            self.select_button.grid_forget()
            # Disable the upload button - it gets grayed out and cannot be pressed
            # self.upload_button.config(state=tk.DISABLED)

    def updatePic(self):
        # print(picturesList)
        current_img = ImageTk.PhotoImage(
            Image.open(self.picturesList[self.currImageIndex]).resize((500, 500))
        )
        self.imgLabel.config(image=current_img)
        self.imgLabel.image = current_img

    # display next pic
    def moveForward(self, event=None):
        self.currImageIndex += 1
        self.updatePic()

    def moveBackward(self, event=None):
        self.currImageIndex -= 1
        self.updatePic()

    # ---------------
    # forward and back buttons
    def init_navigation(self):
        w = 20
        h = 10
        # width=w, height=h

        # backwardImg = ImageTk.PhotoImage(Image.open("Screenshots/backward.ico"))
        self.backButton = tk.Button(
            text="<",
            borderwidth=1,
            relief="solid",
            command=self.moveBackward,
            font=("Helvetica", 20),
        )
        self.backButton.grid(row=1, column=0)

        # forwardImg = ImageTk.PhotoImage(Image.open("Screenshots/forward.ico"))
        self.forwardButton = tk.Button(
            text=">",
            borderwidth=1,
            relief="solid",
            command=self.moveForward,
            font=("Helvetica", 20),
        )
        self.forwardButton.grid(row=1, column=2)

        self.root.bind("<Left>", self.moveBackward)
        self.root.bind("<Right>", self.moveForward)

    # ------------
    # keep, discard, maybe - functions
    # picDict haha

    def keepPic(self, event=None):
        self.sortDict[self.picturesList[self.currImageIndex]] = "Keep"
        self.moveForward()

    def discardPic(self, event=None):
        self.sortDict[self.picturesList[self.currImageIndex]] = "Discard"
        self.moveForward()

    def maybePic(self, event=None):
        self.sortDict[self.picturesList[self.currImageIndex]] = "Maybe"
        self.moveForward()

    def init_sort_buttons(self):
        # ------------
        # keep, discard, maybe - buttons

        w = 5
        h = 2
        # width=w, height=h,
        f1 = tk.Frame(self.root, width=w, height=h)  # borderwidth=1, relief="solid")

        keepButton = tk.Button(
            f1,
            text="Keep",
            width=w,
            height=h,
            command=self.keepPic,
            font=("Helvetica", 15),
        )
        # keepButton.grid(row=1,column=2)
        # formerly relief=tk.FLAT

        discardButton = tk.Button(
            f1,
            text="Discard",
            borderwidth=1,
            command=self.discardPic,
            font=("Helvetica", 15),
        )
        # discardButton.grid(row=1,column=3)

        maybeButton = tk.Button(
            f1,
            text="Maybe",
            borderwidth=1,
            command=self.maybePic,
            font=("Helvetica", 15),
        )
        # maybeButton.grid(row=1,column=4)

        keepButton.grid(
            row=0, column=0
        )  # pack(side="left", fill="both", expand=True) # side="left"
        discardButton.grid(row=0, column=1)  # pack(fill="x") # side="middle"
        maybeButton.grid(
            row=0, column=2
        )  # pack(side="right", fill="both", expand=True)

        f1.grid(row=2, column=1)
        self.root.grid_rowconfigure(2, minsize=100)

        # ------------
        # keep, discard, maybe - keyboard shortcuts

        root.bind("1", self.keepPic)
        root.bind("2", self.discardPic)
        root.bind("3", self.maybePic)

    # execute keep, dicard, maybe
    def cull(self):
        # create folders
        if not os.path.exists(self.folder_path + "/Keep"):
            os.mkdir(self.folder_path + "/Keep")
        if not os.path.exists(self.folder_path + "/Discard"):
            os.mkdir(self.folder_path + "/Discard")
        if not os.path.exists(self.folder_path + "/Maybe"):
            os.mkdir(self.folder_path + "/Maybe")

        # execute
        for pic in app.sortDict:
            if app.sortDict[pic] == "Keep":
                copy2(pic, self.folder_path + "/Keep")
            elif app.sortDict[pic] == "Discard":
                copy2(pic, self.folder_path + "/Discard")
                # os.remove()
            elif app.sortDict[pic] == "Maybe":
                copy2(pic, self.folder_path + "/Maybe")


# -------------

root = tk.Tk()
# folder_path = 'Screenshots'
app = ManualSortApp(root)
root.mainloop()
app.cull()

# put root = tk.Tk() and root.mainloop() into the app class init?
# then the app's destructor can run the code below to execute the keep, discard, maybe

# -------------
# execute keep, dicard, maybe

# for pic in keepList:
#     copy2(pic,'Screenshots/Keep')
# for pic in discardList:
#     copy2(pic,'Screenshots/Discard')
# os.remove()
