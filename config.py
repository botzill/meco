DISABLE_DICT_DOWNLOAD = True
INIT_DB = False

ALPHANUM_CODE = {
    '0': {'sounds': ['s', 'z', 'c']},
    '1': {'sounds': ['t', 'd', 'th']},
    '2': {'sounds': ['n']},
    '3': {'sounds': ['m']},
    '4': {'sounds': ['r']},
    '5': {'sounds': ['l']},
    '6': {'sounds': ['sh', 'j', 'g', 'ch']},
    '7': {'sounds': ['k', 'c', 'g']},
    '8': {'sounds': ['v', 'f']},
    '9': {'sounds': ['p', 'b']},
}

REGEXP_SEP = '[aeiuowhy]*'

SOFT_SOUND_REGEXP = '[eiy]+'

DICT_WORDS_JSON_URL = 'https://raw.githubusercontent.com/dwyl/english-words/master/words_dictionary.json'
DICT_WORDS_FREQ_URL = 'http://norvig.com/ngrams/count_1w.txt'

