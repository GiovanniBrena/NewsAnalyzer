# importing necessary libraries
import pymongo
import sys
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import pickle
import datetime
import warnings
import topic_modeling.preprocess_corpus as preprocessor
import gensim
from gensim.models import CoherenceModel, LdaModel, LdaMulticore, LsiModel, HdpModel
import gensim.corpora as corpora
warnings.simplefilter("ignore", DeprecationWarning)
sys.path.append("/topic_modeling")

use_existing_models = True


def create_model():

    TEST_SIZE = 0.05
    data_path = 'models/dataset_any_2k'
    classes = ['world', 'politics', 'business', 'sports',
               'entertainment/art',
               'science/technology/health',
               'national/local', 'style/food/travel'
               ]

    # load dataset file
    data = pickle.load(open(data_path, 'rb'))
    print(data[0])

    X = [d[0] for d in data]
    y = [d[1] for d in data]

    print('')
    print('')
    print('Training examples: ' + str(len(X)))
    print('Number of classes: ' + str(len(classes)))
    print('Test set size: ' + str(TEST_SIZE * 100) + '%')

    if not use_existing_models:
        # preprocess documents
        X_pp, bigram_model = preprocessor.preprocess(sentences=X)
        bigram_model.save('models/bigram_any_2k')
        pickle.dump(X_pp, open('models/data_pp_any_2k', 'wb'))
        print(X_pp[0])

        # Create Dictionary
        dictionary = corpora.Dictionary(X_pp)
        dictionary.filter_extremes(no_below=5, no_above=0.5)
        dictionary.save('models/dictionary_any_2k')

    else:
        dictionary = corpora.Dictionary.load('models/dictionary_any_2k')
        bigram_model = gensim.models.phrases.Phraser.load('models/bigram_any_2k')
        X_pp = pickle.load(open('models/data_pp_any_2k', 'rb'))

    # Term Document Frequency
    corpus = [dictionary.doc2bow(text) for text in X_pp]

    evaluate_graph(dict=dictionary, corp=corpus, texts=X_pp, min_topics=50, limit=300, step=50, coh_measure='u_mass')

    # train LDA model
    ldamodel = LdaModel(corpus=corpus, num_topics=100, id2word=dictionary)
    num_topics = len(ldamodel.show_topics(num_topics=-1))
    print(ldamodel.top_topics(corpus=corpus, dictionary=dictionary))

    X_vector = []

    for w in X_pp:
        # initialize topic vector
        topic_vector = [0] * num_topics
        # convert article text to BoW
        bow = dictionary.doc2bow(w)
        topic_distr = ldamodel.get_document_topics(bow)
        for dis in topic_distr:
            topic_vector[dis[0]] = dis[1]
        X_vector.append(topic_vector)

    print(X_vector[0])

    # encode labels into integers
    le = preprocessing.LabelEncoder()
    le.fit(classes)
    y_encoded = le.transform(y)

    # dividing X, y into train and test data
    X_train, X_test, y_train, y_test = train_test_split(X_vector, y_encoded, test_size=TEST_SIZE, random_state=10)

    # training Naive Bayes model
    clf_NB = MultinomialNB(class_prior=None, fit_prior=True)
    clf_NB.fit(X_train, y_train)
    train_acc_nb = clf_NB.score(X_train, y_train)
    test_acc_nb = clf_NB.score(X_test, y_test)
    print('')
    print('NAIVE BAYES ---------------------------------------------')
    print('Train score: ' + str(train_acc_nb))
    print('Test score: ' + str(test_acc_nb))

    # training SGD classifiers
    from sklearn.linear_model import SGDClassifier
    clf_SVM = SGDClassifier(n_jobs=-1, max_iter=5000, tol=0.0001, learning_rate='optimal', loss='hinge')
    clf_SVM.fit(X_train, y_train)
    train_acc_svm = clf_SVM.score(X_train, y_train)
    test_acc_svm = clf_SVM.score(X_test, y_test)
    print('')
    print('LINEAR SVM ----------------------------------------------')
    print('Train score: ' + str(train_acc_svm))
    print('Test score: ' + str(test_acc_svm))

    clf_log_reg = SGDClassifier(n_jobs=-1, max_iter=5000, tol=0.0001, learning_rate='optimal', loss='modified_huber')
    clf_log_reg.fit(X_train, y_train)
    train_acc_log = clf_log_reg.score(X_train, y_train)
    test_acc_log = clf_log_reg.score(X_test, y_test)
    cm = confusion_matrix(y_test, clf_log_reg.predict(X_test))
    print('')
    print('LOGISTIC REGRESSION -------------------------------------')
    print('Train score: ' + str(train_acc_log))
    print('Test score: ' + str(test_acc_log))

    print('')
    print('--------------------------------------')
    print('')
    print('COUNFUSION MATRIX FOR LOGISTIC REGRESSION:')
    print('')
    print(cm)
    print('')
    print('')


'''
    from sklearn.ensemble import RandomForestClassifier
    clf_random_for = RandomForestClassifier(n_jobs=-1, n_estimators=20, max_depth=None, random_state=0)
    clf_random_for.fit(X_train_countvect, y_train)
    train_acc_rf = clf_random_for.score(X_train_countvect, y_train)
    test_acc_rf = clf_random_for.score(X_test_countvect, y_test)
    print('')
    print('RANDOM FOREST -------------------------------------------')
    print('Train score: ' + str(train_acc_rf))
    print('Test score: ' + str(test_acc_rf))

'''


# save model, vectors and label encoding to disk
# save_model(clf_log_reg, le)


def evaluate_graph(dict, corp, texts, min_topics, limit, step, coh_measure='c_v'):
    """
    Function to display num_topics - LDA graph using c_v coherence

    Parameters:
    ----------
    dictionary : Gensim dictionary
    corpus : Gensim corpus
    limit : topic limit

    Returns:
    -------
    lm_list : List of LDA topic models
    c_v : Coherence values corresponding to the LDA model with respective number of topics
    """
    c_v = []
    lm_list = []
    for num_topics in range(min_topics, limit, step):
        lm = LdaModel(corpus=corp, num_topics=num_topics, id2word=dict)
        lm_list.append(lm)
        cm = CoherenceModel(model=lm, texts=texts, dictionary=dict, coherence=coh_measure)
        coh = cm.get_coherence()
        c_v.append(coh)
        print('Topic count: ' + str(num_topics) + ' coherence: ' + str(coh))

    # Show graph
    x = range(min_topics, limit, step)
    plt.plot(x, c_v)
    plt.xlabel("num_topics")
    plt.ylabel("Coherence score")
    plt.legend(("c_v"), loc='best')
    plt.show()

    return lm_list, c_v



def main():
    create_model()


if __name__ == "__main__":
    timeStart = datetime.datetime.now()
    main()
    timeEnd = datetime.datetime.now()
    delta = timeEnd - timeStart
    print('Executed in ' + str(int(delta.total_seconds())) + 's')