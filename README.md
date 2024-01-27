# Vision Task for Diagnosis Please Quizzes


This repository provides example codes of models that investigate how advanced language models like *GPT-4 Vision* and *Gemini Pro Vision* can assist in diagnosing health conditions using images.

---
#
## *Getting Started*

This guide will help you set up and run this project on your computer.   
#
#   
## *Prerequisites*
Before starting, you need *Python 3.x* and some other tools installed on your computer. 

All the necessary tools are listed in the requirements.txt file.   
#
#   

## *Installation*
To install all required tools, run the following command:

```bash
pip install -r requirements.txt
```
   
#
#   
## *Securely Storing API Keys*
We use a .env file to securely store essential API keys. 

Make sure to set up your .env file like this:

```makefile
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Replace the placeholders with your actual API keys to keep them secure and separate from your main code.
   
#
#   
## *Workflow*
First, download the "Diagnosis-Please-Quizzes" PDF documents and place them in a pdfs folder. 

Then, preprocess the PDF documents by running the 00.Transform_PDF.py script, followed by either 01.GPT.py or 01.GEMINI.py to analyze the images.

#
#
## *Project Files*
00.Transform_PDF.py: Preprocesses the PDF documents in the pdfs folder into images and texts.
```bash
python 00.Transform_PDF.py
```

01.GPT.py: Analyzes the preprocessed images using the GPT-4 Vision model.
```bash
python 01.GPT.py
```
01.GEMINI.py: Analyzes the preprocessed images using the Gemini Pro Vision model.
```bash
python 01.GEMINI.py
```

#
#
## *Contributing*
We welcome suggestions and bug reports. Your contributions are much appreciated.

#
#
## *License*
This project is available under the MIT License.
