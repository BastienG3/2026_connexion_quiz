# 2026 Connection Quiz

A Streamlit application for interactive quizzes and connection assessments.

## Features

- Interactive quiz interface
- Real-time score tracking
- User-friendly design
- Quick and easy setup

## Installation Guide
### Prerequisites

#### Install Python
- https://www.python.org/downloads/
- Add to Environment Variables
    - Windows search "Edit the system environment variables"
    - Select "environment variable"
    - Select "Path"
    - Select "Edit"
    - Select "New"
    - Add local Python path
      > C:\Users\\<your-name>\AppData\Local\Programs\Python\Python313
    - Save and quit

#### Create Python Virtual Environment
- Install Virtual Env
  > pip install virtualenv 
- Create new Virtual Environment 
  > virtualenv env 
  or
  (if virtualenv is not recognized from direct execution, using python -m will bypass the PATH)
  > python -m virtualenv env
- Activate the environment
  > .\env\Scripts\activate.ps1
  or
  (if system does not allow execution of ps1)
  > powershell.exe -ExecutionPolicy Bypass -File .\env\Scripts\activate.ps1
- Upgrade pip
  > python.exe -m pip install --upgrade pip
- Install packages
  > pip install -r .\requirements.txt

#### Complete secrets
- Init local secret file from template:
  > cp .streamlit/secrets.example.toml .streamlit/secrets.toml

- Complete secrets with your credentials

## Usage

Run the application with:
```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`
