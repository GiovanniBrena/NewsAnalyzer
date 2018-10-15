import topic_modeling.sample_dataset as data_sampler
import topic_modeling.gen_dict_corpus as vectorizer
import topic_modeling.transform_corpus as transformer
import logging
import datetime
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

timeStart = datetime.datetime.now()
ART_PER_CATEGORY = 4000
categories = ['world', 'politics', 'business', 'sports',
               'entertainment/art', 'science/technology/health',
               'national/local', 'style/food/travel']

data_sampler.create(classes=categories, art_per_category=ART_PER_CATEGORY, save_path='tmp/all_32k/')
vectorizer.create(path='tmp/all_32k/')
# transformer.transform(n_topics=100, similarity_size=100, path='tmp/politics/')


timeEnd = datetime.datetime.now()
delta = timeEnd - timeStart
print('Executed in ' + str(int(delta.total_seconds())) + 's')
