# photo-genie
A CPE 551 Project

A photography exercise module and photo sorting application that suggests themed challenges for photographers of all experiences and provides feedback on lighting, composition, technical details, and accuracy to a theme using Gemini AI endpoints. 


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

```
pip install google-generativeai tk python-dotenv pillow pymongo pytest opencv-python
```

### Setting up API Key for Gemini:
Gemini AI in our application is used as a tool to critique photos and generate themes. In order to be able to use these features, **you must provide a valid API key**. This API key is stored in a `.env` file which the `gemini.py` module processes.

#### 1. Getting the Key
Log in into Google AI for Developers through https://ai.google.dev/. Once you have been authenticated, click on the button that says 
```Get API key in Google AI Studio```. Then, click the ```Create API key``` and copy and paste the API key.

#### 2. Setting the Key
- In the root of the directory, create a new file named `.env`.
- Next, in a `KEY=VALUE` format, replace *YOUR_API_KEY* with the actual API key and add the following to your `.env` file. Make sure that keys are uppercased, no spaces around `=`, and no need to put quotes around the value
```
GEMINI_API_KEY=YOUR_API_KEY
```

More Documentation on how to setup a Gemini API key:
- https://ai.google.dev/gemini-api/docs/api-key

### Running the program
To run the program, simply run the following line in your terminal
```
python main.py
```
or
```
python3 main.py
```