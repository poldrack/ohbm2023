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
# Run topic modeling for each year

# %%

# code generated by ChatGPT


import pickle
import os
from bertopic import BERTopic
import openai
from bertopic.representation import OpenAI
from sentence_transformers import SentenceTransformer


# %%
# Load the abstracts
datadir = 'data'
ldadir = os.path.join(datadir, 'lda_models')
if not os.path.exists(ldadir):
    os.makedirs(ldadir)

# %%

sentences = []
years = []


for year in range(1990, 2023):
    print('loading data for year %s' % year)
    abstract_file = os.path.join(
        datadir, f'bigrammed_cleaned_abstracts_{year}.pkl'
    )
    if not os.path.exists(abstract_file):
        print('File %s does not exist' % abstract_file)
        continue
    with open(abstract_file, 'rb') as f:
        new_sentences = [' '.join(i) for i in pickle.load(f)]
        sentences = sentences + new_sentences
        years = years + [year] * len(new_sentences)

assert len(sentences) > 0
assert len(sentences) == len(years)

# %%

use_gpt = True
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

model_name = 'bertopic' if not use_gpt else 'bertopic_gpt4'
representation_model = None

modeldir = 'models'
if not os.path.exists(modeldir):
    os.makedirs(modeldir)

if use_gpt:
    with open('openai_api_key.txt', 'r') as f:
        openai.api_key = f.read().strip()

    representation_model = OpenAI(
        model='gpt-4', chat=True, exponential_backoff=True
    )


topic_model = BERTopic(
    representation_model=representation_model,
    embedding_model=embedding_model,
    verbose=True,
)

topics, probs = topic_model.fit_transform(sentences)

# need to exclude embedding model as it causes GPU/CPU conflict
topic_model.save(
    os.path.join(modeldir, model_name),
    serialization='pytorch',
    save_ctfidf=True,
    save_embedding_model=False,
)
