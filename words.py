import json
import os

import requests

import config


def download_to_file(url, file_path):
    response = requests.get(url, stream=True, verify=False)
    with open(file_path, 'wb') as handle:
        for chunk in response.iter_content(chunk_size=512 * 10):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)


def abspath(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def load_words():
    filename = abspath('words_dictionary.json')
    if not os.path.exists(filename):
        download_to_file(config.DICT_WORDS_JSON_URL, filename)

    try:
        with open(filename, 'r') as english_dictionary:
            valid_words = json.load(english_dictionary)
            return list(valid_words.keys())
    except Exception as e:
        raise e


def load_words_frequencies():
    filename = abspath('count_1w.txt')
    if not os.path.exists(filename):
        download_to_file(config.DICT_WORDS_FREQ_URL, filename)

    words_by_freq = {}
    try:
        with open(filename, 'r') as english_dictionary_word_freq:
            for line in english_dictionary_word_freq.readlines():
                word, freq = line.split()
                words_by_freq[word] = freq
            return words_by_freq
    except Exception as e:
        raise e
