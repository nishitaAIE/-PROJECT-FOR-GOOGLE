import os
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
# Load local environment variables from .env if present
load_dotenv()
import gemini_helper
# Define Custom CSS for Premium Look
CSS_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
/* Apply Outfit font to the app container */
html, body, [data-testid="stAppViewContainer"], .main {
    font-family: 'Outfit', sans-serif;
}
/* Gradient Header */
.header-container {
    padding: 2rem 0rem;
    text-align: center;
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.4), rgba(15, 23, 42, 0.6));
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 2rem;
}
.title-text {
    background: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    font-size: 3rem;
    margin: 0;
    padding-bottom: 0.5rem;
}
.subtitle-text {
    color: #9CA3AF;
    font-size: 1.1rem;
    font-weight: 300;
    margin: 0;
    margin-top: 0.5rem;
}
/* Styling for study material cards */
.study-card {
    background-color: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(12px);
    margin-bottom: 24px;
}
/* Flashcards Container Grid */
.flashcards-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    padding: 15px 0;
}
/* 3D Flipping Card Styling */
.flip-card {
    background-color: transparent;
    height: 220px;
    perspective: 1000px;
}
.flip-card-inner {
    position: relative;
    width: 100%;
    height: 100%;
    text-align: center;
    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    transform-style: preserve-3d;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    border-radius: 16px;
}
/* Flip effect on hover */
.flip-card:hover .flip-card-inner {
    transform: rotateY(180deg);
}
.flip-card-front, .flip-card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    -webkit-backface-visibility: hidden; /* Safari */
    backface-visibility: hidden;
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 24px;
    box-sizing: border-box;
}
/* Card Front: Indigo/Blue Gradient */
.flip-card-front {
    background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
/* Card Back: Dark Deep Purple/Blue */
.flip-card-back {
    background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%);
    color: #E2E8F0;
    transform: rotateY(180deg);
    border: 2px solid #818CF8;
}
.card-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 12px;
    font-weight: 600;
}
.back-label {
    color: #818CF8;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
    font-weight: 600;
}
.card-text {
    font-size: 1.05rem;
    font-weight: 500;
    line-height: 1.5;
}
/* MCQ Quiz Styling */
.quiz-question-box {
    background-color: rgba(30, 41, 59, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border-left: 4px solid #6366F1;
}
.explanation-box {
    background-color: rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    padding: 14px;
    margin-top: 14px;
    font-size: 0.95rem;
    color: #9CA3AF;
    border-left: 2px solid #818CF8;
}
.badge-success {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 8px;
}
.badge-danger {
    background-color: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 8px;
}
.badge-outline {
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #9CA3AF;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 8px;
}
</style>
"""
def extract_text_from_pdf(file) -> str:
    """
    Extracts text from an uploaded PDF file.
    """
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"
# Setup Page Configuration
st.set_page_config(
    page_title="Smart Study Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Inject CSS styles
st.markdown(CSS_STYLE, unsafe_allow_html=True)
# Initialize Session State Keys
state_defaults = {
    "input_text": "",
    "generated_summary": "",
    "generated_quiz": None,
    "generated_flashcards": None,
    "quiz_submitted": False,
    "quiz_selections": {},
    "flashcard_index": 0,
    "flashcard_revealed": False,
    "last_uploaded_file_key": ""
}
for key, default in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default
# Sidebar Callback for Sample Notes
def handle_sample_change():
    selection = st.session_state["sample_selection"]
    if selection == "None (Write/Upload own)":
        return
    
    filepath = ""
    if selection == "📝 Machine Learning":
        filepath = os.path.join("sample_notes", "machine_learning.txt")
    elif selection == "🌿 Photosynthesis":
        filepath = os.path.join("sample_notes", "photosynthesis.txt")
        
    if filepath and os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            st.session_state["input_text"] = f.read()
# ================= SIDEBAR =================
st.sidebar.markdown("### ⚙️ Configurations")
# API Key input with fallback to env variable
env_api_key = os.getenv("GEMINI_API_KEY", "")
api_key_placeholder = "API Key detected from environment" if env_api_key else "Enter your Gemini API Key..."
api_key_input = st.sidebar.text_input(
    "Gemini API Key:",
    type="password",
    placeholder=api_key_placeholder,
    help="Get an API key from Google AI Studio. If left blank, we will try to load GEMINI_API_KEY from environment variables."
)
# Use env variable if text input is empty
active_api_key = api_key_input.strip() if api_key_input.strip() else env_api_key
# Model Choice
model_choice = st.sidebar.selectbox(
    "Choose Gemini Model:",
    ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro"],
    index=0,
    help="gemini-2.5-flash is recommended for speed and efficiency; gemini-2.5-pro is optimal for complex conceptual tasks."
)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Load Materials")
# Sample Notes Selectbox
st.sidebar.selectbox(
    "Use a Sample Note:",
    ["None (Write/Upload own)", "📝 Machine Learning", "🌿 Photosynthesis"],
    key="sample_selection",
    on_change=handle_sample_change
)
# File Uploader
uploaded_file = st.sidebar.file_uploader(
    "Upload Document (.txt, .pdf):",
    type=["txt", "pdf"],
    help="Upload your class notes, textbook chapters, or reference material."
)
# Extract and populate text from uploaded file
if uploaded_file is not None:
    file_key = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state["last_uploaded_file_key"] != file_key:
        st.session_state["last_uploaded_file_key"] = file_key
        
        if uploaded_file.name.endswith(".pdf"):
            extracted = extract_text_from_pdf(uploaded_file)
        else:
            try:
                extracted = uploaded_file.read().decode("utf-8")
            except Exception as e:
                extracted = f"Error reading text file: {str(e)}"
                
        st.session_state["input_text"] = extracted
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="font-size: 0.85rem; color: #6B7280; text-align: center;">
        Made with 💜 using Google Gemini API
    </div>
    """,
    unsafe_allow_html=True
)
# ================= MAIN AREA =================
# Header Section
st.markdown(
    """
    <div class="header-container">
        <h1 class="title-text">✨ Smart Study Assistant</h1>
        <p class="subtitle-text">Transform your raw notes into custom summaries, interactive quizzes, and flipping flashcards using Gemini API.</p>
    </div>
    """,
    unsafe_allow_html=True
)
# Input Section
st.markdown("### 📝 Study Material Input")
input_text_area = st.text_area(
    "Paste your study notes, articles, or chapters below:",
    value=st.session_state["input_text"],
    height=250,
    key="input_text",
    placeholder="Type or paste your educational content here..."
)
# Parameters grid
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    summary_length = st.select_slider(
        "Summary Length:",
        options=["Short", "Medium", "Long"],
        value="Medium"
    )
with col_p2:
    num_questions = st.slider(
        "Quiz Questions:",
        min_value=3,
        max_value=10,
        value=5
    )
with col_p3:
    num_flashcards = st.slider(
        "Flashcards:",
        min_value=4,
        max_value=15,
        value=8
    )
# Action button
generate_button = st.button("🚀 Generate Study Suite", type="primary", use_container_width=True)
if generate_button:
    if not input_text_area.strip():
        st.error("⚠️ Input content cannot be empty! Please paste notes or upload a file.")
    elif not active_api_key:
        st.error("🔑 API Key not found! Please set GEMINI_API_KEY in your environment or enter it in the sidebar.")
    else:
        # Perform API Generation
        try:
            client = gemini_helper.get_client(active_api_key)
        except Exception as e:
            st.error(f"Error creating Gemini client: {e}")
            client = None
            
        if client:
            # Summary
            with st.spinner("📝 Generating Summary..."):
                summary = gemini_helper.summarize_text(
                    client=client,
                    text=input_text_area,
                    length_option=summary_length,
                    model=model_choice
                )
                st.session_state["generated_summary"] = summary
            
            # Quiz
            with st.spinner("🧠 Designing Quiz Questions..."):
                quiz = gemini_helper.generate_quiz(
                    client=client,
                    text=input_text_area,
                    num_questions=num_questions,
                    model=model_choice
                )
                st.session_state["generated_quiz"] = quiz
                # Reset quiz state
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_selections"] = {}
                
            # Flashcards
            with st.spinner("🗂️ Crafting Flashcards..."):
                flashcards = gemini_helper.generate_flashcards(
                    client=client,
                    text=input_text_area,
                    num_flashcards=num_flashcards,
                    model=model_choice
                )
                st.session_state["generated_flashcards"] = flashcards
                st.session_state["flashcard_index"] = 0
                st.session_state["flashcard_revealed"] = False
                
            st.success("🎉 Your personalized Study Suite is ready! Explore the tabs below.")
st.markdown("<br>", unsafe_allow_html=True)
# ================= RESULTS TABS =================
if st.session_state["generated_summary"]:
    tab_summary, tab_quiz, tab_flashcards = st.tabs([
        "📝 Summary & Takeaways",
        "🧠 Practice Quiz",
        "🗂️ Active-Recall Flashcards"
    ])
    
    # -------- Tab 1: Summary --------
    with tab_summary:
        st.markdown("### 📝 Text Summary")
        st.markdown(st.session_state["generated_summary"])
        st.markdown("<br>", unsafe_allow_html=True)
        # Download button for summary
        st.download_button(
            label="📥 Download Summary (Markdown)",
            data=st.session_state["generated_summary"],
            file_name="study_summary.md",
            mime="text/markdown"
        )
        
    # -------- Tab 2: Quiz --------
    with tab_quiz:
        quiz_data = st.session_state["generated_quiz"]
        if quiz_data and quiz_data.questions:
            st.markdown("### 🧠 Interactive Practice Quiz")
            st.write("Review the material, select your answers below, and click **Submit Quiz** to check your score.")
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Render Quiz Questions
            for idx, question in enumerate(quiz_data.questions):
                st.markdown(f"<div class='quiz-question-box'>", unsafe_allow_html=True)
                st.markdown(f"**Question {idx+1}:** {question.question_text}")
                
                # Options mapping
                options_dict = {opt.key: f"{opt.key}) {opt.text}" for opt in question.options}
                option_keys = list(options_dict.keys())
                option_labels = list(options_dict.values())
                
                # Load current choice
                current_choice = st.session_state["quiz_selections"].get(idx, None)
                preselect_idx = option_keys.index(current_choice) if current_choice in option_keys else None
                
                if st.session_state["quiz_submitted"]:
                    # Quiz submitted view: show colored indicators and explanations
                    user_ans = st.session_state["quiz_selections"].get(idx, None)
                    correct_ans = question.correct_option
                    
                    st.write("") # small spacing
                    for opt in question.options:
                        is_user = (opt.key == user_ans)
                        is_correct = (opt.key == correct_ans)
                        
                        if is_correct:
                            st.markdown(f"<span class='badge-success'>✓ {opt.key}</span> <strong>{opt.text}</strong>", unsafe_allow_html=True)
                        elif is_user:
                            st.markdown(f"<span class='badge-danger'>✗ {opt.key}</span> <span style='color: #EF4444; text-decoration: line-through;'>{opt.text}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span class='badge-outline'>{opt.key}</span> <span style='color: #9CA3AF;'>{opt.text}</span>", unsafe_allow_html=True)
                    
                    if user_ans == correct_ans:
                        st.markdown("<div style='color: #10B981; font-weight: 600; margin-top: 10px; font-size: 0.95rem;'>✓ Correct Answer</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='color: #EF4444; font-weight: 600; margin-top: 10px; font-size: 0.95rem;'>✗ Incorrect (You selected {user_ans or 'None'}, correct is {correct_ans})</div>", unsafe_allow_html=True)
                        
                    st.markdown(f"<div class='explanation-box'><strong>Explanation:</strong> {question.explanation}</div>", unsafe_allow_html=True)
                else:
                    # Interactive Mode: Select option
                    choice = st.radio(
                        f"Options for Q{idx+1}",
                        option_labels,
                        index=preselect_idx,
                        key=f"q_radio_input_{idx}",
                        label_visibility="collapsed"
                    )
                    if choice:
                        st.session_state["quiz_selections"][idx] = choice[0] # Store the option key (A, B, C, D)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Quiz submission/reset actions
            if not st.session_state["quiz_submitted"]:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📊 Submit Quiz", type="primary", use_container_width=True):
                    # Check if all questions are answered
                    unanswered = [i+1 for i in range(len(quiz_data.questions)) if i not in st.session_state["quiz_selections"]]
                    if unanswered:
                        st.warning(f"⚠️ You missed answering questions: {', '.join(map(str, unanswered))}. You can still submit, but they will be graded as incorrect.")
                    st.session_state["quiz_submitted"] = True
                    st.rerun()
            else:
                # Grade quiz and show report
                correct_count = sum(
                    1 for i, q in enumerate(quiz_data.questions)
                    if st.session_state["quiz_selections"].get(i) == q.correct_option
                )
                total_count = len(quiz_data.questions)
                score_percentage = (correct_count / total_count) * 100
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 📊 Quiz Summary Report")
                
                metric_col, text_col = st.columns([1, 3])
                with metric_col:
                    st.metric("Final Score", f"{correct_count} / {total_count}", f"{score_percentage:.0f}% Correct")
                with text_col:
                    if score_percentage == 100:
                        st.balloons()
                        st.success("🏆 **Perfect Score!** You have fully mastered this study material!")
                    elif score_percentage >= 80:
                        st.success("🌟 **Excellent Work!** You understand this content exceptionally well.")
                    elif score_percentage >= 60:
                        st.warning("💪 **Good Effort!** Go through the explanations for missed questions to improve.")
                    else:
                        st.error("📚 **Keep Learning!** Re-read the summary, revise the notes, and try again.")
                
                if st.button("🔄 Retake / Reset Quiz", use_container_width=True):
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_selections"] = {}
                    st.rerun()
                    
    # -------- Tab 3: Flashcards --------
    with tab_flashcards:
        flashcards_data = st.session_state["generated_flashcards"]
        if flashcards_data and flashcards_data.flashcards:
            st.markdown("### 🗂️ Active-Recall Study Cards")
            
            study_mode = st.radio(
                "Select Study Interface:",
                ["🎛️ Interactive Hover Grid", "🔄 Classic Slideshow Trainer"],
                horizontal=True
            )
            
            if study_mode == "🎛️ Interactive Hover Grid":
                st.markdown("<p style='font-style: italic; color: #9CA3AF; text-align: center;'>Hover over a card (or tap on mobile) to flip it and reveal the answer.</p>", unsafe_allow_html=True)
                
                grid_html = "<div class='flashcards-container'>"
                for i, card in enumerate(flashcards_data.flashcards):
                    grid_html += f"""
                    <div class='flip-card'>
                        <div class='flip-card-inner'>
                            <div class='flip-card-front'>
                                <div class='card-label'>Front • Card {i+1}</div>
                                <div class='card-text'>{card.question}</div>
                            </div>
                            <div class='flip-card-back'>
                                <div class='back-label'>Back • Answer</div>
                                <div class='card-text'>{card.answer}</div>
                            </div>
                        </div>
                    </div>
                    """
                grid_html += "</div>"
                st.markdown(grid_html, unsafe_allow_html=True)
                
            else:
                # Slideshow Trainer
                cards = flashcards_data.flashcards
                total_cards = len(cards)
                current_idx = st.session_state["flashcard_index"]
                
                # Safeguard bounds
                current_idx = max(0, min(current_idx, total_cards - 1))
                st.session_state["flashcard_index"] = current_idx
                active_card = cards[current_idx]
                
                # Card tracker & Progress bar
                st.markdown(f"<h4 style='text-align: center; color: #818CF8;'>Card {current_idx+1} of {total_cards}</h4>", unsafe_allow_html=True)
                st.progress((current_idx + 1) / total_cards)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # HTML Card display
                if not st.session_state["flashcard_revealed"]:
                    card_markup = f"""
                    <div style="background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%); 
                                color: white; border-radius: 16px; padding: 40px; 
                                text-align: center; min-height: 220px; display: flex; 
                                flex-direction: column; justify-content: center; align-items: center;
                                box-shadow: 0 10px 20px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);">
                        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(255,255,255,0.60); margin-bottom: 15px; font-weight: 600;">Front • Question</div>
                        <div style="font-size: 1.35rem; font-weight: 500; line-height: 1.5;">{active_card.question}</div>
                    </div>
                    """
                else:
                    card_markup = f"""
                    <div style="background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%); 
                                color: #E2E8F0; border-radius: 16px; padding: 40px; 
                                text-align: center; min-height: 220px; display: flex; 
                                flex-direction: column; justify-content: center; align-items: center;
                                box-shadow: 0 10px 20px rgba(0,0,0,0.3); border: 2px solid #818CF8;">
                        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.12em; color: #818CF8; margin-bottom: 15px; font-weight: 600;">Back • Answer</div>
                        <div style="font-size: 1.25rem; font-weight: 400; line-height: 1.5;">{active_card.answer}</div>
                    </div>
                    """
                
                st.markdown(card_markup, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Navigation controls
                c_prev, c_flip, c_next = st.columns([1, 2, 1])
                with c_prev:
                    if st.button("◀ Previous Card", disabled=(current_idx == 0), use_container_width=True):
                        st.session_state["flashcard_index"] -= 1
                        st.session_state["flashcard_revealed"] = False
                        st.rerun()
                with c_flip:
                    flip_btn_label = "🙈 Hide Answer" if st.session_state["flashcard_revealed"] else "👀 Reveal Answer"
                    if st.button(flip_btn_label, type="primary", use_container_width=True):
                        st.session_state["flashcard_revealed"] = not st.session_state["flashcard_revealed"]
                        st.rerun()
                with c_next:
                    if st.button("Next Card ▶", disabled=(current_idx == total_cards - 1), use_container_width=True):
                        st.session_state["flashcard_index"] += 1
                        st.session_state["flashcard_revealed"] = False
                        st.rerun()
else:
    # Notice to show if study materials have not been generated yet
    st.info("💡 Paste notes above or load a sample note/file, then click 'Generate Study Suite' to create summaries, quizzes, and flashcards!")
