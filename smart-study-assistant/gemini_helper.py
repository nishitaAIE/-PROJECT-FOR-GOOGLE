from pydantic import BaseModel, Field
from google import genai
from google.genai import types


# ── Flashcard structures ──────────────────────────────────────────────────────

class Flashcard(BaseModel):
    question: str = Field(description="The question or prompt for the front of the flashcard.")
    answer: str = Field(description="The concise answer or explanation for the back of the flashcard.")


class FlashcardList(BaseModel):
    flashcards: list[Flashcard] = Field(description="A list of generated flashcards.")


# ── MCQ Quiz structures ───────────────────────────────────────────────────────

class MCQOption(BaseModel):
    key: str = Field(description="The key identifying the option, must be 'A', 'B', 'C', or 'D'.")
    text: str = Field(description="The text content for this option.")


class MCQQuestion(BaseModel):
    question_text: str = Field(description="The multiple choice question based on the content.")
    options: list[MCQOption] = Field(description="Exactly four options (A, B, C, D).")
    correct_option: str = Field(description="The correct option key ('A', 'B', 'C', or 'D').")
    explanation: str = Field(
        description="Detailed explanation of why the correct option is right and others are wrong."
    )


class Quiz(BaseModel):
    questions: list[MCQQuestion] = Field(description="A list of generated multiple choice questions.")


# ── Client ────────────────────────────────────────────────────────────────────

def get_client(api_key: str = None) -> genai.Client:
    """
    Initialises and returns a Google GenAI client.
    Uses the provided api_key; otherwise falls back to the GEMINI_API_KEY
    environment variable.
    """
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()


# ── Core functions ────────────────────────────────────────────────────────────

def summarize_text(
    client: genai.Client,
    text: str,
    length_option: str = "Medium",
    model: str = "gemini-2.5-flash",
) -> str:
    """Generates a structured Markdown summary of the given text."""
    length_guidelines = {
        "Short": (
            "A brief, highly-condensed summary of about 1-2 paragraphs "
            "focusing only on core takeaways."
        ),
        "Medium": (
            "A balanced summary (3-4 paragraphs) with key sections, "
            "bullet points, and high-yield concepts."
        ),
        "Long": (
            "A detailed, comprehensive summary outlining all major concepts, "
            "sub-sections, and detailed explanations."
        ),
    }

    guideline = length_guidelines.get(length_option, length_guidelines["Medium"])

    prompt = f"""
You are an expert academic tutor and study assistant.
Please summarize the following educational content according to these guidelines:
- Target Length / Style: {guideline}
- Format: Use clean Markdown, bold headers, and structured bullet points.
- Focus: Extract key terms, definitions, core explanations, and any important formulas or steps.
- Tone: Informative, clear, and easy for students to study.

Content to summarize:
---
{text}
---
"""

    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def generate_quiz(
    client: genai.Client,
    text: str,
    num_questions: int = 5,
    model: str = "gemini-2.5-flash",
) -> Quiz:
    """Generates a multiple-choice quiz from the provided text."""
    prompt = f"""
You are an expert educator. Based on the provided study material, generate a multiple choice quiz.

Requirements:
- Number of questions: {num_questions}
- Each question must have exactly 4 options labeled A, B, C, D.
- Ensure questions cover different key concepts from the material.
- Provide a clear, detailed explanation of why the correct option is correct.

Study material:
---
{text}
---
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Quiz,
                temperature=0.2,
            ),
        )
        return response.parsed
    except Exception as e:
        return Quiz(
            questions=[
                MCQQuestion(
                    question_text=f"Failed to generate quiz due to an error: {str(e)}",
                    options=[
                        MCQOption(key="A", text="Check API Key"),
                        MCQOption(key="B", text="Verify Network Connection"),
                        MCQOption(key="C", text="Confirm model selection"),
                        MCQOption(key="D", text="Retry later"),
                    ],
                    correct_option="A",
                    explanation="Please check the logs or ensure your GEMINI_API_KEY is valid.",
                )
            ]
        )


def generate_flashcards(
    client: genai.Client,
    text: str,
    num_flashcards: int = 8,
    model: str = "gemini-2.5-flash",
) -> FlashcardList:
    """Generates active-recall flashcards from the provided text."""
    prompt = f"""
You are a study helper. Generate active-recall flashcards from the provided educational content.

Requirements:
- Number of flashcards: {num_flashcards}
- Front (Question): A conceptual question, term to define, or fill-in-the-blank prompt. Keep it clear and focused.
- Back (Answer): The key definition, formula, process, or answer. Keep it concise, high-yield, and easy to memorize.

Educational content:
---
{text}
---
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FlashcardList,
                temperature=0.3,
            ),
        )
        return response.parsed
    except Exception as e:
        return FlashcardList(
            flashcards=[
                Flashcard(
                    question=f"Error generating flashcards: {str(e)}",
                    answer="Please check your configurations and try again.",
                )
            ]
        )


# ── Entry point (optional smoke-test) ────────────────────────────────────────

if __name__ == "__main__":
    client = get_client()          # uses GEMINI_API_KEY from environment
    sample = "Machine learning is a subset of AI that learns from data."
    print(summarize_text(client, sample, length_option="Short"))