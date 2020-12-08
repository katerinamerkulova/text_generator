"""
Lab 4
"""

import re

from ngrams.ngram_trie import NGramTrie
import validation


def tokenize_by_sentence(text: str) -> tuple:
    validation.ensure_type({str: text})

    # внутри [] не нужно маскировать . и ?
    clean_text = re.sub(r'[^\.!\?\w\s]', '', text)
    # следующие две строчки можно заменить на одну, это будет быстрее:
    # tokens = tuple(re.sub(r'([A-Z][\w\s]+)[.!?]?', r'\1'.lower() + ' <END>', text).split())
    sentences = re.sub(r'([A-Z][\w\s]+)[.!?]?', r'\1 <end>', clean_text).lower()
    splitted_text = tuple(re.sub(r'<end>', r'<END>', sentences).split())
    return splitted_text


class WordStorage:

    def __init__(self):
        self.storage = {}
        self._reverse_storage = {}

    def _put_word(self, word: str) -> int:
        validation.ensure_type({str: word})
        validation.is_empty(word)
    
        if word not in self.storage:
            # обновляем _reverse_storage!
            # word_id = len(self.storage)
            # self.storage[word] = word_id
            # self._reverse_storage[word_id] = word
            self.storage[word] = len(self.storage)
        return self.storage[word]

    def get_id(self, word: str) -> int:
        validation.ensure_type({str: word})
        # следующая строчка не нужна, т.к. self.storage[word] и так даст KeyError
        validation.is_in(word, self.storage)

        return self.storage[word]

    def _update_reverse_storage(self):
        self._reverse_storage = {
            key: value for key, value in zip(
                self.storage.values(),
                self.storage.keys(),
                )
            }

    def get_word(self, word_id: int) -> str:
        validation.ensure_type({int: word_id})
        # здесь лучше не вызывать метод _update... сразу, а сначала поискать word_id в
        # _reverse_storage. Если не находится, тогда сделать рефреш _reverse_storage методом
        # _update... и поискать word_id ещё раз. Если всё же не находится, вот тогда ошибка.
        # таким образом, полный рефреш делается только как защитная мера от грёбаного тупого теста,
        # а при нормальном сценарии в нём нет необходимости, т.к. обратный индекс пополняется
        # автоматически в _put_word
        self._update_reverse_storage()
        validation.is_in(word_id, self._reverse_storage)
        
        return self._reverse_storage[word_id]

    def update(self, corpus: tuple):
        validation.ensure_type({tuple: corpus})

        # ни в коем случае не set! просто `for word in corpus:`
        for word in set(corpus):
            self._put_word(word)


def encode_text(storage: WordStorage, text: tuple) -> tuple:
    validation.ensure_type({WordStorage: storage, tuple: text})

    return tuple(storage.get_id(word) for word in text)


class NGramTextGenerator:

    def __init__(self, word_storage: WordStorage, n_gram_trie: NGramTrie):
        self._word_storage = word_storage
        self._n_gram_trie = n_gram_trie

    def _generate_next_word(self, context: tuple) -> int:
        validation.ensure_type({tuple: context})
        validation.is_correct_length(context, self._n_gram_trie.size - 1)

        # поскольку ключи уникальны, слова с одинаковой частотой "затирают" друг друга
        # на это можно сделать test case
        # а здесь ещё неоправданно создаётся лишний словарь с теми же данными, что и в
        # n_gram_frequencies, только в обратном порядке. Это неэкономно с т.зр. памяти,
        # т.к. нужно найти всего одну пару ключ-значение с максимальной частотой.
        all_n_grams = {
            freq: n_gram for n_gram, freq 
            in self._n_gram_trie.n_gram_frequencies.items()
            if n_gram[:-1] == context
            }

        if all_n_grams:
            max_freq = max(all_n_grams.keys())
            n_gram = all_n_grams[max_freq]

        else:
            max_freq = 0
            for uni_gram in self._n_gram_trie.uni_grams:
                if self._n_gram_trie.uni_grams[uni_gram] > max_freq:
                    max_freq = self._n_gram_trie.uni_grams[uni_gram]
                    n_gram = uni_gram

        return n_gram[-1]

    def _generate_sentence(self, context: tuple) -> tuple:
        validation.ensure_type({tuple: context})

        sent = context
        length = self._n_gram_trie.size - 1
        n_gram = sent[-length:]
        end_id = self._word_storage.get_id('<END>')
        for i in range(20):
            sent += (self._generate_next_word(n_gram), )
            if sent[-1] == end_id:
                break
            n_gram = sent[-length:]
        else:
            sent += (end_id, )
        return sent

    def generate_text(self, context: tuple, number_of_sentences: int) -> tuple:
        validation.ensure_type({tuple: context, int: number_of_sentences})

        text = tuple()
        length = self._n_gram_trie.size - 1
        for i in range(number_of_sentences):
            text += self._generate_sentence(context)[1:]
            context = text[-length:]
        return text


class LikelihoodBasedTextGenerator(NGramTextGenerator):

    def _calculate_maximum_likelihood(self, word: int, context: tuple) -> float:
        validation.ensure_type({int: word, tuple: context})
        validation.is_correct_length(context, self._n_gram_trie.size - 1)

        current_n_gram = context + (word, )

        try:
            current_freq = self._n_gram_trie.n_gram_frequencies[current_n_gram]

        except KeyError:
            return 0

        else:
            common_freq = sum(
                self._n_gram_trie.n_gram_frequencies[n_gram]
                for n_gram in self._n_gram_trie.n_gram_frequencies
                if n_gram[:-1] == context)
            return current_freq / common_freq

    def _generate_next_word(self, context: tuple) -> int:
        validation.ensure_type({tuple: context})
        validation.is_correct_length(context, self._n_gram_trie.size - 1)

        self._word_storage._update_reverse_storage()
        likelihood = {
            self._calculate_maximum_likelihood(word, context): word
            for word in self._word_storage._reverse_storage
            }
        max_likelihood = max(likelihood.keys())

        return likelihood[max_likelihood]


def decode_text(storage: WordStorage, encoded_text: tuple) -> tuple:
    validation.ensure_type({WordStorage: storage, tuple: encoded_text})

    text = ' '.join((storage.get_word(word) for word in encoded_text))
    text = text.split('<END>')

    return tuple(text)


class BackOffGenerator(NGramTextGenerator):

    def __init__(self, word_storage: WordStorage, n_gram_trie: NGramTrie, *args):
        super().__init__(word_storage, n_gram_trie)

        tries = (n_gram_trie, ) + args
        self._n_gram_tries = sorted(tries, key = lambda trie: trie.size)[::-1]

    def _generate_next_word(self, context: tuple) -> int:
        validation.ensure_type({tuple: context})

        max_trie_size = len(context) + 1
        self._n_gram_tries = [trie for trie in self._n_gram_tries if trie.size <= max_trie_size]

        for trie in self._n_gram_tries:
            self._n_gram_trie = trie
            if n_gram := super()._generate_next_word(context):
                return n_gram
            context = context[:-1]


def save_model(model: NGramTextGenerator, path_to_saved_model: str):
    pass


def load_model(path_to_saved_model: str) -> NGramTextGenerator:
    pass
