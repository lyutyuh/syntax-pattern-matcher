from util import SyntaxTree

if __name__ == '__main__':
    example_sentence = 'It is important to eat breakfast.'
    example_syntax_pattern = ['It', 'is', '[JJ,1]', 'to', '[VP,2]']
    
    print(SyntaxTree.matchPattern(example_sentence, example_syntax_pattern))

