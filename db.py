import logging

from peewee import *

import words
from utils import inf_engine

db = SqliteDatabase('words.db')


class EngWords(Model):
    id = IntegerField(index=True, null=True, primary_key=True)
    word = CharField(unique=False, index=True)
    frequency = BigIntegerField(index=True)

    class Meta:
        database = db  # This model uses the "words.db" database.

    def __unicode__(self):
        return '%s -> %s' % (self.word, self.frequency)


def init_db(chunk=50000, reset=False, include_plural=True):
    logging.info("start insert...")

    if reset:
        db.drop_tables([EngWords])

    db.create_tables([EngWords, ], safe=True)

    all_words = []
    words_freq = words.load_words_frequencies()

    for word in words.load_words():
        similar_words = [word]
        freq = words_freq.get(word, 0)

        if include_plural:
            similar_words.append(inf_engine.plural(word))

        for w in list(set(similar_words)):
            all_words.append({'word': w, 'frequency': freq})

    if not reset and len(all_words) == EngWords.select().count():
        logging.info("Already up to date")
        return

    with db.atomic():
        for idx in range(0, len(all_words), chunk):
            words_chunk = all_words[idx:idx + chunk]
            EngWords.insert_many(words_chunk).execute()

    logging.info("Done.")
