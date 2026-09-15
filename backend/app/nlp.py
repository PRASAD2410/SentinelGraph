"""spaCy loader with a no-download fallback suitable for local Windows setup."""
import spacy
try:
    NLP=spacy.load('en_core_web_sm')
except OSError:
    NLP=spacy.blank('en')

