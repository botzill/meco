# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools
import logging
import os
import time
from collections import namedtuple

import nltk
from flask import Flask, render_template, request
from flask_cache import Cache
from nltk.corpus import wordnet as wn

import config
import db
from db import EngWords
from utils import inf_engine

cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': config.CACHE_TIMEOUT})
app = Flask(__name__)
cache.init_app(app)

NOUNS = set()
try:
    if not config.DISABLE_DICT_DOWNLOAD:
        nltk.download('wordnet')

    for x in wn.all_synsets('n'):
        noun_word = x.name().split('.', 1)[0]
        NOUNS.add(noun_word)
        NOUNS.add(inf_engine.plural(noun_word))
except Exception as e:
    logging.error(e)


def convert_number_to_word(number, filter_nouns=False):
    logging.info("Convert number '%s' to words..." % number)
    if filter_nouns:
        nouns = NOUNS
    else:
        nouns = {}

    ll = []
    for n in str(number):
        sounds = config.ALPHANUM_CODE[n]['sounds']
        ll.append([(n, s) for s in sounds])

    sound_codes = itertools.product(*ll)

    regexp_sound_codes = []

    # Create all the possible sound codes reqexp
    for sound_code_list in sound_codes:
        sounds = []
        for num, sound in sound_code_list:
            sound_regexp = '(%s)+' % sound
            # Make sure we handle the soft g/c which should be followed by e,i,y but not as a general rule
            # this is just a simple example
            # https://www.thoughtco.com/pronunciation-hard-soft-c-and-g-1212096
            if num in ('6',) and sound in ('g',):
                sound_regexp = '%s%s' % (sound_regexp, config.SOFT_SOUND_REGEXP)
            elif num in ('0',) and sound in ('c',):
                sound_regexp = '%s%s' % (sound_regexp, config.SOFT_SOUND_REGEXP)

            sounds.append(sound_regexp)

        sound_code = '^{1}{0}{1}$'.format(config.REGEXP_SEP.join(sounds), config.REGEXP_SEP)
        regexp_sound_codes.append(sound_code)

    words_sel = EngWords.select().where(EngWords.word.regexp('|'.join(regexp_sound_codes))).order_by(
        EngWords.frequency.desc()).distinct()

    if filter_nouns:
        words_sel = words_sel.select().where(EngWords.word.in_(nouns)).distinct()

    # TODO: geo here we should get distinct items from db already!
    all_words = list(set([w.word for w in words_sel]))
    logging.info("Done.")

    return all_words


def init():
    if config.INIT_DB:
        db.init_db()


def global_vars():
    return {
        'app_id': os.environ.get('CURRENT_VERSION_ID', 'v10101')
    }


def get_request_params():
    Params = namedtuple('Params', 'number, filter_nouns')

    return Params(
        request.args.get('number', '0'),
        request.args.get('filter_nouns', 'off'))


def make_cache_key(*args, **kwargs):
    params = get_request_params()
    return '{number}_{filter_nouns}'.format(**params._asdict())


@app.route('/')
@cache.cached(key_prefix='index')
def index():
    init()
    return render_template('index.html',
                           **global_vars())


@app.route('/to-word', methods=['GET'])
@cache.cached(key_prefix=make_cache_key)
def submitted_form():
    params = get_request_params()

    number = params.number
    filter_nouns = params.filter_nouns

    filter_nouns = True if filter_nouns in ('on',) else False

    if filter_nouns:
        checked = 'checked'
    else:
        checked = ''

    t_start = time.process_time()
    words = convert_number_to_word(number, filter_nouns=filter_nouns)
    elapsed_time = time.process_time() - t_start
    extra_title = ''

    if words:
        extra_title = '| Number %s can be encoded in %s' % (number, ', '.join(words[0:4]))

    return render_template(
        'index.html',
        words=words,
        number=number,
        checked=checked,
        elapsed_time=elapsed_time,
        extra_title=extra_title,
        **global_vars()
    )


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8081, debug=True)
