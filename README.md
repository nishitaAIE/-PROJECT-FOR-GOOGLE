# ✨ Smart Study Assistant
An AI-powered academic helper built using **Streamlit** and the official **Google GenAI Python SDK** (`google-genai`). The web application transforms notes, articles, or PDF documents into structured study suites featuring interactive summaries, multiple-choice quizzes, and dynamic flipping flashcards.
This project was built for educational purposes and provides a hands-on implementation of Google's state-of-the-art Gemini generative models.
---
## 🛠️ Key Features
1.  **📝 Structured Summarization**:
    *   Generates summaries at three custom lengths (Short, Medium, Long).
    *   Leverages standard text generation via `client.models.generate_content`.
    *   Formats outputs into clean, easily readable Markdown with key terms and bullet points.
2.  **🧠 Interactive MCQ Quizzes**:
    *   Creates dynamic, targeted multiple-choice questions from the uploaded material.
    *   Enforces structured JSON generation using Gemini's structured output configuration with Pydantic (`Quiz` and `MCQQuestion` schemas).
    *   Features an active quiz-taking interface with instant grading, color-coded correct/incorrect indicators, score reporting, and detailed conceptual explanations.
3.  **🗂️ Active-Recall Flashcards**:
    *   Extracts definition terms, active-recall questions, and formulas.
    *   Generates structured card objects using Pydantic validation (`FlashcardList`).
    *   Offers two study interfaces:
        *   *Interactive Hover Grid*: CSS-based 3D flip card transition showing questions and answers when hovered or tapped.
        *   *Classic Slideshow Trainer*: Sequentially trains cards with "Reveal Answer" and navigation buttons.
4.  **📁 Flexible File Upload & Inputs**:
    *   Supports text pasting.
    *   Allows uploading `.txt` and `.pdf` files (with automatic text extraction via `pypdf`).
    *   Includes preloaded sample notes (Machine Learning and Photosynthesis) for immediate testing.
---
## 📁 Directory Structure
```text
smart-study-assistant/
│
├── app.py                  # Main Streamlit web application & UI styling
├── gemini_helper.py        # Gemini API configurations & Pydantic schemas
├── requirements.txt        # Python library dependencies
├── .env.example            # Environment variables placeholder
├── README.md               # Project documentation
└── sample_notes/           # Preloaded study material examples
    ├── machine_learning.txt
    └── photosynthesis.txt
```
---
## 🚀 Quick Start & Installation
### Prerequisite
*   Python 3.9 or higher installed on your system.
*   A Gemini API Key (Get one from [Google AI Studio](https://aistudio.google.com/)).
### 1. Clone or Copy the Project
Ensure all files are arranged in the directory structure shown above.
### 2. Set Up a Virtual Environment (Optional but Recommended)
Open a terminal in the project directory and run:
```bash
# Create virtual environment
python -m venv venv
# Activate virtual environment
# On Windows (Command Prompt)
venv\Scripts\activate
# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# On macOS/Linux
source venv/bin/activate
```
### 3. Install Dependencies
Install the required packages using pip:
```bash
pip install -r requirements.txt
```
### 4. Configure Environment Variables
Copy `.env.example` to a new file named `.env`:
```bash
# On Windows
copy .env.example .env
# On macOS/Linux
cp .env.example .env
```
Open `.env` in a text editor and enter your Gemini API Key:
```env
GEMINI_API_KEY=AIzaSyYourActualAPIKeyHere...
```
*Note: If you choose not to create a `.env` file, you can also enter your API key directly inside the app's sidebar interface.*
### 5. Run the Application
Start the Streamlit development server:
```bash
streamlit run app.py
```
A browser window should automatically open to `http://localhost:8501`. If it doesn't, navigate to that URL in your browser.
---
## 🧠 Gemini API Integration Details
### Standard Content Generation
Summarization uses the standard generation interface:
```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)
```
### Structured Output Configuration
Quizzes and Flashcards enforce JSON output using Pydantic models to guarantee valid structured data shapes:
```python
from pydantic import BaseModel
from google.genai import types
class Flashcard(BaseModel):
    question: str
    answer: str
class FlashcardList(BaseModel):
    flashcards: list[Flashcard]
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=FlashcardList,
        temperature=0.3
    )
)
# Access the automatically-parsed object directly
flashcard_data = response.parsed
```