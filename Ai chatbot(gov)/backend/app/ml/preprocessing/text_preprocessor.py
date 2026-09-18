"""
Text preprocessing pipeline for ML models.
Handles cleaning, normalization, stopword removal, and stemming/lemmatization.
"""
import re
import string
from typing import List, Optional
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize


def download_nltk_resources():
    """Download required NLTK data if not already present."""
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
    ]
    for path, name in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, quiet=True)


# Download on module load
download_nltk_resources()

_stop_words = set(stopwords.words("english"))
# Keep negation words — important for complaint text ("not working", "no supply")
_KEEP_WORDS = {"no", "not", "never", "without", "none", "lack", "lacking"}
_stop_words -= _KEEP_WORDS

_stemmer = PorterStemmer()
_lemmatizer = WordNetLemmatizer()


def clean_text(text: str) -> str:
    """
    Basic text cleaning:
    - Lowercase
    - Remove URLs
    - Remove email addresses
    - Remove special characters (keep spaces)
    - Normalize whitespace
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\d+", " NUM ", text)  # Replace numbers with token
    text = re.sub(r"[^\w\s]", " ", text)  # Remove punctuation
    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_stopwords(tokens: List[str]) -> List[str]:
    """Remove stopwords while keeping negation words."""
    return [t for t in tokens if t not in _stop_words and len(t) > 1]


def lemmatize(tokens: List[str]) -> List[str]:
    """Lemmatize a list of tokens."""
    return [_lemmatizer.lemmatize(t) for t in tokens]


def preprocess(text: str, use_lemmatization: bool = True) -> str:
    """
    Full preprocessing pipeline:
    1. Clean text
    2. Tokenize
    3. Remove stopwords
    4. Lemmatize (or stem)

    Returns preprocessed string for TF-IDF vectorization.
    """
    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    if use_lemmatization:
        tokens = lemmatize(tokens)
    return " ".join(tokens)


def preprocess_batch(texts: List[str], use_lemmatization: bool = True) -> List[str]:
    """Preprocess a batch of texts."""
    return [preprocess(t, use_lemmatization) for t in texts]


# ─── Severity / Duration extraction helpers ───────────────────────────────────

DURATION_PATTERNS = [
    (r"(\d+)\s*(day|days)", "{} day(s)"),
    (r"(\d+)\s*(week|weeks)", "{} week(s)"),
    (r"(\d+)\s*(hour|hours|hr|hrs)", "{} hour(s)"),
    (r"(\d+)\s*(month|months)", "{} month(s)"),
    (r"since\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", "since {}"),
    (r"since\s+(\w+\s+\d+)", "since {}"),
    (r"(yesterday|last\s+night|last\s+week)", "{}"),
]

SEVERITY_KEYWORDS = {
    "Critical": ["fire", "flood", "collapse", "accident", "emergency", "danger", "death",
                 "life threatening", "hazardous", "crisis"],
    "High": ["many people", "entire area", "whole colony", "no water", "no electricity",
             "no supply", "not working", "broken", "damaged", "overflowing", "severe",
             "days", "urgent", "serious", "elderly", "children", "hospital"],
    "Medium": ["inconvenient", "problem", "issue", "affecting", "disturbing", "weeks"],
    "Low": ["minor", "small", "slight", "occasional", "sometimes"],
}


def extract_duration(text: str) -> Optional[str]:
    """Extract duration mention from complaint text using regex."""
    text_lower = text.lower()
    for pattern, template in DURATION_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                return template.format(groups[0])
            elif len(groups) == 1:
                return template.format(groups[0])
    return None


def infer_severity(text: str, explicit_severity: Optional[str] = None) -> str:
    """Infer severity from text content if not explicitly provided."""
    if explicit_severity and explicit_severity in SEVERITY_KEYWORDS:
        return explicit_severity

    text_lower = text.lower()
    for level in ["Critical", "High", "Medium", "Low"]:
        for kw in SEVERITY_KEYWORDS[level]:
            if kw in text_lower:
                return level
    return "Medium"
