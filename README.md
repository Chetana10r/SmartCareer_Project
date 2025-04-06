# 🚀 SmartCareer – Resume Skill Recommender System

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
resume-skill-recommender/
├── backend/
│   ├── app.py
│   ├── resume_model_IT.pkl
│   └── resume_model_NonIT.pkl
├── client/
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── index.js
│       ├── index.css
│       ├── ResumeRecommender.js
│       ├── ResumeRecommender.css
│       ├── components/
│       │   └── SkillCardSlider.js
├── README.md
```

---

## ⚙️ Getting Started

### 🔧 Backend Setup

```bash
cd backend
pip install Flask flask-cors PyPDF2 scikit-learn spacy
python -m spacy download en_core_web_sm
python app.py
```

- Make sure `resume_model_IT.pkl` and `resume_model_NonIT.pkl` are placed correctly.

---

### 🎨 Frontend Setup

```bash
cd client
npm install
npm start
```

- Replace default `src` and `public` files with this repo's customized versions.
- Ensure dependencies like `axios`, `react-icons`, and Tailwind CSS are installed.

---

## 🧠 Machine Learning Logic

- Models trained separately for **IT** and **Non-IT** categories.
- Uses **TF-IDF vectorization + Cosine Similarity** to compare resume text with reference job descriptions.
- Based on gap analysis, missing skills are detected.
- Skills mapped to curated **Coursera** courses and **job links**.

---

## 💡 Customization Tips

- 🔄 Update `common_skills`, `job_required_skills`, and `job_reference_text` inside `app.py`.
- 🎓 Add more job categories or fetch courses dynamically using APIs (Coursera, Udemy, etc.).
- ✨ UI Enhancements can be done in `ResumeRecommender.css` and `SkillCardSlider.css`.

---

## 🤝 Acknowledgments

- Guided by: **Dr. Smita Bhanap** & **Mrs. Rasika Kulkarni**


