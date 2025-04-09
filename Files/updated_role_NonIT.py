# ✅ Final Improved Version: Role_NON_IT.ipynb (Accuracy Enhanced)

import pandas as pd
import re
import string
import spacy
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.multiclass import OneVsRestClassifier
from sklearn.utils import resample
#import matplotlib.pyplot as plt

# Load spaCy
nlp = spacy.load("en_core_web_sm")

# ------------------------
# 🔧 Text Preprocessing
# ------------------------
def clean_and_lemmatize(text):
    text = re.sub(r"<[^>]+>", "", str(text))
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.lower()
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

# ------------------------
# 📄 Load Dataset
# ------------------------
df = pd.read_csv("resume_data_Non_IT_5000_updated.csv")

# Drop NA in important columns
required_cols = ["Skills", "Job Role", "Keywords", "Technologies"]
df.dropna(subset=required_cols, inplace=True)

# Combine multiple fields for richer features
df["combined"] = df["Skills"] + " " + df["Keywords"] + " " + df["Technologies"]

# Clean text
df["cleaned"] = df["combined"].apply(clean_and_lemmatize)

# ------------------------
# ⚖️ Handle Imbalance (Upsampling minority class to match majority)
# ------------------------
min_class_size = df["Job Role"].value_counts().min()
df_balanced = df.groupby("Job Role").apply(lambda x: resample(x, replace=True, n_samples=min_class_size, random_state=42)).reset_index(drop=True)

X_raw = df_balanced["cleaned"]
y = df_balanced["Job Role"].str.strip()

# ------------------------
# 🔢 TF-IDF Vectorization
# ------------------------
tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=4000)
X = tfidf.fit_transform(X_raw)

# ------------------------
# 🤖 Train-Test Split
# ------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# ------------------------
# 🧠 Train Model
# ------------------------
model = OneVsRestClassifier(LogisticRegression(max_iter=300, class_weight='balanced'))
model.fit(X_train, y_train)

# ------------------------
# 📊 Evaluation
# ------------------------
y_pred = model.predict(X_test)
print("\nClassification Report (Non-IT Role Prediction):\n")
print(classification_report(y_test, y_pred))

'''# Plot Confusion Matrix
cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
disp.plot(xticks_rotation=45)
plt.tight_layout()
plt.show()
'''
# ------------------------
# 💾 Save Artifacts
# ------------------------
joblib.dump(model, "models/Non_IT_job_role_model.pkl")
joblib.dump(tfidf, "models/Non_IT_tfidf.pkl")

