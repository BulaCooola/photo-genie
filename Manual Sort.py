#%%
# I'm currently working on putting the functionality in a class

# 1,2,3 for keep, dicard, maybe
# arrow key shortcuts for displaying the next or previous picture

import tkinter as tk
# from tkinter import *
from PIL import ImageTk, Image
import os
from shutil import copy2 # copy2 preserves more metadata

# path to folder with pics to be sorted
folder_path = 'Screenshots'

def updatePic(currImageIndex):
    global current_img
    global imgLabel
    
    imgLabel.grid_forget()
    # print(picturesList)
    img = ImageTk.PhotoImage(Image.open(picturesList[currImageIndex]).resize((500,500)))
    current_img = img
    imgLabel = tk.Label(root,image=img)
    imgLabel.grid(row=1,column=1)

def moveForward(event=None):
    global current_img
    global currImageIndex
    global imgLabel
    
    currImageIndex += 1
    updatePic(currImageIndex)

def moveBackward(event=None):
    global current_img
    global currImageIndex
    global imgLabel
    
    currImageIndex -= 1
    updatePic(currImageIndex)

picturesList = []

#Here is the variable where the reference will be stored
current_img = None
for pic in os.listdir(folder_path):
    if pic[-3:] in ['png','jpg','jpeg']: # endswith('png'):
        picturesList.append(folder_path+'/'+pic)

currImageIndex = 0

root = tk.Tk()
root.resizable(width=True, height=True)

img = ImageTk.PhotoImage(Image.open(picturesList[currImageIndex]).resize((500,500)))
imgLabel = tk.Label(image=img)
imgLabel.grid(row=1,column=1)

#--------------

title = tk.Label(text="Manual Sort", height = 5)
title.grid(row=0,column=1)

#---------------
# forward and back buttons

w = 20
h = 20

# backwardImg = ImageTk.PhotoImage(Image.open("Screenshots/backward.ico"))
backButton = tk.Button(text='<',width=w,height=h,relief=tk.FLAT, command=moveBackward)
backButton.grid(row=1,column=0)

# forwardImg = ImageTk.PhotoImage(Image.open("Screenshots/forward.ico"))
forwardButton = tk.Button(text='>', width=w, height=h, relief=tk.FLAT, command=moveForward)
forwardButton.grid(row=1,column=2)

root.bind('<Left>', moveBackward)
root.bind('<Right>', moveForward)

#------------
# keep, discard, maybe - functions

sortDict = dict.fromkeys(picturesList)

# keepList = []
# discardList = []
# maybeList = []
# .append(picturesList[currImageIndex])

def keepPic(event=None):
    global currImageIndex
    sortDict[picturesList[currImageIndex]] = 'Keep'
    moveForward()
def discardPic(event=None):
    global currImageIndex
    sortDict[picturesList[currImageIndex]] = 'Discard'
    moveForward()
def maybePic(event=None):
    global currImageIndex
    sortDict[picturesList[currImageIndex]] = 'Maybe'
    moveForward()

#------------
# keep, discard, maybe - buttons

w = 20
h = 10
f1 = tk.Frame(root, borderwidth=1, relief="solid")

keepButton = tk.Button(f1, text='Keep', width=w, height=h, relief=tk.FLAT, command=keepPic)
# keepButton.grid(row=1,column=2)

discardButton = tk.Button(f1, text='Discard', width=w, height=h, relief=tk.FLAT, command=discardPic)
# discardButton.grid(row=1,column=3)

maybeButton = tk.Button(f1, text='Maybe', width=w, height=h, relief=tk.FLAT, command=maybePic)
# maybeButton.grid(row=1,column=4)

keepButton.pack(side="left", fill="both", expand=True) # side="left"
maybeButton.pack(side="right", fill="both", expand=True)
discardButton.pack(fill="x") # side="middle"

f1.grid(row=2,column=1)

#------------
# keep, discard, maybe - keyboard shortcuts

root.bind('1', keepPic)
root.bind('2', discardPic)
root.bind('3', maybePic)

#-------------

root.mainloop()

#-------------
# execute keep, dicard, maybe

# create folders
if not os.path.exists(folder_path+'/Keep'):
    os.mkdir(folder_path+'/Keep')
if not os.path.exists(folder_path+'/Discard'):
    os.mkdir(folder_path+'/Discard')
if not os.path.exists(folder_path+'/Maybe'):
    os.mkdir(folder_path+'/Maybe')

# execute
for pic in sortDict:
    if sortDict[pic] == 'Keep':
        copy2(pic, folder_path+'/Keep')
    elif sortDict[pic] == 'Discard':
        copy2(pic, folder_path+'/Discard')
        # os.remove()
    elif sortDict[pic] == 'Maybe':
        copy2(pic, folder_path+'/Maybe')

# for pic in keepList:
#     copy2(pic,'Screenshots/Keep')
# for pic in discardList:
#     copy2(pic,'Screenshots/Discard')
    # os.remove()
