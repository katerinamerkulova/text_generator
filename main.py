"""
Lab 4
"""

## add test for empty inputs
## add test for input 0

import ast
from pprint import pprint
import re

from ngrams.ngram_trie import NGramTrie
import validation


def tokenize_by_sentence(text: str) -> tuple:
    validation.ensure_type((text, str))

    clean_text = re.sub(r'[^.!?\w\s]', '', text)
    tokens = tuple(re.sub(r'([A-Z][\w\s]+)[.!?]?',
                          lambda x: x.group(1).lower() + ' <END>',
                          clean_text
                          ).split())
    return tokens


class WordStorage:

    def __init__(self):
        self.storage = {}
        self.reversed_storage = {}

    def _put_word(self, word: str) -> int:
        validation.ensure_type((word, str))
        validation.ensure_not_empty(word)
    
        if word not in self.storage:
            word_id = len(self.storage)
            self.storage[word] = word_id
            self.reversed_storage[word_id] = word

        return self.storage[word]

    def get_id(self, word: str) -> int:
        validation.ensure_type((word, str))

        return self.storage[word]

    def update_reversed_storage(self):
        self.reversed_storage = {
            key: value for key, value in zip(
                self.storage.values(),
                self.storage.keys(),
                )
            }

    def get_word(self, word_id: int) -> str:
        validation.ensure_type((word_id, int))
        
        if word_id not in self.reversed_storage:
            self.update_reversed_storage()

        return self.reversed_storage[word_id]

    def update(self, corpus: tuple):
        validation.ensure_type((corpus, tuple))

        for word in corpus:
            self._put_word(word)


def encode_text(storage: WordStorage, text: tuple) -> tuple:
    validation.ensure_type(
        (storage, WordStorage),
        (text, tuple),
        )

    return tuple(storage.get_id(word) for word in text)


class NGramTextGenerator:

    def __init__(self, word_storage: WordStorage, n_gram_trie: NGramTrie):
        self._word_storage = word_storage
        self._n_gram_trie = n_gram_trie

    def _generate_next_word(self, context: tuple) -> int:
        validation.ensure_type((context, tuple))
        validation.ensure_length(context, self._n_gram_trie.size - 1)

        freqs = self._n_gram_trie.n_gram_frequencies
        max_freq = 0

        if any(n_gram for n_gram in freqs if n_gram[:-1] == context):
            for n_gram in freqs:
                if freqs[n_gram] > max_freq and n_gram[:-1] == context:
                    max_freq = freqs[n_gram]
                    max_n_gram = n_gram
        else:
            for uni_gram in self._n_gram_trie.uni_grams:
                if self._n_gram_trie.uni_grams[uni_gram] > max_freq:
                    max_freq = self._n_gram_trie.uni_grams[uni_gram]
                    max_n_gram = uni_gram
        return max_n_gram[-1]

    def _generate_sentence(self, context: tuple) -> tuple:
        validation.ensure_type((context, tuple))

        sent = list(context)
        length = self._n_gram_trie.size - 1
        n_gram = sent[-length:]
        end_id = self._word_storage.get_id('<END>')
        for i in range(20):
            sent.append(self._generate_next_word(n_gram))
            if sent[-1] == end_id:
                break
            n_gram = sent[-length:]
        else:
            sent.append(end_id)
        return tuple(sent)

    def generate_text(self, context: tuple, number_of_sentences: int) -> tuple:
        validation.ensure_type(
            (context, tuple),
            (number_of_sentences, int),
            )

        text = tuple()
        length = self._n_gram_trie.size - 1
        for i in range(number_of_sentences):
            text += self._generate_sentence(context)[1:]
            context = text[-length:]
        return text


class LikelihoodBasedTextGenerator(NGramTextGenerator):

    def _calculate_maximum_likelihood(self, word: int, context: tuple) -> float:
        validation.ensure_type(
            (word, int),
            (context, tuple),
            )
        validation.ensure_length(context, self._n_gram_trie.size - 1)

        current_n_gram = context + (word, )
        freq = self._n_gram_trie.n_gram_frequencies

        if current_freq := freq.get(current_n_gram, 0):
            common_freq = sum(
                freq[n_gram] for n_gram in freq
                if n_gram[:-1] == context
                )
            return current_freq / common_freq
        return 0

    def _generate_next_word(self, context: tuple) -> int:
        validation.ensure_type((context, tuple))
        validation.ensure_length(context, self._n_gram_trie.size - 1)

        self._word_storage.update_reversed_storage()
        likelihood = {
            self._calculate_maximum_likelihood(word, context): word
            for word in self._word_storage.reversed_storage
            }
        max_likelihood = max(likelihood.keys())

        return likelihood[max_likelihood]


def decode_text(storage: WordStorage, encoded_text: tuple) -> tuple:
    validation.ensure_type(
        (storage, WordStorage),
        (encoded_text, tuple),
        )

    text = ' '.join((storage.get_word(word) for word in encoded_text))
    text = text.split('<END>')

    return tuple(text)


class BackOffGenerator(NGramTextGenerator):

    def __init__(self, word_storage: WordStorage, n_gram_trie: NGramTrie, *args):
        super().__init__(word_storage, n_gram_trie)

        tries = [n_gram_trie] + list(args)
        self._n_gram_tries = sorted(tries, key=lambda trie: trie.size)[::-1]

    def _generate_next_word(self, context: tuple) -> int:
        validation.ensure_type((context, tuple))

        max_trie_size = len(context) + 1
        self._n_gram_tries = [trie for trie in self._n_gram_tries if trie.size <= max_trie_size]

        for trie in self._n_gram_tries:
            self._n_gram_trie = trie
            if n_gram := super()._generate_next_word(context):
                return n_gram
            context = context[:-1]


def save_model(model: NGramTextGenerator, path_to_saved_model: str):
    validation.ensure_type(
        (model, NGramTextGenerator),
        (path_to_saved_model, str),
        )

    #_n_gram_trie = 'encoded_text', 'n_gram_frequencies', 'n_grams', 'size', 'uni_grams'
    _n_gram_trie = {
        'encoded_text': model._n_gram_trie.encoded_text,
        'n_gram_frequencies': model._n_gram_trie.n_gram_frequencies,
        'n_grams': model._n_gram_trie.n_grams,
        'size': model._n_gram_trie.size,
        'uni_grams': model._n_gram_trie.uni_grams,
        }

    #_word_storage = 'storage', 'reversed_storage'
    _word_storage = {
        'storage': model._word_storage.storage,
        'reversed_storage': model._word_storage.reversed_storage,
        }

    model_dict = {
        'name': f'{type(model).__name__}',
        'data': {
            '_n_gram_trie' : _n_gram_trie,
            '_word_storage': _word_storage,
        }
    }

    # if *_n_gram_tries
    if model_dict['name'] == 'BackOffGenerator':
        _n_gram_tries = []

        for trie in model._n_gram_tries:
            _n_gram_trie = {
                'encoded_text': trie.encoded_text,
                'n_gram_frequencies': trie.n_gram_frequencies,
                'n_grams': trie.n_grams,
                'size': trie.size,
                'uni_grams': trie.uni_grams,
                }
            _n_gram_tries.append(_n_gram_trie)

        model_dict['data']['_n_gram_tries'] = _n_gram_tries

    with open(path_to_saved_model, 'w') as file:
        pprint(model_dict, stream=file, compact=True)


def load_model(path_to_saved_model: str) -> NGramTextGenerator:
    validation.ensure_type((path_to_saved_model, str))

    with open(path_to_saved_model, 'r') as file:
        model_dict = file.read()

    model_dict = ast.literal_eval(model_dict)

    _n_gram_trie = NGramTrie(
        model_dict['data']['_n_gram_trie']['size'],
        model_dict['data']['_n_gram_trie']['encoded_text'],
        )
    _n_gram_trie.n_gram_frequencies = model_dict['data']['_n_gram_trie']['n_gram_frequencies']
    _n_gram_trie.n_grams = model_dict['data']['_n_gram_trie']['n_grams']
    _n_gram_trie.uni_grams = model_dict['data']['_n_gram_trie']['uni_grams']

    _word_storage = WordStorage()
    _word_storage.storage = model_dict['data']['_word_storage']['storage']
    _word_storage.reversed_storage = model_dict['data']['_word_storage']['reversed_storage']
    
    if model_dict['name'] == 'NGramTextGenerator':
        generator = NGramTextGenerator(_word_storage, _n_gram_trie)
    
    elif model_dict['name'] == 'LikelihoodBasedTextGenerator':
        generator = LikelihoodBasedTextGenerator(_word_storage, _n_gram_trie)

    elif model_dict['name'] == 'BackOffGenerator':
        tries = []
        for trie in model_dict['data']['_n_gram_tries']:
            _n_gram_trie = NGramTrie(
                trie['size'],
                trie['encoded_text'],
                )
            _n_gram_trie.n_gram_frequencies = trie['n_gram_frequencies']
            _n_gram_trie.n_grams = trie['n_grams']
            _n_gram_trie.uni_grams = trie['uni_grams']
            tries.append(_n_gram_trie)

        generator = BackOffGenerator(_word_storage, _n_gram_trie, *tries)

    return generator
