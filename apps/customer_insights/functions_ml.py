import spacy
import re
import pandas as pd
import json

from langchain.llms import OpenAI
from langchain import PromptTemplate, LLMChain

from collections import Counter

spacy_nlp = spacy.load("en_core_web_md")


def remove_stops(doc):
    return [token.text for token in doc if not token.is_stop]

def lemmatize(doc):
    doc = re.sub(r'[^\w\s]', '', str(doc))
    doc = spacy_nlp(doc)
    lemma_list = [token.lemma_ for token in doc if not token.is_stop]
    lemma_list = list(set(lemma_list))

    return ' '.join(lemma_list)

def find_types_of_words(text, word_type_list, nlp=spacy_nlp):
    doc = nlp(text)
    words = [x.text.lower() for x in doc if x.pos_ in word_type_list]
    words = list(set(words))
    words.sort()
    ignore_words = ['have']
    words = [x for x in words if x not in ignore_words]
    
    return words

def most_common_words(text_list, word_type_list):
    all_review_adjectives = []
    for review in text_list:
        adjs = find_types_of_words(review, word_type_list)
        all_review_adjectives.extend(adjs)
    most_common_words = Counter(all_review_adjectives).most_common(500)
    return most_common_words

def phrase_around_top_words(review, regex):
    try:
        return re.findall(regex, review)
    except:
        return ['']

def sampled_phrases(top_words, lemmatized_reviews):
    review_top_nouns_adjs_verbs_top_twenty = top_words[:20]
    review_top_nouns_adjs_verbs_vals = [x[0] for x in review_top_nouns_adjs_verbs_top_twenty]
    review_top_nouns_adjs_verbs_regex = '(?:' + '|'.join(review_top_nouns_adjs_verbs_vals) + ')'
    phrase_around_top_nouns_adjs_verbs_regex = '[ 0-9a-zA-Z]{1,50} ' + review_top_nouns_adjs_verbs_regex + '[ 0-9a-zA-Z]{1,50}[ \\.]{1}'

    _phrases_around_keywords = []
    for x in lemmatized_reviews[:1500]:
        _phrases_around_keywords.extend(phrase_around_top_words(x, phrase_around_top_nouns_adjs_verbs_regex))

    phrases_around_keywords = []
    for x in _phrases_around_keywords[:1500]:
        temp = {
            'keyword': re.findall(review_top_nouns_adjs_verbs_regex, x)[0],
            'phrase': x
        }
        phrases_around_keywords.append(temp)

    phrases_around_keywords_df = pd.DataFrame(phrases_around_keywords)

    _sampled_phrases = phrases_around_keywords_df.groupby('keyword').head(8)['phrase'].to_list()
    sampled_phrases = []
    counter = 0
    for x in _sampled_phrases:
        counter += 1
        sampled_phrases.append(str(counter) + ') ' + x)

    return sampled_phrases

def create_topics(sampled_phrases):
    create_topics_template = """
        Question: Please create 10 features that describe mostly frequently mentioned qualities of the product from the reviews below. Please output the categories as a numbered list separated by newline characters Reviews: {reviews}
        
        Answer: Here are 10 features:
    """
    openai_llm = OpenAI(verbose=True, temperature=.1, model_name="text-davinci-003")
    simple_prompt = PromptTemplate(input_variables=["reviews"], template=create_topics_template)
    chain = LLMChain(llm=openai_llm, prompt=simple_prompt)
    _topics = chain.run(' '.join(sampled_phrases))
    topics = _topics.split('\n')
    topics = [re.sub('[0-9]{1,2}\\. ', '', x) for x in topics]

    return topics

def subtopic_labler(review, topic):
    review = str(review)
    topic = str(topic)
    
    subtopic_regex = ' [ 0-9a-zA-Z]{1,20} ' + topic.lower() + '[^ \..]{0,20}'
    try:
        return re.findall(subtopic_regex, review.lower())[0]
    except:
        return ''
    
def categorize_common_words(common_words):
    categorize_common_words_template = """
        I am going to give you a list of words. Please tell me which refer to people ("who"), which refer to dates or times ("when"), which refer to places ("where"), and which describe actions or activities ("activities"). Please return your response as a JSON object with who, when, where, and what as keys, and the results as lists for values. If a word does not fit into one of those categories, you can exclude it from the response. Please exclude adjectives from your response. Words: {words}
    """

    openai_llm = OpenAI(verbose=True, temperature=.1, model_name="text-davinci-003", max_tokens=2000)
    simple_prompt = PromptTemplate(input_variables=["words"], template=categorize_common_words_template)
    chain = LLMChain(llm=openai_llm, prompt=simple_prompt)
    word_list = list(set([x[0] for x in common_words[:150]]))
    word_list = ', '.join(word_list)

    categorized_words = chain.run(word_list)
    categorized_words = json.loads(categorized_words)

    return categorized_words