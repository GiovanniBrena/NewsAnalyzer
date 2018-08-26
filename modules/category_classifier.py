# importing necessary libraries
import pymongo
from math import exp
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import pickle
import datetime
import warnings
warnings.simplefilter("ignore", DeprecationWarning)

# PARAMETERS
# minimum probability to accept prediction
classifier_threshold = 0.4


def save_model(classifier, countvect, tfidfvect, labelencoder):
    print("...... saving model as pickle file ......")
    pickle.dump(classifier, open('../models/classifier.sav', 'wb'))
    pickle.dump(countvect, open('../models/countvect.sav', 'wb'))
    pickle.dump(tfidfvect, open('../models/tfidfvect.sav', 'wb'))
    pickle.dump(labelencoder, open('../models/labelencoder.sav', 'wb'))
    print("Done.")


# predicts category given a LIST of keywords
# output:
#   {
#       'class': category_prediction,
#       'probability': confidence value (0,1)
#   }
#   if probability < classifier_threshold returns None

def predict(keywords, models=None):
    if not models:
        # load the model from disk
        model = pickle.load(open('../models/classifier.sav', 'rb'))
        countvect = pickle.load(open('../models/countvect.sav', 'rb'))
        tfidfvect = pickle.load(open('../models/tfidfvect.sav', 'rb'))
        labelencoder = pickle.load(open('../models/labelencoder.sav', 'rb'))
    else:
        try:
            model = models['model']
            countvect = models['countvect']
            tfidfvect = models['tfidfvect']
            labelencoder = models['labelencoder']
        except KeyError:
            print('Bad model provided')
            return None

    X = [' '.join(keywords)]
    x_count = countvect.transform(X)
    feature_vect = tfidfvect.transform(x_count)
    prediction = model.predict_log_proba(feature_vect)
    maxprob = max(prediction[0])
    if exp(maxprob) > classifier_threshold:
        for i in range(0, len(prediction[0])):
            if prediction[0][i] == maxprob:
                return {'class': labelencoder.inverse_transform(i), 'probability': exp(maxprob)}
    return None


'''
Aggregated categories:
politics
sports
business
world
entertainment/art
national/local
style/food/travel
science/technology/health
'''


def get_aggregated_category(category):
    if category in ['national', 'local']:
        return 'national/local'
    elif category in ['entertainment', 'art']:
        return 'entertainment/art'
    elif category in ['science', 'technology', 'health']:
        return 'science/technology/health'
    elif category in ['style', 'food', 'travel']:
        return 'style/food/travel'
    else:
        return category


def create_model():
    classes = ['world', 'politics', 'business', 'sports', 'entertainment/art',
               'national/local', 'style/food/travel', 'science/technology/health']

    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = mongo_client["NewsAnalyzer"]

    # load the dataset
    articles = db.articles.find({'ground_truth': True})
    print('Training SVM on ' + str(articles.count()) + ' examples for ' + str(len(classes)) + ' classes...')

    # X -> features, y -> label
    X = []
    y = []

    # create features as concatenation of keywords and tags, labels as category
    for a in articles:
        if a['category_aggregate'] in classes:
            kw_concat = ' '.join(a['keywords'])
            if len(a['tags']) > 2:
                kw_concat = kw_concat + ' ' + ' '.join(a['tags'])
            X.append(kw_concat)
            y.append(a['category_aggregate'])

    # encode labels into integers
    le = preprocessing.LabelEncoder()
    le.fit(classes)
    y_encoded = le.transform(y)

    # vectorize features
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(X)
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

    # dividing X, y into train and test data
    X_train, X_test, y_train, y_test = train_test_split(X_train_tfidf, y_encoded, random_state=0)

    # training a linear SVM classifier
    from sklearn.svm import SVC
    svm_model_linear = SVC(kernel='linear', C=1, probability=True)
    svm_model_linear.fit(X_train, y_train)
    svm_predictions = svm_model_linear.predict(X_test)

    # model accuracy for X_test
    accuracy = svm_model_linear.score(X_test, y_test)

    # creating a confusion matrix
    cm = confusion_matrix(y_test, svm_predictions)

    print('done')
    print('accuracy: ' + str(accuracy))

    # save model, vectors and label encoding to disk
    save_model(svm_model_linear, count_vect, tfidf_transformer, le)


def main():
    create_model()


if __name__ == "__main__":
    timeStart = datetime.datetime.now()
    main()
    timeEnd = datetime.datetime.now()
    delta = timeEnd - timeStart
    print('Executed in ' + str(int(delta.total_seconds())) + 's')
