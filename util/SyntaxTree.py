from stanfordcorenlp import StanfordCoreNLP
import queue
import nltk
import re
import itertools
from .SkipGram import skipgrams

PATH_TO_CORENLP = '../../stanford_corenlp/stanford-corenlp-full-2018-10-05/'
nlp_server = StanfordCoreNLP(PATH_TO_CORENLP)

class parseTree():
    class TreeNode():
        def __init__(self):
            self.father = None
            self.children = []
            self.tag = None
            self.span = None            
            
    def treeTransform(self):
        root = self.TreeNode()
        my_Q = queue.Queue()
        my_Q.put((root, self.tree))
        while my_Q.qsize() > 0:
            fatherChild = my_Q.get()
            # except for the root, tmp should be (father, child)
            tmp = self.TreeNode()
            if type(fatherChild[1]) == str:
                tmp.tag = fatherChild[1]
                tmp.father = fatherChild[0]
                fatherChild[0].children.append(tmp)
                continue
            else:
                tmp.tag = fatherChild[1].label()
                
            tmp.father = fatherChild[0]
            fatherChild[0].children.append(tmp)
            for child in list(fatherChild[1]):
                my_Q.put((tmp, child))             
        return root.children[0]
    
    def getLeaves(self, _treeNode, leftMost):
        tmp = []
        starting = leftMost
        for x in _treeNode.children:
            if len(x.children) == 0:
                tmp.append(x)
            else:
                _child_leaves = self.getLeaves(x, leftMost)
                tmp += _child_leaves
                leftMost += len(_child_leaves)
        _treeNode.span = (starting, starting + len(tmp))
        return tmp
    
    def _contains(self, bigspan, smallspan):
        if smallspan[0] >= bigspan[0] and smallspan[1] <= bigspan[1]:
            return True
        else:
            return False
        
    def lowest_ancestor(self, _root, _span):
        for x in _root.children:
            if not x.span:
                # x is leaf
                continue
            if self._contains(x.span, _span):
                return self.lowest_ancestor(x, _span)
        return _root
    
    def _search_tag_in_span(self, _tag, _span):
        _leftmost_id = _span[0]
        _rightmost_id = _span[1]
        _leftmost_leaf = self.leaves[_leftmost_id]
        if _leftmost_id != -1 and _rightmost_id != self.length:
            # looking top-bottom for full-length phrase in _span
            _returned_anc = self.lowest_ancestor(self.tree, _span)
            _returned_span, _returned_tag = _returned_anc.span, _returned_anc.tag            
            while self._contains(_span, _returned_span):
                if _returned_tag in _tag[0]:
                    return (_tag[1], _returned_tag, _span)
                else:
                    _returned_anc = _returned_anc.father
                    _returned_span, _returned_tag = _returned_anc.span, _returned_anc.tag                    
            return None
        else:
            # looking bottom-top for phrase adjacent to one side of _span
            if _leftmost_id == -1:
                for i in range(0, _rightmost_id):
                    # search (i, _rightmost_id)
                    _canBeFound = self._search_tag_in_span(_tag, (i, _rightmost_id))
                    if _canBeFound is not None:
                        return _canBeFound
            elif _rightmost_id == self.length:
                for i in range(self.length-1, _leftmost_id, -1):
                    _canBeFound = self._search_tag_in_span(_tag, (_leftmost_id, i))
                    if _canBeFound is not None:
                        return _canBeFound
            return None
    
    def get_substring(self, span_tuple):
        return self.sentenceAsList[slice(span_tuple[0], span_tuple[1])]
    def indice_toword(self, indices_list):
        return [self.sentenceAsList[x] for x in indices_list]
    
    def _match_one_syntax(self, _one_syntax):
        _span = _one_syntax[0]
        if _span[1] is None:
            _span = (_span[0], self.length)
        _type = _one_syntax[1]
        _type = [x[1:-1].split(',') for x in _type]
        _type = [(re.split('[\\\/]', x[0]), int(x[1])) for x in _type]
        # _type should be a list of ([np, vp], 1), ([np], 2)...
        # _span should be like (-1, 9)...
        # searching in _span:
        _number_of_targets = len(_type)
        _matched_targets = []
        for _bounds in itertools.combinations(range(_span[0]+1, _span[1]), _number_of_targets-1):
            _prev = _span[0]
            if _prev == -1:
                _prev = 0
            _type_ptr = 0
            flag_this_seg_is_fine = True
            for _next in _bounds+(_span[1], ):
                _tmp_span = (_prev, _next)
                _one_matched = self._search_tag_in_span(_type[_type_ptr], _tmp_span)
                if _one_matched is None:
                    flag_this_seg_is_fine = False
                    break
                _type_ptr += 1
                _matched_targets.append(_one_matched)
                _prev = _next
            if not flag_this_seg_is_fine:
                _matched_targets = []
            else:
                break
        return _matched_targets        
        
    def match_syntax(self, _syntax):
        # _syntax should be like: [((-1, 9), ['[NP,1]']), ((9, 14), ['[NP,2]']), ((14, None), ['[NP,3]', '[VP,4]'])]        
        # a list of (span, type)
        _matched_all_syntax = []
        for x in _syntax:
            _matched_all_syntax.append(self._match_one_syntax(x))
        return _matched_all_syntax
    
    def __init__(self, sentence):
        # parsingResult should be a string
        parsingResult = nlp_server.parse(sentence)
        assert type(parsingResult) == str
        self.tree = nltk.Tree.fromstring(parsingResult)
        self.tree = self.treeTransform()
        self.leaves = self.getLeaves(self.tree, 0)
        self.length = len(self.leaves)
        self.sentenceAsList = [x.tag for x in self.leaves] # should be same with corenlp tokenized result
        self.sentenceAsString = ' '.join(self.sentenceAsList)
        
        
        
def check_words_equal(list_1, list_2):
    if len(list_1) == len(list_2):
        _idx = 0
        for x1 in list_1:
            if x1 != list_2[_idx]:
                return False
            _idx += 1
        return True
    else:
        return False
    
def search_pattern(_pattern, _fixed_points):
    _ptr = 0
    _toBeMatched = []
    _starting = -1 # from head to tail
    _tmp = []
    for x in _pattern:
        if x[0] == '[':
            _tmp.append(x)
            pass
        else:
            if len(_tmp) > 0:
                _ending = _fixed_points[_ptr][0]
                _toBeMatched.append(((_starting, _ending), _tmp))
                _starting = _ending
            _starting = _fixed_points[_ptr][0] + 1
            _tmp = []
            _ptr += 1
    if len(_tmp) > 0:
        _ending = None
        _toBeMatched.append(((_starting, _ending), _tmp))
    return _toBeMatched
    
def match_all(_parseTree, _toBeMatched):
    _syn_to_pass = []
    _toreturn = []
    for x in _toBeMatched:
        _span = x[0]
        _target = x[1]
        for _idy, y in enumerate(_target):
            _target[_idy] = y.upper()            
        _syn_to_pass.append((_span, _target))
    return _parseTree.match_syntax(_syn_to_pass)

def matchPattern(sentence, pattern):
    # a pattern should be like ['it', 'is', '[JJ,1]', 'to', '[VP,2]']
    # maximum 10 fixed words, minimum 2
    pattern_word_set = []
    for x in pattern:
        if x[0] != '[':
            pattern_word_set.append(x)    
    myParseTree = parseTree(sentence)
    sentence = myParseTree.sentenceAsList
    skip_grams = []
    for i in range(1, min(6, len(sentence))):
        skip_grams += skipgrams(sentence, i, min(i, len(sentence)))
        
    matched = None
    for skg in skip_grams:
        if check_words_equal([x[1] for x in skg], pattern_word_set):
            pat = search_pattern(pattern, skg)
            # pat should be something like [((-1, 2), ['[np,1]']), ((3, None), ['[rb,2]', '[jj,3]', '[sbar/vp,4]'])]
            matched = match_all(myParseTree, pat)
            break
    
    _toret = []
    for chunk in matched:
        for piece in chunk:
            _toret.append((piece[0], piece[1], myParseTree.get_substring(piece[2])))
    return _toret