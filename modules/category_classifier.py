# importing necessary libraries
import pymongo
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import pickle
import datetime
import warnings
warnings.simplefilter("ignore", DeprecationWarning)


def save_vector(cv):
    print("....... saving vector as pickle file ......")
    filename = '/models/classifier-tf-vector.sav'
    pickle.dump(cv, open(filename, 'wb'))
    print("Done.")


def save_model(classifier, countvect, tfidfvect, labelencoder):
    print("....... saving model as pickle file ......")
    pickle.dump(classifier, open('../models/classifier.sav', 'wb'))
    pickle.dump(countvect, open('../models/countvect.sav', 'wb'))
    pickle.dump(tfidfvect, open('../models/tfidfvect.sav', 'wb'))
    pickle.dump(labelencoder, open('../models/labelencoder.sav', 'wb'))
    print("Done.")


def predict(keywords, N, models=None):
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

    X = [' '.join(keywords[:N])]
    x_count = countvect.transform(X)
    feature_vect = tfidfvect.transform(x_count)
    prediction = model.predict(feature_vect)
    return labelencoder.inverse_transform(prediction)




def create_model():
    N_keywords = 10
    classes = ['world', 'politics', 'business', 'sports', 'entertainment', 'health', 'local', 'technology', 'style']

    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = mongo_client["NewsAnalyzer"]

    # loading the dataset
    articles = db.articles.find()

    # X -> features, y -> label
    X = []
    y= []
    for a in articles:
        if a['category'] in classes:
            kw_concat = ' '.join(a['keywords'])
            if len(a['tags']) > 2:
                kw_concat = kw_concat + ' ' + ' '.join(a['tags'])
            X.append(kw_concat)
            y.append(a['category'])

    le = preprocessing.LabelEncoder()
    le.fit(classes)
    y_encoded = le.transform(y)
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(X)
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)


    # dividing X, y into train and test data
    X_train, X_test, y_train, y_test = train_test_split(X_train_tfidf, y_encoded, random_state=0)

    # training a linear SVM classifier
    from sklearn.svm import SVC

    svm_model_linear = SVC(kernel='linear', C=1).fit(X_train, y_train)
    svm_predictions = svm_model_linear.predict(X_test)

    # model accuracy for X_test
    accuracy = svm_model_linear.score(X_test, y_test)

    # creating a confusion matrix
    cm = confusion_matrix(y_test, svm_predictions)

    print('done')
    print('accuracy: ' + str(accuracy))
    save_model(svm_model_linear, count_vect, tfidf_transformer, le)
    art = db.articles.find_one({'category': 'technology'})
    print(predict(art['keywords'], 10))


def main():
    create_model()


if __name__ == "__main__":
    timeStart = datetime.datetime.now()
    main()
    timeEnd = datetime.datetime.now()
    delta = timeEnd - timeStart
    print('Executed in ' + str(int(delta.total_seconds())) + 's')
