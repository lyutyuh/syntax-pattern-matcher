# syntax-pattern-matcher

A syntax pattern matcher based on **Stanford Corenlp parser** ([python wrapper](https://github.com/Lynten/stanford-corenlp)).

The syntax should be in the same format with **[PPDB syntax paraphrase](http://paraphrase.org/#/download)**.
For example:
  
```python
example_syntax_pattern_1 = ['[np,1]', 'are', 'certainly', 'difficult','[to,3]', '[vp,4]']
example_syntax_pattern_2 = ['[np/prp,1]', 'like', 'eating', '[np,2]','[pp,3]']
```

The tags should conform to Penn Treebank tags, which are explained in the [reference](https://gist.github.com/nlothian/9240750).

## Running samples:

```python

>>> example_sentence = 'Some cats are certainly difficult to deal with.'
>>> example_syntax_pattern = ['[np,1]', 'are', 'certainly', 'difficult','[to,3]', '[vp,4]']
>>> print(SyntaxTree.matchPattern(example_sentence, example_syntax_pattern))
[(1, 'NP', ['Some', 'cats']), (3, 'TO', ['to']), (4, 'VP', ['deal', 'with'])]
```

```python
>>> example_sentence = 'Dogs like eating sandwiches for breakfast.'
>>> example_syntax_pattern = ['[np,1]', 'like', 'eating', '[np,2]','[pp,3]']
>>> print(SyntaxTree.matchPattern(example_sentence, example_syntax_pattern))
[(1, 'NP', ['Dogs']), (2, 'NP', ['sandwiches']), (3, 'PP', ['for', 'breakfast'])]
```

### Use '/' to match a set of tags
```python
>>> example_sentence = 'Dogs like eating bread and meat.'
>>> example_syntax_pattern = ['[np/prp,1]', 'like', 'eating', '[np/pp,2]']
>>> print(SyntaxTree.matchPattern(example_sentence, example_syntax_pattern))
[(1, 'NP', ['Dogs']), (2, 'NP', ['bread', 'and', 'meat'])]
# NP(Noun Phrase) and NP matched

>>> example_sentence = 'We like eating at home.'
>>> example_syntax_pattern = ['[np/prp,1]', 'like', 'eating', '[np/pp,2]']
>>> print(SyntaxTree.matchPattern(example_sentence, example_syntax_pattern))
[(1, 'PRP', ['We']), (2, 'PP', ['at', 'home'])]
# PRP(Personal pronoun) and PP(Prepositional Phrase) matched
```

Requirements:

```
pip install nltk
pip install stanfordcorenlp
```
