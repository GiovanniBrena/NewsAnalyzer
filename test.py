import modules.enrich_news_tweet as enricher
import pymongo
import threading
from threading import Thread
import time
from random import randint


mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["NewsAnalyzer"]

# Definizione del lock
threadLock = threading.Lock()


class IlMioThread(Thread):
    def __init__(self, nome, durata):
        Thread.__init__(self)
        self.nome = nome
        self.durata = durata

    def run(self):
        print("Thread '" + self.name + "' avviato")
        # Acquisizione del lock
        threadLock.acquire()
        time.sleep(self.durata)
        print("Thread '" + self.name + "' terminato")
        # Rilascio del lock
        threadLock.release()


# Creazione dei thread
thread1 = IlMioThread("Thread#1", randint(1, 100))
thread2 = IlMioThread("Thread#2", randint(1, 100))
thread3 = IlMioThread("Thread#3", randint(1, 100))

# Avvio dei thread
thread1.start()
thread2.start()
thread3.start()

# Join
thread1.join()
thread2.join()
thread3.join()

# Fine dello script
print("Fine")
