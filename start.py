"""
Example of running programm in lab_4
"""

from main import tokenize_by_sentence, WordStorage, encode_text, BackOffGenerator
from ngrams.ngram_trie import NGramTrie

'''
def main():
    text = ('I have a cat. His name is Bruno. '
            'I have a dog too. His name is Rex. '
            'Her name is Rex too.')
    
    corpus = tokenize_by_sentence(text)

    storage = WordStorage()
    storage.update(corpus)

    encoded = encode_text(storage, corpus)

    two = NGramTrie(2, encoded)
    trie = NGramTrie(3, encoded)

    expected_word = storage.get_id('rex')
    context = (storage.get_id('name'),
               storage.get_id('is'),)

    generator = BackOffGenerator(storage, trie, two)

    actual = generator._generate_next_word(context)

    print(f'TEXT:\n{text}')
    print('\nEXPECTED WORD AFTER name is IS rex')
    print(f'ACTUAL WORD AFTER name is IS {storage.get_word(actual)}')


if __name__ == "__main__":
    main()


'''

from main import NGramTextGenerator, WordStorage, encode_text
from ngrams.ngram_trie import NGramTrie

corpus = ('i', 'have', 'a', 'cat', '<END>',
          'his', 'name', 'is', 'bruno', '<END>',
          'i', 'have', 'a', 'dog', 'too', '<END>',
          'his', 'name', 'is', 'rex', '<END>',
          'her', 'name', 'is', 'rex', 'too', '<END>')
storage = WordStorage()
storage.update(corpus)
encoded = encode_text(storage, corpus)
trie = NGramTrie(2, encoded)
context = (storage.get_id('i'), )

first_generated = storage.get_id('have')
last_generated = storage.get_id('<END>')

generator = NGramTextGenerator(storage, trie)
actual = generator._generate_sentence(context)
print(actual[1], first_generated)
print(actual[-1], last_generated)
print(actual)