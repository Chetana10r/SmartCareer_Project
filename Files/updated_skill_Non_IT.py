# ✅ Improved Version of Skills_NON_IT.ipynb

import pandas as pd
import re
import string
import spacy
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# --------------------
# 🔧 Text Preprocessing
# --------------------
def clean_and_lemmatize(text):
    text = re.sub(r"<[^>]+>", "", str(text))
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.lower()
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

# --------------------
# 📄 Load Dataset
# --------------------
df = pd.read_csv("resume_data_Non_IT_5000_updated.csv")
print(df.columns)

df["combined"] = df["Keywords"].fillna("") + " " + df["Technologies"].fillna("")
df.dropna(subset=["combined", "Skills"], inplace=True)
df["cleaned"] = df["combined"].apply(clean_and_lemmatize)

# --------------------
# 🏷️ Prepare Labels
# --------------------
df["Skills"] = df["Skills"].apply(lambda x: [s.strip().lower() for s in x.split(",")])
mlb = MultiLabelBinarizer()
y = mlb.fit_transform(df["Skills"])

# --------------------
# 🔢 TF-IDF Features
# --------------------
tfidf = TfidfVectorizer(ngram_range=(1,2), max_features=5000)
X = tfidf.fit_transform(df["cleaned"])

# --------------------
# 🔍 Train-Test Split
# --------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --------------------
# 🤖 Model Training
# --------------------
model = OneVsRestClassifier(LogisticRegression(max_iter=300))
model.fit(X_train, y_train)

# --------------------
# 📊 Evaluation
# --------------------
y_pred = model.predict(X_test)
print("\nClassification Report (Non-IT Skill Prediction):\n")
print(classification_report(y_test, y_pred, target_names=mlb.classes_))

# --------------------
# 💾 Save Artifacts
# --------------------
joblib.dump(model, "models/Non_IT_skill_model.pkl")
joblib.dump(tfidf, "models/Non_IT_tfidf.pkl")
joblib.dump(mlb, "models/Non_IT_mlb.pkl")
