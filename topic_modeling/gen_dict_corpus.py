import topic_modeling.preprocess_corpus as preprocessor
import gensim.corpora as corpora
import os
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def create():
    if not os.path.exists("tmp/raw_data_train.txt"):
        print('Missing raw data.')
        return

    texts = []
    with open('tmp/raw_data_train.txt', 'r') as filehandle:
        filecontents = filehandle.readlines()
        for line in filecontents:
            # remove linebreak which is the last character of the string
            current_place = line[:-1]
            # add item to the list
            texts.append(current_place)

    print('Preprocessing texts...')
    texts = preprocessor.preprocess(texts, use_bigrams=False)

    print('Creating dictionary...')
    dictionary = corpora.Dictionary(texts)
    dictionary.save('tmp/dictionary.dict')  # store the dictionary, for future reference
    print(dictionary)
    print('Serializing corpus...')
    corpora.MmCorpus.serialize('tmp/corpus.mm', [dictionary.doc2bow(t) for t in texts])


'''
    class MyCorpus(object):
        def __iter__(self):
            for line in open('tmp/raw_data_train.txt'):
                preprocessor.preprocess([line[0]], use_bigrams=False)
                yield dictionary.doc2bow(line.lower().split())

    print('Creating corpus...')
    corpus = MyCorpus()  # doesn't load the corpus into memory!

    print('Serializing corpus...')
    corpora.MmCorpus.serialize('tmp/corpus.mm', corpus)
'''
