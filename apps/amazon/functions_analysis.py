import json

from collections import Counter
import spacy

nlp = spacy.load("en_core_web_md")

# 'NOUN', 'ADJ'
def find_types_of_words(text, word_type, nlp=nlp):
    doc = nlp(text)
    words = [x.text.lower() for x in doc if x.pos_ == word_type]
    words = list(set(words))
    words.sort()
    
    return words

def most_common_words(text_list, word_type):
    all_review_adjectives = []
    for review in text_list:
        adjs = find_types_of_words(review, word_type)
        all_review_adjectives.extend(adjs)

    most_common_words = Counter(all_review_adjectives).most_common(15)
    return most_common_words