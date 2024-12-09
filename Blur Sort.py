# Blurriness metric = variance of Laplacian of grayscale image.
# Slider sets threshold below which pictures are considered too blurry.
# Blurry pictures are copied to Discard folder, the rest are copied to Keep folder.
# The Discard and Keep folders are created inside the folder being sorted.

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
        self.blurValues = [] # blur vals
        # self.num_blurry = 0 # unused
        
        self.title = tk.Label(text="Blur Sort", height = 2, font=('Helvetica',15))
        self.title.pack()
        
        # select folder
        self.select_button = tk.Button(
            self.root,
            text="Select Folder",
            command=self.select_folder,
            font=("Helvetica", 12),
        )
        self.select_button.pack()
        
        self.init_threshold_options()
        
        self.sort_button = tk.Button(
            self.root,
            text="Sort",
            command=self.sort,
            font=("Helvetica", 12)
        )
        self.sort_button.pack(pady=10)
        
        # maybe just a label that says "Done!" would be better
        # self.blurry_label = tk.Label(self.root, font=('Helvetica',10))
        # will only display this once the sort button has been pressed
    
    def init_threshold_options(self):
        self.threshold_frame1 = tk.Frame(self.root)
        
        self.threshold_label = tk.Label(self.threshold_frame1, text="Set Threshold:", font=('Helvetica',12))
        self.threshold_label.pack(side="left") # grid(row=0,column=0)
        
        # current_value = tk.DoubleVar()
        self.slider = tk.Scale(
            self.threshold_frame1,
            from_=0,
            to=100,
            orient='horizontal'
            # variable=current_value
        )
        self.slider.set(100)
        self.slider.pack(side="right") # .grid(row=0,column=1)
        
        self.threshold_frame1.pack()
        self.threshold_frame2 = tk.Frame(self.root)
        
        self.default_label = tk.Label(self.threshold_frame2, text="Set Default Threshold:", font=('Helvetica',12))
        self.default_label.pack(side="left")
        
        self.checkbox_value = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(self.threshold_frame2,
                                       variable = self.checkbox_value,
                                       command=self.set_default_threshold)
        self.checkbox.pack(side="right")
        
        self.threshold_frame2.pack()
    
    def set_default_threshold(self):
        if self.checkbox_value.get(): # self.checkbox.get() == True:
            self.slider.set(100)
            self.slider.config(state=tk.DISABLED)
        else:
            self.slider.config(state=tk.NORMAL)
    
    # only do this once we get a folder path via the select button / select_folder function
    def init_vars(self): # initialize some member variables
        for pic in os.listdir(self.folder_path):
            if pic[-3:] in ['png','jpg','jpeg','bmp']:
                self.picturesList.append(self.folder_path+'/'+pic)
        
        for pic in self.picturesList:
            # print(pic)
            self.blurValues.append(self.compute_blurVal(pic))
        
    def select_folder(self):
        # Open file dialog
        self.folder_path = tk.filedialog.askdirectory()
        # print(self.slider.get())
        # print(folder_path)
        
        if self.folder_path:
            self.init_vars()
            # which will display an image for the first time

            # self.select_button.pack_forget()
            # Disable the upload button - it gets grayed out and cannot be pressed
            # self.upload_button.config(state=tk.DISABLED)

    def compute_blurVal(self,image_path):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        return cv2.Laplacian(image, cv2.CV_64F).var()
    
    # execute keep, dicard, maybe
    def sort(self):
        if self.folder_path:
            # create folders
            if not os.path.exists(self.folder_path+'/Keep'):
                os.mkdir(self.folder_path+'/Keep')
            if not os.path.exists(self.folder_path+'/Discard'):
                os.mkdir(self.folder_path+'/Discard')
            
            # execute
            # self.num_blurry = 0
            for i in range(len(self.picturesList)):
                # print(self.slider.get())
                if self.blurValues[i] < self.slider.get():
                    copy2(self.picturesList[i],self.folder_path+'/Discard')
                    # self.num_blurry += 1
                else:
                    copy2(self.picturesList[i],self.folder_path+'/Keep')
            
            # self.blurry_label.config(text=str(self.num_blurry)+" pictures are too blurry and have been removed.")
            # self.blurry_label.pack()
        
#-------------

if __name__ == "__main__":
    root = tk.Tk()
    app = BlurSortApp(root)
    root.mainloop()
