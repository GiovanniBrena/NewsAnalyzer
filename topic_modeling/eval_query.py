import os
import pprint as pp
import pickle
from gensim import corpora, models, similarities
import topic_modeling.preprocess_corpus as preprocessor
import warnings
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
warnings.simplefilter("ignore", DeprecationWarning)

N_voting = 20
TEST_SIZE = 1000

doc = "Apple has launched new iphone app smartphone market revolution"

dictionary = None
corpus = None
label_encoder = None
target_vector = None
lda = None
tfidf = None

print('Loading models')
if os.path.exists("tmp/dictionary.dict") and os.path.exists("tmp/corpus.mm"):
    dictionary = corpora.Dictionary.load('tmp/dictionary.dict')
    corpus = corpora.MmCorpus('tmp/corpus.mm')
    label_encoder = pickle.load(open('tmp/labelencoder.sav', 'rb'))
    target_vector = pickle.load(open('tmp/target_train.sav', 'rb'))
    lda = models.LdaModel.load('models/LDA_model.lda')
    index = similarities.MatrixSimilarity.load('models/sim_index_lda.index')
    tfidf = models.TfidfModel.load('tmp/model.tfidf')
else:
    print("Missing dictionary / corpus files.")

corpus_lda = lda[tfidf[corpus]]
vec_bow = dictionary.doc2bow(preprocessor.preprocess([doc], use_bigrams=False)[0])
vec_lda = lda[vec_bow]
print(vec_lda)

sims = index[vec_lda] # perform a similarity query against the corpus
sims = sorted(sims, key=lambda item: -item[1])
sims = sims[:N_voting]
pp.pprint(sims) # print sorted (document number, similarity score) 2-tuples

print('QUERY: ' + doc)
voting_pool = [0]*label_encoder.classes_.size
for s in sims:
    doc_index = s[0]
    doc_category = target_vector[doc_index]
    voting_pool[doc_category] += 1
    doc_category_label = label_encoder.inverse_transform(doc_category)
    print('doc_index: ' + str(doc_index) + ' similarity: ' + str(s[1]) + ' category: ' + str(doc_category_label))

print('MAJORITY VOTING:')
category_votes = []
for i in range(0, len(voting_pool)):
    category_votes.append((label_encoder.inverse_transform(i), voting_pool[i]))
category_votes = sorted(category_votes, key=lambda item: -item[1])
pp.pprint(category_votes)

