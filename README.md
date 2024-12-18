# photo-genie
AAI/CPE/EE 551 Project 2

A photography exercise module and photo sorting application that suggests themed challenges for photographers of all experiences and provides feedback on lighting, composition, technical details, and accuracy to a theme using Gemini AI endpoints. 

<img src="readme_images/demo.png" width=70%>

## Instructions

### Packages to install:

You must install the following packages in order for the application to work.
- google.generativeai
- tkinter
- python-dotenv
- pillow
- pymongo
- pytest
- opencv-python

Other packages this project uses:
- threading
- os
- json
- datetime
- shutil
- io
  
```
pip install google-generativeai tk python-dotenv pillow pymongo pytest opencv-python
```

### Setting up API Key for Gemini:
Gemini AI in our application is used as a tool to critique photos and generate themes. In order to be able to use these features, **you must provide a valid API key**. This API key is stored in a `.env` file which the `gemini.py` module processes.

#### 1. Getting the Key
Log in into Google AI for Developers through https://ai.google.dev/. Once you have been authenticated, click on the button that says 
```Get API key in Google AI Studio```. Then, click the ```Create API key``` and copy and paste the API key.

<img src="readme_images/image.png" width=70%>
<img src="readme_images/image-1.png" width=70%>

#### 2. Setting the Key
- In the root of the directory, create a new file named `.env`.
![alt text](readme_images/env.png)
- Next, in a `KEY=VALUE` format, replace *YOUR_API_KEY* with the actual API key and add the following to your `.env` file. Make sure that keys are uppercased, no spaces around `=`, and no need to put quotes around the value
```
GEMINI_API_KEY=YOUR_API_KEY
```

More Documentation on how to setup a Gemini API key:
- https://ai.google.dev/gemini-api/docs/api-key

### Running the program
To run the program, simply run one of the following lines in your terminal on the root of this directory.
```
python main.py
```
or
```
python3 main.py
```

### RECOMMENDED: Seeding database
To run the seed file, simply run one of the following lines in your terminal on the root of this directory.
```
python seed.py
```
or
```
python3 seed.py
```
Please run this once only, or you will get duplicate file entries. The terminal should say "Done Seeding Database" if the seed was successful. 

More instructions on the application :)
