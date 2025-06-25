import joblib
import numpy as np
import json
import re
from textstat import flesch_reading_ease

# ---- Config Paths ----
CONFIG_PATH = "config/config.json"
BUZZWORD_PATH = "config/buzzwordlist.json"

# ---- Load Configurations ----
with open(CONFIG_PATH) as f:
    config = json.load(f)

with open(BUZZWORD_PATH) as f:
    buzzwords = set(json.load(f)["buzzwords"])

regex_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in config.get("regex_blacklist_patterns", [])]
reason_templates = config.get("reason_templates", {})

# ---- Load Model and Vectorizers ----
model = joblib.load(config["model"])
headline_vectorizer = joblib.load(config["vectorizers"]["headline_vectorizer"])
bio_vectorizer = joblib.load(config["vectorizers"]["bio_vectorizer"])

with open(config["vectorizers"]["feature_columns"]) as f:
    feature_columns = json.load(f)

# ---- Feature Extraction Functions ----
def count_buzzwords(text: str) -> int:
    return sum(1 for word in re.findall(r'\b\w+\b', text.lower()) if word in buzzwords)

def buzzword_density(text: str) -> float:
    words = re.findall(r'\b\w+\b', text.lower())
    return count_buzzwords(text) / len(words) if words else 0

def readability(text: str) -> float:
    try:
        score = flesch_reading_ease(text)
        return score if score == score else 0  # NaN safe
    except Exception:
        return 0

def extract_features(profile_data):
    headline = profile_data.headline.strip().lower()
    bio = profile_data.bio.strip().lower()

    features = {
        "headline_char_count": len(headline),
        "headline_word_count": len(headline.split()),
        "headline_readability": readability(headline),
        "headline_buzzword_matches": count_buzzwords(headline),
        "headline_buzzword_density": buzzword_density(headline),
        "bio_char_count": len(bio),
        "bio_word_count": len(bio.split()),
        "bio_readability": readability(bio),
        "bio_buzzword_matches": count_buzzwords(bio),
        "bio_buzzword_density": buzzword_density(bio),
    }

    tfidf_headline = headline_vectorizer.transform([headline]).toarray().flatten()
    tfidf_bio = bio_vectorizer.transform([bio]).toarray().flatten()

    feature_vector = np.concatenate([list(features.values()), tfidf_headline, tfidf_bio])

    if feature_vector.shape[0] != len(feature_columns):
        raise ValueError(f"Feature mismatch: Extracted {feature_vector.shape[0]}, expected {len(feature_columns)}")

    return feature_vector, features, headline, bio
