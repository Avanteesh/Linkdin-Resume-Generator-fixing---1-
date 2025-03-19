from flask import Flask, request, send_file, render_template, redirect
import os
from bs4 import BeautifulSoup
import requests
from fpdf import FPDF

app = Flask(__name__)

def scrape_linkedin_profile(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Content-Type": "text/html",
        "Accept-Language":'en-US,en;q=0.5',
        "authority": "www.google.com"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract name
        name_element = soup.find("h1", class_="text-heading-xlarge")
        name = name_element.get_text(strip=True) if name_element else "Name not found"

        # Extract headline
        headline_element = soup.find("div", class_="text-body-medium")
        headline = headline_element.get_text(strip=True) if headline_element else "Headline not found"

        # Extract summary
        summary_element = soup.find("div", class_="pv-about__summary-text")
        summary = summary_element.get_text(strip=True) if summary_element else "Summary not found"

        # Extract experience
        experience = []
        for exp in soup.find_all("li", class_="experience-item"):
            title_element = exp.find("h3", class_="t-16 t-bold")
            company_element = exp.find("p", class_="pv-entity__secondary-title")
            if title_element and company_element:
                experience.append({
                    "title": title_element.get_text(strip=True),
                    "company": company_element.get_text(strip=True)
                })

        return {
            "name": name,
            "headline": headline,
            "summary": summary,
            "experience": experience
        }

def generate_resume(data, filename="resume.pdf"):
    # Ensure the "resumes" folder exists
    if not os.path.exists("resumes"):
        os.makedirs("resumes")
    # Full path for the PDF file
    pdf_path = os.path.join("resumes", filename)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Add name
    pdf.cell(200, 10, txt=f"Name: {data['name']}", ln=True, align='C')
    # Add headline
    pdf.cell(200, 10, txt=f"Headline: {data['headline']}", ln=True, align='C')
    # Add summary
    pdf.multi_cell(0, 10, txt=f"Summary: {data['summary']}")
    # Add experience
    pdf.cell(200, 10, txt="Experience:", ln=True)
    for exp in data['experience']:
        pdf.cell(200, 10, txt=f"{exp['title']} at {exp['company']}", ln=True)
    # Save the PDF in the "resumes" folder
    pdf.output(pdf_path)
    return pdf_path

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/error", methods=["GET"])
def errorPage():
    return render_template("error.html")

@app.route("/handle-profile", methods=["POST"])
def handleProfile():
    url = request.form.get("url")
    profile_data = scrape_linkedin_profile(url)
    if profile_data is None:
        return redirect("/error", status_code=303)  
    resume_filename = "resume.pdf"
    resume_path = generate_resume(profile_data, resume_filename)
    return send_file(resume_path, as_attachment=True)
    
if __name__ == "__main__":
    app.run(debug=True)    
