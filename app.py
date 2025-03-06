from dotenv import load_dotenv
import streamlit as st
import os
import io
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Load environment variables
load_dotenv()

# Configure Google Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("GOOGLE_API_KEY not found. Please set it in your environment variables.")
    st.stop()

genai.configure(api_key=API_KEY)

def get_gemini_response(prompt):
    """Generate a response using Google Gemini API."""
    if not prompt.strip():
        return "Error: Prompt is empty. Please provide a valid prompt."
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, f"Add unique variations each time this prompt is called: {os.urandom(8).hex()}"])
        if hasattr(response, 'text') and response.text:
            return response.text
        else:
            return "Error: No valid response received from Gemini API."
    except Exception as e:
        st.error(f"API call failed: {str(e)}")
        return f"Error: {str(e)}"

st.set_page_config(page_title="A5 ATS Resume Expert", layout='wide')

# Header with a fresh style
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>MY PERSONAL ATS</h1>
    <hr style='border: 1px solid #4CAF50;'>
""", unsafe_allow_html=True)

# Input section with better layout
col1, col2 = st.columns(2)

with col1:
    input_text = st.text_area("📋 Job Description:", key="input", height=150)

uploaded_file = None
resume_text = ""
with col2:
    uploaded_file = st.file_uploader("📄 Upload your resume (PDF)...", type=['pdf'])
    if uploaded_file:
        st.success("✅ PDF Uploaded Successfully.")
        try:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                if page and page.extract_text():
                    resume_text += page.extract_text()
        except Exception as e:
            st.error(f"❌ Failed to read PDF: {str(e)}")

# Always visible buttons styled
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>🛠 Quick Actions</h3>", unsafe_allow_html=True)

# Full-width response area
response_container = st.container()

# Ensure response container takes full width
with st.expander("📋 Response", expanded=True):
    response_container = st.empty()

# Button actions
if st.button("📖 Tell Me About the Resume"):
    with st.spinner("⏳ Loading... Please wait"):
        if resume_text:
            response = get_gemini_response(f"Please review the following resume and provide a detailed evaluation: {resume_text}")
            response_container.write(response)
            st.download_button("💾 Download Resume Evaluation", response, "resume_evaluation.txt")
        else:
            st.warning("⚠ Please upload a valid resume first.")

if st.button("📊 Percentage Match"):
    with st.spinner("⏳ Loading... Please wait"):
        if resume_text and input_text:
            response = get_gemini_response(f"Evaluate the following resume against this job description and provide a percentage match in first :\n\nJob Description:\n{input_text}\n\nResume:\n{resume_text}")
            response_container.write(response)
            st.download_button("💾 Download Percentage Match", response, "percentage_match.txt")
        else:
            st.warning("⚠ Please upload a resume and provide a job description.")

learning_path_duration = st.selectbox("📆 Select Personalized Learning Path Duration:", ["3 Months", "6 Months", "9 Months", "12 Months"])
if st.button("🎓 Personalized Learning Path"):
    with st.spinner("⏳ Loading... Please wait"):
        if resume_text and input_text and learning_path_duration:
            response = get_gemini_response(f"Create a detailed and structured personalized learning path for a duration of {learning_path_duration} based on the resume and job description:\n\nJob Description:\n{input_text}\n\nResume:\n{resume_text} and also suggest books and other important thing")
            response_container.write(response)
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Custom', spaceAfter=12))
            story = [Paragraph(f"Personalized Learning Path ({learning_path_duration})", styles['Title']), Spacer(1, 12)]
            for line in response.split('\n'):
                story.append(Paragraph(line, styles['Custom']))
                story.append(Spacer(1, 12))
            doc.build(story)
            st.download_button(f"💾 Download Learning Path PDF", pdf_buffer.getvalue(), f"learning_path_{learning_path_duration.replace(' ', '_').lower()}.pdf", "application/pdf")
        else:
            st.warning("⚠ Please upload a resume and provide a job description.")

if st.button("📝 Generate Updated Resume"):
    with st.spinner("⏳ Loading... Please wait"):
        if resume_text:
            response = get_gemini_response(f"Suggest improvements and generate an updated resume for this candidate according to job description, not more than 2 pages:\n{resume_text}")
            response_container.write(response)

            # Convert response to PDF
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet

            pdf_file = "updated_resume.pdf"
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            styles = getSampleStyleSheet()
            story = [Paragraph(response.replace('\n', '<br/>'), styles['Normal'])]
            doc.build(story)

            # Read PDF as binary
            with open(pdf_file, "rb") as f:
                pdf_data = f.read()

            # Download button for PDF
            st.download_button(label="📥 Download Updated Resume", data=pdf_data, file_name="Updated_Resume.pdf", mime="application/pdf")
        else:
            st.warning("⚠ Please upload a resume first.")


if st.button("❓ Generate 30 Interview Questions and Answers"):
    with st.spinner("⏳ Loading... Please wait"):
        if resume_text:
            response = get_gemini_response("Generate 30 technical interview questions and their detailed answers according to that job description.")
            response_container.write(response)
        else:
            st.warning("⚠ Please upload a resume first.")


if st.button("🚀 Skill Development Plan"):
    with st.spinner("⏳ Loading... Please wait"):
        if resume_text and input_text:
            response = get_gemini_response(f"Based on the resume and job description, suggest courses, books, and projects to improve the candidate's weak or missing skills.\n\nJob Description:\n{input_text}\n\nResume:\n{resume_text}")
            response_container.write(response)
        else:
            st.warning("⚠ Please upload a resume first.")

if st.button("🎥 Mock Interview Questions"):
    with st.spinner("⏳ Loading... Please wait"):
        if resume_text and input_text:
            response = get_gemini_response(f"Generate follow-up interview questions based on the resume and job description, simulating a live interview.\n\nJob Description:\n{input_text}\n\nResume:\n{resume_text}")
            response_container.write(response)
        else:
            st.warning("⚠ Please upload a resume first.")


st.markdown("---")

if st.button("🎯 TCS Data Science Preparation"):
    with st.spinner("⏳ Loading... Please wait"):
        if resume_text:
            response = get_gemini_response("What specific skills, tools, and knowledge should a candidate focus on to get a Data Science role at TCS? Provide a detailed preparation strategy.")
            response_container.write(response)
        else:
            st.warning("⚠ Please upload a resume first.")

if st.button("🎯 Accenture Data Science Preparation"):
    with st.spinner("⏳ Loading... Please wait"):
        if resume_text:
            response = get_gemini_response("What specific skills, tools, and knowledge should a candidate focus on to get a Data Science role at Accenture? Provide a detailed preparation strategy.")
            response_container.write(response)
        else:
            st.warning("⚠ Please upload a resume first.")






















st.markdown("---")


question_category = st.selectbox("❓ Select Question Category:", ["Python", "Machine Learning", "Deep Learning", "Docker", "Data Warehousing", "Data Pipelines", "Data Modeling", "SQL"])

if st.button(f"📝 Generate 30 {question_category} Interview Questions"):
    with st.spinner("⏳ Loading... Please wait"):
        response = get_gemini_response(f"Generate 30 {question_category} interview questions and detailed answers")
        response_container.write(response)
        
# Section for DSA questions based on Data Science
st.markdown("## 🧠 DSA Questions for Data Science")

difficulty_level = st.selectbox("📊 Select Difficulty Level:", ["Easy", "Medium", "Advanced"])

if st.button(f"📝 Generate {difficulty_level} DSA Questions (Data Science)"):
    with st.spinner("⏳ Loading... Please wait"):
        response = get_gemini_response(
            f"Generate 10 {difficulty_level} level Data Science-related DSA questions. "
            f"Provide solutions and explanations for each question. "
            f"Ensure the problems cover important DSA concepts related to data science."
        )
        response_container.write(response)
        