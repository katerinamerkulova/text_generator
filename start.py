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

generator = NGramTextGenerator(storage, trie)

context = (storage.get_id('bruno'),)
end = storage.get_id('<END>')
actual = generator.generate_text(context, 3)

print(f'EXPECTED:\n{3}')
print(f'ACTUAL:\n{actual.count(end)}')
print(end)
print(actual)