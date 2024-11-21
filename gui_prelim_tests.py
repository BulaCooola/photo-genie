from tkinter import *
from PIL import ImageTk, Image
import os

root = Tk()
img = ImageTk.PhotoImage(Image.open("_DSC3940.JPG"))
panel = Label(root, image=img)
panel.pack(side="bottom", fill="both", expand="yes")
root.mainloop()

# %%
# https://stackoverflow.com/questions/19895877/tkinter-cant-bind-arrow-key-events
from tkinter import *

main = Tk()


def leftKey(event):
    print("Left key pressed")


def rightKey(event):
    print("Right key pressed")


frame = Frame(main, width=100, height=100)
main.bind("<Left>", leftKey)
main.bind("<Right>", rightKey)
frame.pack()
main.mainloop()

# %%
# cv2 seems easier than tkinter
# https://stackoverflow.com/questions/59270464/python-navigate-through-and-show-images-in-a-folder

# https://stackoverflow.com/questions/61735195/i-am-trying-to-build-an-image-viewer-using-tkinter-but-i-am-stuck-at-this-weird

# %%
# scroll with arrow keys

from tkinter import *
from PIL import ImageTk, Image
import os


def moveForward(event):
    global current_img
    global currImageIndex
    global imgLabel
    currImageIndex += 1

    imgLabel.grid_forget()
    # print(picturesList)
    img = ImageTk.PhotoImage(
        Image.open(picturesList[currImageIndex]).resize((500, 500))
    )
    current_img = img
    imgLabel = Label(root, image=img)
    imgLabel.grid(row=0, column=1)


def moveBackward(event):
    global current_img
    global currImageIndex
    global imgLabel
    currImageIndex -= 1

    imgLabel.grid_forget()
    # print(picturesList)
    img = ImageTk.PhotoImage(
        Image.open(picturesList[currImageIndex]).resize((500, 500))
    )
    current_img = img
    imgLabel = Label(root, image=img)
    imgLabel.grid(row=0, column=1)


picturesList = []

# Here is the variable where the reference will be stored
current_img = None
for pictures in os.listdir("Screenshots"):
    if pictures.startswith("Screenshot"):
        picturesList.append("Screenshots/" + pictures)

currImageIndex = 162

root = Tk()
root.resizable(width=True, height=True)

img = ImageTk.PhotoImage(Image.open("_DSC5808_RyanSmith.JPG").resize((500, 500)))
imgLabel = Label(image=img)
imgLabel.grid(row=0, column=1)

root.bind("<Left>", moveForward)
root.bind("<Right>", moveBackward)

root.mainloop()

# %%
# scroll with on-screen buttons
# https://stackoverflow.com/questions/61735195/i-am-trying-to-build-an-image-viewer-using-tkinter-but-i-am-stuck-at-this-weird

from tkinter import *
from PIL import ImageTk, Image
import os


def moveForward():
    global current_img
    global currImageIndex
    global imgLabel
    currImageIndex += 1

    imgLabel.grid_forget()
    # print(picturesList)
    img = ImageTk.PhotoImage(
        Image.open(picturesList[currImageIndex]).resize((500, 500))
    )
    current_img = img
    imgLabel = Label(root, image=img)
    imgLabel.grid(row=0, column=1)


picturesList = []

# Here is the variable where the reference will be stored
current_img = None
for pictures in os.listdir("Screenshots"):
    if pictures.startswith("Screenshot"):
        picturesList.append("Screenshots/" + pictures)

currImageIndex = 162

root = Tk()
root.resizable(width=True, height=True)

img = ImageTk.PhotoImage(Image.open("_DSC5808_RyanSmith.JPG").resize((500, 500)))
imgLabel = Label(image=img)
imgLabel.grid(row=0, column=1)

# backwardImg = ImageTk.PhotoImage(Image.open("Screenshots/backward.ico"))
backButton = Button(text="<", width=80, height=80, relief=FLAT)
backButton.grid(row=0, column=0)


# forwardImg = ImageTk.PhotoImage(Image.open("Screenshots/forward.ico"))
forwardButton = Button(text=">", width=80, height=80, relief=FLAT, command=moveForward)
forwardButton.grid(row=0, column=2)

root.mainloop()
