# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# Process fmri pubmed abstracts by year

# %%

# code generated by ChatGPT

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pickle
from collections import namedtuple
import os
from nltk.stem import WordNetLemmatizer

nltk.download('wordnet', quiet=True)
import gensim

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')


# %%


def clean_text(sentences):
    # Instantiate the wordnet lemmatizer
    lem = WordNetLemmatizer()

    # Define the stop words
    stop_words = list(set(stopwords.words('english')))
    with open('additional_stopwords_topicmodel.txt', 'r') as f:
        additional_stopwords = [i.strip() for i in f.readlines()]
    stop_words = stop_words + additional_stopwords

    cleaned_sentences = []
    for sentence in sentences:
        # Tokenize the sentence
        words = [i.lower() for i in word_tokenize(sentence)]

        # Remove stop words and stem the words
        cleaned_sentence = [lem.lemmatize(w) for w in words if w.isalpha()]
        cleaned_sentence = [
            w for w in cleaned_sentence if w not in stop_words and len(w) > 2
        ]
        cleaned_sentences.append(' '.join(cleaned_sentence))

    return cleaned_sentences


# %%

# Read the abstracts

PMID = namedtuple('PMID', ['pmid', 'year', 'abstract'])

datadir = 'data'
recordfile = os.path.join(datadir, 'pmid_records.pkl')
with open(recordfile, 'rb') as f:
    pmid_records = pickle.load(f)

years = list(set([r.year for r in pmid_records]))


# %%

#  Get abstracts for each year
bigram = gensim.models.Phrases(
    min_count=40
)   # min_count determined by eyeball

for year in years:
    print('getting abstracts for', year)
    abstracts = []
    for r in pmid_records:
        if r.abstract is None:
            continue
        if r.year == year:
            abstracts.append(clean_text([r.abstract]))
    bigram.add_vocab([a[0].split(' ') for a in abstracts])

    with open(
        os.path.join(datadir, f'cleaned_abstracts_{year}.pkl'), 'wb'
    ) as f:
        pickle.dump(abstracts, f)

frozen_model = bigram.freeze()
frozen_model.save(os.path.join(datadir, 'bigram_model.pkl'))


for year in years:
    print('getting bigrammed abstracts for', year)
    bg_abstracts = []
    with open(
        os.path.join(datadir, f'cleaned_abstracts_{year}.pkl'), 'rb'
    ) as f:
        abstracts = pickle.load(f)
    split_abstracts = [a[0].split(' ') for a in abstracts]
    # demarcate bigrams with dash
    bg_abstracts = [i.replace('_', '-') for i in frozen_model[split_abstracts]]

    with open(
        os.path.join(datadir, f'bigrammed_cleaned_abstracts_{year}.pkl'), 'wb'
    ) as f:
        pickle.dump(bg_abstracts, f)
