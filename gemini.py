# Authors: Branden Bulatao, Matthew Kribs, Hashil Patel
# Description: Test for Gemini file

import google.generativeai as genai
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

print(os.getenv("GEMINI_API_KEY"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(
    [{"text": "Can you give me a one photography theme? Format in python dictionary"}]
)

print(response.text)
