# 🚀 SmartCareer – Resume Skill Recommender System

A complete full-stack AI-powered Resume Analyzer and Skill Recommender System that helps candidates understand where they stand and what they need to grow in their professional journey.
🔹 Predict job domains, extract resume skills, find missing ones, and recommend job roles, certifications, and courses. Works for both IT and Non-IT sectors.
A full-stack application that **analyzes resumes**, **identifies missing skills**, and **recommends**:
- 🔍 Suitable **Job Roles**
- 🎓 Relevant **Courses & Certifications**
- 💼 Matching **Job Opportunities**

Built using **ReactJS** (Frontend), **Flask** (Backend), and **Machine Learning Models** for both **IT** and **Non-IT** job sectors. Features a responsive, creative **dark-themed UI** with animated, scrollable skill cards and a dot-based slider.

---

## 🌟 Features

- ✅ Upload PDF Resume (Text-based)
- 🧠 Predict Job Category using ML
- 📌 Extract Relevant & Missing Skills
- 🎯 Role-based Suggestions (IT / Non-IT)
- 📚 Recommend Courses & Certifications
- 💼 Show Jobs (via Naukri/LinkedIn)
- ⚡ Beautiful UI with dot-slider cards
- 📱 Fully Responsive and Dark Themed
- 🌟 Clean and Interactive Dark UI
- 🔄 Works with text-based & scanned resumes using OCR fallback

---

## 💠 Tech Stack

| Frontend        | Backend       | Machine Learning         | Styling & UI        |
|----------------|---------------|---------------------------|---------------------|
| ReactJS         | Flask          | TF-IDF, Cosine Similarity | Tailwind CSS, Custom CSS |
| Axios           | Python         | Logistic Regression       | React Icons (Lucide) |
| HTML/CSS/JS     | Flask-CORS     | spaCy, sklearn, pandas    | Animations, Dots Carousel |

---

## 📁 Project Structure

```
SmartCareer_Project/
│
├── IT/
│   ├── IT_Role_Prediction.ipynb
│   ├── IT_Skill_Recommendation.ipynb
│   └── resume_data_IT_5000_updated.csv
│
├── Non_IT/
│   ├── Non_IT_Role_Prediction.ipynb
│   ├── Non_IT_Skill_Recommendation.ipynb
│   └── resume_data_Non_IT_5000_updated.csv
│
├── Streamlit_App/
│   ├── app.py
│   ├── utils.py
│   ├── requirements.txt
│   ├── models/
│   │   ├── it_role_model.pkl
│   │   ├── non_it_role_model.pkl
│   │   ├── it_skill_model.pkl
│   │   ├── nonit_skill_model.pkl
│   │   ├── it_course_model.pkl
│   │   ├── nonit_course_model.pkl
│   │   ├── it_cert_model.pkl
│   │   ├── nonit_cert_model.pkl
│   │   └── vectorizers/
│   │       ├── it_tfidf.pkl
│   │       └── nonit_tfidf.pkl
│   └── data/
│       └── sample_resumes/
│           ├── resume1.pdf
│           └── resume2.pdf
│
├── client/
│   ├── package.json
│   ├── package-lock.json
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js
│   │   ├── index.css
│   │   ├── components/
│   │   │   ├── ResumeUpload.jsx
│   │   │   ├── SkillRecommender.jsx
│   │   │   └── RolePredictor.jsx
│   │   └── assets/
│   │       └── logo.png
│
├── static/
│   └── logo.png
│
├── README.md
└── LICENSE
```

---

## ⚙️ Getting Started

### 🔧 Backend Setup

```bash
# cd backend
cd Streamlit_App # if using streamlit app
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
```

- Make sure `resume_model_IT.pkl` and `resume_model_NonIT.pkl` are placed correctly.
- Make sure Tesseract-OCR is installed and pytesseract.pytesseract.tesseract_cmd path is correctly set.

---

### 🎨 Frontend Setup(React)

```bash
cd client
npm install
npm start
```
- Open http://localhost:3000 to view it in the browser.
- Replace default `src` and `public` files with this repo's customized versions.
- Ensure dependencies like `axios`, `react-icons`, and Tailwind CSS are installed.

---

## 🧠 Machine Learning Logic

- Preprocessing resumes using regex + spaCy lemmatization
- Models trained separately for **IT** and **Non-IT** categories.
- Uses **TF-IDF vectorization + Cosine Similarity** to compare resume text with reference job descriptions.(max_features=5000)
- Based on gap analysis, missing skills are detected.
- Skills mapped to curated **Coursera** courses and **job links**.

- Separate models are trained for:
* IT Sector: Python, ML, React, Cloud, etc.
* Non-IT Sector: Communication, Sales, Excel, etc.
* OCR fallback ensures scanned PDFs are handled properly.

---

## 💡 Customization Tips

- 🔄 Update `common_skills`, `job_required_skills`, and `job_reference_text` inside `app.py`.
- 🎓 Add more job categories or fetch courses dynamically using APIs (Coursera, Udemy, etc.).
- 🚀 UI Enhancements can be done in `ResumeRecommender.css` and `SkillCardSlider.css`.
- ✨ Export recommendations as downloadable PDF
- 🌍 Providing real-time job openings for the repective job role.

---

## 🤝 Team and Mentors

- Chetana Rane , Pranjali Tade , Vijayan Naidu
- Guided by: **Dr. Smita Bhanap** & **Mrs. Rasika Kulkarni**
-  Fergusson College (Autonomous) Pune, Maharashtra

## 📁 License
This project is licensed under the MIT License.
