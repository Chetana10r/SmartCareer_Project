# SmartCareer-Project

## Overview

The **Resume Skill Recommender** is a full-stack application that helps job seekers analyze their resumes by:
- Extracting skills from uploaded PDF resumes.
- Predicting the job category using machine learning techniques (TF-IDF + Cosine Similarity).
- Identifying missing skills based on the job role the candidate is applying for.
- Recommending relevant courses (and certifications) to fill the skill gaps.

This project consists of a **Flask backend** and a **React frontend** with a creative, dark-themed UI.

## Features

- **PDF Resume Upload:** Users can upload a text-based PDF resume.
- **Job Role Input:** Users specify the job role they are applying for.
- **Text Extraction:** The backend uses [PyPDF2](https://pypi.org/project/PyPDF2/) to extract text from the PDF.
- **Job Role Prediction:** Uses cosine similarity with TF-IDF vectors to predict the job category.
- **Skill Extraction:** A predefined list of common skills is used to extract relevant skills from the resume text.
- **Gap Analysis:** Compares extracted skills with required skills for the specified job role to identify missing skills.
- **Recommendations:** Provides course recommendations (and a placeholder for certifications) based on the missing skills.
- **Creative UI:** The React frontend uses a dark theme, effective icons (via [react-icons](https://react-icons.github.io/react-icons/)), and a modern layout. Once analysis is complete, only the output is shown.

## Tech Stack

- **Backend:** Python, Flask, Flask-CORS, PyPDF2, scikit-learn, spaCy
- **Frontend:** React, Axios, react-icons
- **ML & NLP:** TF-IDF vectorization, Logistic Regression (for the pre-trained model), Cosine Similarity

## Project Structure

```
my-react-app/
├── package.json
├── public/
│   └── index.html
└── src/
    ├── index.js
    ├── index.css
    ├── ResumeRecommender.js
    └── ResumeRecommender.css
```

- **Backend Files (Flask):**
  - `app.py` – Flask application that handles file uploads, PDF text extraction, job role prediction, skill extraction, gap analysis, and recommendations.
  - `resume_model.pkl` – Pre-trained ML model (trained using a dataset of resumes) used for predicting job categories.
- **Frontend Files (React):**
  - `src/ResumeRecommender.js` – Main React component that manages file uploads, input handling, submission, and displays results.
  - `src/ResumeRecommender.css` – Custom styles for the ResumeRecommender component.
  - `src/index.js` and `src/index.css` – Application entry point and global styles.
  - `public/index.html` – HTML template for the React app.

## Installation & Setup

### Backend Setup

1. **Clone or Download the Repository.**

2. **Install Python Dependencies:**

   Ensure you have Python installed (preferably 3.7+), then install the required packages:

   ```bash
   pip install Flask flask-cors PyPDF2 scikit-learn spacy
   python -m spacy download en_core_web_sm
   ```

3. **Place Your Pre-Trained Model:**

   Ensure your `resume_model.pkl` file (trained using your dataset) is in the backend directory.

4. **Run the Flask Server:**

   In your backend directory, run:

   ```bash
   python app.py
   ```

   The server should start on `http://127.0.0.1:5000`.

### Frontend Setup

1. **Create the React App (if not already created):**

   If you haven't already, create a React project using Create React App:

   ```bash
   npx create-react-app my-react-app
   cd my-react-app
   ```

2. **Replace the Default Files:**

   Replace or create the following files with the content provided in this project:
   
   - `public/index.html`
   - `src/index.js`
   - `src/index.css`
   - `src/ResumeRecommender.js`
   - `src/ResumeRecommender.css`

3. **Install Frontend Dependencies:**

   In your React project directory, run:

   ```bash
   npm install axios react-icons
   ```

4. **Run the React App:**

   Start the development server:

   ```bash
   npm start
   ```

   The app will typically run on `http://localhost:3000`.

## Usage

1. **Open the React App:**  
   Navigate to `http://localhost:3000` in your browser.

2. **Upload Your Resume:**  
   Click on the "Upload Resume" button to select a PDF file. Ensure your PDF is text-based (not a scanned image).

3. **Enter Job Role:**  
   Provide the job role you are applying for in the input field.

4. **Check Analysis:**  
   Click on the "Check Analysis" button. Once processed, the input form will hide and the results (predicted job category, extracted skills, missing skills, recommended courses, and certifications) will be displayed on the output screen.

## Customization & Further Development

- **Modify Reference Texts & Skills:**  
  Adjust the `job_reference_text`, `common_skills`, and `job_required_skills` in `app.py` to better fit your dataset and target job roles.
  
- **Enhance Certification Recommendations:**  
  Currently, certifications are a placeholder. You can extend this functionality by mapping skills to relevant certifications.

- **UI Improvements:**  
  Customize the CSS in `ResumeRecommender.css` to further refine the visual design.

- **Error Handling:**  
  Enhance error handling in both the backend and frontend for a smoother user experience.

## Contributing

Contributions, suggestions, and bug reports are welcome! Feel free to fork the repository and submit pull requests.

## License

This project is licensed under the MIT License.
