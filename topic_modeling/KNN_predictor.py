import os
import pprint as pp
import numpy as np
import pickle
import pymongo
from gensim import corpora, models, similarities
import topic_modeling.preprocess_corpus as preprocessor
import warnings
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
warnings.simplefilter("ignore", DeprecationWarning)

N_voting = 20
TEST_SIZE = 100

dictionary = None
corpus = None
label_encoder = None
target_train = None
target_test = None
lsi = None
index_lsi = None
lda = None
index_lda = None

print('Loading models')
if os.path.exists("tmp/dictionary.dict") and os.path.exists("tmp/corpus.mm"):
    dictionary = corpora.Dictionary.load('tmp/dictionary.dict')
    corpus = corpora.MmCorpus('tmp/corpus.mm')
    label_encoder = pickle.load(open('tmp/labelencoder.sav', 'rb'))
    target_train = pickle.load(open('tmp/target_train.sav', 'rb'))
    target_test = pickle.load(open('tmp/target_test.sav', 'rb'))
    index_lsi = similarities.MatrixSimilarity.load('tmp/sim_index_lsi.index')
    lsi = models.LsiModel.load('tmp/model.lsi')
    index_lda = similarities.MatrixSimilarity.load('tmp/sim_index_lda.index')
    lda = models.LdaModel.load('tmp/model.lda')
else:
    print("Missing dictionary / corpus files.")

texts = []

with open('tmp/raw_data_test.txt', 'r') as filehandle:
    filecontents = filehandle.readlines()
    for line in filecontents:
        # remove linebreak which is the last character of the string
        current_place = line[:-1]
        # add item to the list
        texts.append(current_place)

vec_bow = [dictionary.doc2bow(text) for text in preprocessor.preprocess(texts, use_bigrams=False)]
total_count = len(vec_bow)


def evaluate_model(test_bow, model, sim_index):
    positive_count = 0
    for i in range(0, len(test_bow)):
        topic_space_vec = model[test_bow[i]]

        sims = sim_index[topic_space_vec]  # perform a similarity query against the corpus
        sims = sorted(sims, key=lambda item: -item[1])
        sims = sims[:N_voting]

        voting_pool = [0] * label_encoder.classes_.size
        for s in sims:
            doc_index = s[0]
            doc_category = target_train[doc_index]
            voting_pool[doc_category] += 1

        category_votes = []
        for j in range(0, len(voting_pool)):
            category_votes.append((j, voting_pool[j]))

        category_votes = sorted(category_votes, key=lambda item: -item[1])
        # pp.pprint(label_encoder.inverse_transform(category_votes[0][0]))
        if category_votes[0][0] == target_test[i]:
            positive_count += 1
    return positive_count


pos_count_lsi = evaluate_model(test_bow=vec_bow, model=lsi, sim_index=index_lsi)
pos_count_lda = evaluate_model(test_bow=vec_bow, model=lda, sim_index=index_lda)

print('LSI based KNN Accuracy: ' + str(pos_count_lsi) + '/' + str(total_count))
print(str(round(pos_count_lsi / total_count, 3)))
print('LDA based KNN Accuracy: ' + str(pos_count_lda) + '/' + str(total_count))
print(str(round(pos_count_lda / total_count, 3)))

