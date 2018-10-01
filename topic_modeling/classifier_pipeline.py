import topic_modeling.sample_dataset as data_sampler
import topic_modeling.gen_dict_corpus as vectorizer
import topic_modeling.transform_corpus as transformer
import logging
import datetime
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

timeStart = datetime.datetime.now()
ART_PER_CATEGORY = 8000

data_sampler.create(ART_PER_CATEGORY)
vectorizer.create()
transformer.transform(n_topics=300, similarity_size=50)


timeEnd = datetime.datetime.now()
delta = timeEnd - timeStart
print('Executed in ' + str(int(delta.total_seconds())) + 's')
