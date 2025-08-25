# COBOL to Java Converter

A Django web application that converts COBOL code to Java using GPT4All AI model with intelligent rule-based fallback conversion.

## Features

- **File Upload Interface**: Upload COBOL files for conversion
- **AI-powered Conversion**: Uses GPT4All Meta-Llama-3-8B model for intelligent code 
- **Special Scenario Handling**:
  - Type casting for numeric variables
  - COPY REPLACING statements with token substitution
  - Undeclared variables detection and SYSVARS generation
- **Java Code Fixes**: Automatic string comparison and operator corrections

## Quick Start

### 1. Setup and Run

```bash
cd /CodeChallenge
source env/bin/activate  
python manage.py runserver 8000
```

### 2. Access the Application

Visit: `http://127.0.0.1:8001/cobol/`

### 3. Convert COBOL Code

1. Click "Choose File" and upload a COBOL file
2. Click "Convert" button
3. View the converted Java code in the right panel
4. Check conversion logs for details

## Technical Details

### AI Model
- **Model**: GPT4All Meta-Llama-3-8B-Instruct.Q4_0.gguf
- **Local Processing**: No internet connection required
- **Fallback**: Rule-based conversion if AI fails

