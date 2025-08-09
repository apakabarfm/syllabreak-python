import pytest
from syllabreak import Syllabreak
from syllabreak.tokenizer import Tokenizer
from syllabreak.language_rule import LanguageRule


def create_test_rule(**overrides):
    """Create a test LanguageRule with defaults that can be overridden."""
    default_data = {
        'lang': 'test',
        'vowels': 'aeiou',
        'consonants': 'bcdfghjklmnpqrstvwxyz',
        'sonorants': 'lmnr',
        'clusters_keep_next': [],
        'dont_split_digraphs': [],
        'digraph_vowels': [],
        'glides': '',
        'syllabic_consonants': '',
        'modifiers_attach_left': '',
        'modifiers_attach_right': '',
        'modifiers_separators': ''
    }
    default_data.update(overrides)
    return LanguageRule(default_data)


def test_syllabic_r_creates_nucleus():
    """Test that syllabic 'r' can be a nucleus when not adjacent to vowels."""
    rule = create_test_rule(
        vowels='aeiou',
        consonants='bcdfghjklmnpqrstvwxyz',
        syllabic_consonants='r'
    )
    
    s = Syllabreak("-")
    # 'brr' - b(cons) r(syllabic) r(cons)
    tokens = Tokenizer("brr", rule).tokenize()
    nuclei = s._find_nuclei(tokens, rule)
    
    # 'r' at index 1 should be a nucleus (no adjacent vowels)
    assert 1 in nuclei


def test_syllabic_l_creates_nucleus():
    """Test that syllabic 'l' can be a nucleus when not adjacent to vowels."""
    rule = create_test_rule(
        vowels='aeiou',
        consonants='bcdfghjklmnpqrstvwxyz',
        syllabic_consonants='l'
    )
    
    s = Syllabreak("-")
    # 'bll' - b(cons) l(syllabic) l(cons)
    tokens = Tokenizer("bll", rule).tokenize()
    nuclei = s._find_nuclei(tokens, rule)
    
    # 'l' at index 1 should be a nucleus (no adjacent vowels)
    assert 1 in nuclei


def test_syllabic_not_nucleus_with_adjacent_vowel():
    """Test that syllabic consonant is NOT a nucleus when adjacent to vowel."""
    rule = create_test_rule(
        vowels='aeiou',
        consonants='bcdfghjklmnpqrstvwxyz',
        syllabic_consonants='rl'
    )
    
    s = Syllabreak("-")
    
    # 'world' - w(cons) o(vowel) r(cons but adjacent to vowel) l(cons) d(cons)
    tokens = Tokenizer("world", rule).tokenize()
    nuclei = s._find_nuclei(tokens, rule)
    
    # Only 'o' at index 1 should be nucleus
    # 'r' and 'l' are adjacent to vowel 'o' so not nuclei
    assert nuclei == [1]


def test_english_syllabic_consonants():
    """Test what syllabic consonants are defined for English."""
    s = Syllabreak("-")
    eng_rule = s._get_rule_by_lang("eng")
    
    # English defines these as syllabic
    assert 'l' in eng_rule.syllabic_consonants
    assert 'm' in eng_rule.syllabic_consonants
    assert 'n' in eng_rule.syllabic_consonants
    assert 'r' in eng_rule.syllabic_consonants


def test_world_has_single_nucleus():
    """Test that 'world' has only one nucleus."""
    s = Syllabreak("-")
    rule = s._get_rule_by_lang("eng")
    tokens = s._tokenize_word("world", rule)
    nuclei = s._find_nuclei(tokens, rule)
    
    # 'world' should have only one nucleus at 'o'
    assert len(nuclei) == 1
    assert tokens[nuclei[0]].surface == 'o'