
# from __future__ import print_function
from pprint import pprint
from time import time
import logging
import pymongo
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from sklearn import preprocessing
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# print(__doc__)
lemmatizer = WordNetLemmatizer()


def transform_keywords(text):
    pos_dict = {'NOUN': 'n', 'NN': 'n', 'NNS': 'n',
                'NNPS': 'n', 'NNP': 'n', 'FW': 'n',
                'ADJ': 'a', 'JJ': 'a', 'JJR': 'a', 'JJS': 'a',
                # 'ADV': 'r', 'RBR': 'r', 'RBS': 'r',
                'VERB': 'v', 'VB': 'v', 'VBD': 'v', 'VBG': 'v',
                'VBN': 'v', 'VBP': 'v', 'VBZ': 'v'}

    tokens = word_tokenize(text)  # Generate list of tokens
    tokens_pos = pos_tag(tokens)

    stemmed_kw = []

    for kw in tokens_pos:
        word = kw[0]
        pos = kw[1]
        if pos not in pos_dict:
            continue
        pos = pos_dict[pos]
        stemmed_kw.append(lemmatizer.lemmatize(word, pos))

    return ' '.join(stemmed_kw)


# Display progress logs on stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

ARTICLES_PER_CATEG0RY = 5000

# #############################################################################
# Load categories from the training set
classes = ['world', 'politics', 'business', 'sports',
           'entertainment/art',
           # 'national/local',
           # 'style/food/travel',
           'science/technology/health']

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["NewsAnalyzer"]

# load the dataset
articles = []
for cat in classes:
    for aa in list(db.articles.aggregate([{"$match": {"category_aggregate": cat, "ground_truth": True}},
                                          {"$sample": {"size": ARTICLES_PER_CATEG0RY}}])):
        articles.append(aa)

print('Training SVM on ' + str(len(articles)) + ' examples for ' + str(len(classes)) + ' classes...')

# X -> features, y -> label
X = []
y = []

# create features as concatenation of keywords and tags, labels as category
for a in articles:
    if a['category_aggregate'] in classes:

        kw_concat = ' '.join(a['keywords'])
        if len(a['tags']) > 2:
            kw_concat = kw_concat + ' ' + ' '.join(a['tags'])

        kw_concat = transform_keywords(kw_concat)

        X.append(kw_concat)
        y.append(a['category_aggregate'])

# encode labels into integers
le = preprocessing.LabelEncoder()
le.fit(classes)
y_encoded = le.transform(y)

# #############################################################################
# Define a pipeline combining a text feature extractor with a simple
# classifier
pipeline = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', SVC(kernel='linear')),
])

# uncommenting more parameters will give better exploring power but will
# increase processing time in a combinatorial way
parameters = {
    'vect__max_df': (0.1, 0.2, 0.3),
    # 'vect__min_df': (1, 2),
    # 'vect__max_features': (None, 5000, 10000, 50000),
    # 'vect__ngram_range': ((1, 1), (1, 2)),  # unigrams or bigrams
    # 'tfidf__use_idf': (True, False),
    # 'tfidf__norm': ('l1', 'l2'),
    # 'clf__C': (1.0, 0.8, 0.6, 0.4),
    # 'clf__kernel': ('linear', 'poly', 'rbf'),
    # 'clf__n_iter': (10, 50, 80),
}

if __name__ == "__main__":
    # multiprocessing requires the fork to happen in a __main__ protected
    # block

    # find the best parameters for both the feature extraction and the
    # classifier
    grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1, verbose=1)

    print("Performing grid search...")
    print("pipeline:", [name for name, _ in pipeline.steps])
    print("parameters:")
    pprint(parameters)
    t0 = time()
    grid_search.fit(X, y_encoded)
    print("done in %0.3fs" % (time() - t0))
    print()

    print("Best score: %0.3f" % grid_search.best_score_)
    print("Best parameters set:")
    best_parameters = grid_search.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        print("\t%s: %r" % (param_name, best_parameters[param_name]))