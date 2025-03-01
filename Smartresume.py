import streamlit as st
import json
import pdfplumber
from fpdf import FPDF
import base64

# Custom PDF class for formatting & borders
class PDF(FPDF):
    def header(self):
        self.set_draw_color(0, 0, 0)
        self.set_line_width(1)
        self.rect(5, 5, 200, 287)  # Page border

    def section_title(self, title):
        self.set_font("Arial", style='B', size=14)
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(2)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())  # Underline section titles
        self.ln(5)

# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text.strip()

# Generate PDF resume
def generate_pdf_resume(user_data):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title (Name)
    pdf.set_font("Arial", style='B', size=20)
    pdf.cell(200, 10, user_data.get("name", "No Name Provided"), ln=True, align='C')
    pdf.ln(5)
    
    # Contact Info
    pdf.set_font("Arial", size=12)
    contact_info = f"Email: {user_data.get('email', 'N/A')} | Phone: {user_data.get('phone', 'N/A')}"
    pdf.cell(0, 10, contact_info, ln=True, align='C')
    
    social_links = f"LinkedIn: {user_data.get('linkedin', 'N/A')} | GitHub: {user_data.get('github', 'N/A')}"
    pdf.cell(0, 10, social_links, ln=True, align='C')
    pdf.ln(10)

    # Objective
    if user_data.get("objective"):
        pdf.section_title("Objective")
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, user_data["objective"])
        pdf.ln(5)

    # Skills
    if user_data.get("skills") and len(user_data["skills"]) > 0:
        pdf.section_title("Skills")
        pdf.multi_cell(0, 10, ", ".join(user_data["skills"]))
        pdf.ln(5)

    # Experience
    if user_data.get("experience") and len(user_data["experience"]) > 0:
        pdf.section_title("Experience")
        for exp in user_data["experience"]:
            pdf.set_font("Arial", style='B', size=12)
            pdf.cell(0, 10, f"{exp.get('role', 'N/A')} - {exp.get('company', 'N/A')} ({exp.get('duration', 'N/A')})", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, exp.get('description', 'No description provided'))
            pdf.ln(5)

    # Education
    if user_data.get("education") and len(user_data["education"]) > 0:
        pdf.section_title("Education")
        for edu in user_data["education"]:
            pdf.set_font("Arial", style='B', size=12)
            pdf.cell(0, 10, f"{edu.get('degree', 'N/A')} - {edu.get('institution', 'N/A')} ({edu.get('year', 'N/A')})", ln=True)
        pdf.ln(5)

    # Achievements
    if user_data.get("achievements") and len(user_data["achievements"]) > 0:
        pdf.section_title("Achievements")
        pdf.multi_cell(0, 10, "\n".join(user_data["achievements"]))
        pdf.ln(5)

    # Save PDF
    pdf_file = "resume.pdf"
    pdf.output(pdf_file, 'F')
    return pdf_file

# Function to display PDF in Streamlit
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Main Streamlit App
def main():
    st.title("Smart Resume Generator")

    input_method = st.sidebar.radio("Choose input method", ["Upload JSON", "Upload PDF", "Manual Entry"])
    uploaded_file = st.sidebar.file_uploader("Upload JSON or PDF", type=["json", "pdf"])
    pdf_file = None

    if input_method == "Upload JSON" and uploaded_file:
        user_data = json.load(uploaded_file)
        st.write("✅ Loaded Data:", user_data)  # Debugging print
        pdf_file = generate_pdf_resume(user_data)
        st.subheader("Resume Preview:")
        display_pdf(pdf_file)

    elif input_method == "Upload PDF" and uploaded_file:
        extracted_text = extract_text_from_pdf(uploaded_file)
        st.subheader("Extracted Text from Resume")
        st.text_area("", extracted_text, height=400)

    elif input_method == "Manual Entry":
        user_data = {
            "name": st.text_input("Full Name"),
            "email": st.text_input("Email"),
            "phone": st.text_input("Phone"),
            "linkedin": st.text_input("LinkedIn URL"),
            "github": st.text_input("GitHub URL"),
            "objective": st.text_area("Objective"),
            "skills": [skill.strip() for skill in st.text_area("Skills (comma-separated)").split(",") if skill.strip()],
            "achievements": [ach.strip() for ach in st.text_area("Achievements (comma-separated)").split(",") if ach.strip()],
            "experience": [],
            "education": []
        }

        num_experience = st.number_input("Number of Experience Entries", min_value=0, step=1)
        for i in range(num_experience):
            with st.expander(f"Experience {i+1}"):
                role = st.text_input(f"Role {i+1}")
                company = st.text_input(f"Company {i+1}")
                duration = st.text_input(f"Duration {i+1}")
                description = st.text_area(f"Description {i+1}")
                user_data["experience"].append({
                    "role": role, "company": company, "duration": duration, "description": description
                })

        num_education = st.number_input("Number of Education Entries", min_value=0, step=1)
        for i in range(num_education):
            with st.expander(f"Education {i+1}"):
                degree = st.text_input(f"Degree {i+1}")
                institution = st.text_input(f"Institution {i+1}")
                year = st.text_input(f"Year {i+1}")
                user_data["education"].append({
                    "degree": degree, "institution": institution, "year": year
                })

        if st.button("Generate Resume"):
            st.write("✅ User Data:", user_data)  # Debugging print
            pdf_file = generate_pdf_resume(user_data)
            st.subheader("Resume Preview:")
            display_pdf(pdf_file)

    if pdf_file:
        with open(pdf_file, "rb") as f:
            st.download_button("Download Resume", f, "resume.pdf")

if __name__ == "__main__":
    main()
