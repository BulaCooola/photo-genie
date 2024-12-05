# blurriness metric = variance of Laplacian of grayscale image.
# slider sets threshold below which pictures are considered too blurry.
# blurry pictures are copied to Discard folder inside folder being sorted

import tkinter as tk
import cv2
import os
from shutil import copy2 # copy2 preserves more metadata

class BlurSortApp:
    def __init__(self, root):
        self.root = root
        self.root.resizable(width=True, height=True)
        
        self.folder_path = None
        self.picturesList = []
        self.LapVars = []
        
        title = tk.Label(text="Blur Sort", height = 2, font=('Helvetica',15))
        title.pack()
        
        # select folder
        self.select_button = tk.Button(
            self.root,
            text="Select Folder",
            command=self.select_folder,
            font=("Helvetica", 12),
        )
        self.select_button.pack()
        
        # current_value = tk.DoubleVar()
        self.slider = tk.ttk.Scale(
            self.root,
            from_=0,
            to=100,
            orient='horizontal',
            # variable=current_value
        )
        self.slider.pack()
        
        self.sort_button = tk.Button(
            self.root,
            text="Sort",
            command=self.sort,
            font=("Helvetica", 12),
        )
        self.sort_button.pack()
    
    # only do this once we get a folder path via the select button / select_folder function
    def init_vars(self): # initialize some member variables
        for pic in os.listdir(self.folder_path):
            if pic[-3:] in ['png','jpg','jpeg','bmp']:
                self.picturesList.append(self.folder_path+'/'+pic)
        
        for pic in self.picturesList:
            # print(pic)
            self.LapVars.append(self.compute_LapVar(pic))
        
        # select folder
        # label for num of pictures
        # slider
        # button that says "Sort"
        # once you click sort, another label appears saying how many pics are too blurry
        
    def select_folder(self):
        # Open file dialog
        self.folder_path = tk.filedialog.askdirectory()
        # print(self.slider.get())
        # print(folder_path)
        
        if self.folder_path: # is if statement necessary?
            self.init_vars()
            # which will display an image for the first time

            # self.select_button.pack_forget()
            # Disable the upload button - it gets grayed out and cannot be pressed
            # self.upload_button.config(state=tk.DISABLED)

    def compute_LapVar(self,image_path):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        return cv2.Laplacian(image, cv2.CV_64F).var()
    
    # execute keep, dicard, maybe
    def sort(self):
        # create folders
        # if not os.path.exists(self.folder_path+'/Keep'):
        #     os.mkdir(self.folder_path+'/Keep')
        # print(self.folder_path)
        if not os.path.exists(self.folder_path+'/Discard'):
            os.mkdir(self.folder_path+'/Discard')
        
        # execute
        for i in range(len(self.picturesList)):
            # print(self.slider.get())
            if self.LapVars[i] < self.slider.get():
                copy2(self.picturesList[i],self.folder_path+'/Discard')

#-------------

root = tk.Tk()
# folder_path = 'Screenshots'
app = BlurSortApp(root)
root.mainloop()
# app.sort()

# put root = tk.Tk() and root.mainloop() into the app class init?
# then the app's destructor can run the code below to execute the keep, discard, maybe

#-------------
# execute keep, dicard, maybe

# for pic in keepList:
#     copy2(pic,'Screenshots/Keep')
# for pic in discardList:
#     copy2(pic,'Screenshots/Discard')
    # os.remove()
