import pytest
from syllabreak.tokenizer import Tokenizer, Token
from syllabreak.language_rule import LanguageRule


def create_test_rule(lang="test", **overrides):
    """Create a test LanguageRule with defaults that can be overridden."""
    default_data = {
        'lang': lang,
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


class TestTokenizerDigraphs:
    def test_consonant_digraph_nj(self):
        """Test that 'nj' is recognized as a single consonant digraph."""
        rule = create_test_rule(
            vowels='aeio',
            consonants='njgv',
            dont_split_digraphs=['nj']
        )
        
        tokenizer = Tokenizer("njegov", rule)
        tokens = tokenizer.tokenize()
        
        surfaces = [t.surface for t in tokens]
        assert surfaces == ["nj", "e", "g", "o", "v"]
        assert tokens[0].token_class == "cons"
        assert tokens[0].start_idx == 0
        assert tokens[0].end_idx == 2
    
    def test_consonant_digraph_precedence(self):
        """Test that consonant digraphs have precedence over single chars."""
        rule = create_test_rule(
            vowels='aeiou',
            consonants='chlst',
            dont_split_digraphs=['ch', 'sh', 'th']
        )
        
        tokenizer = Tokenizer("cheat", rule)
        tokens = tokenizer.tokenize()
        
        surfaces = [t.surface for t in tokens]
        assert surfaces == ["ch", "e", "a", "t"]
        assert tokens[0].token_class == "cons"
    
    def test_vowel_digraph(self):
        """Test vowel digraph recognition."""
        rule = create_test_rule(
            vowels='aeiou',
            consonants='bcdfg',
            digraph_vowels=['ea', 'ee']
        )
        
        tokenizer = Tokenizer("beat", rule)
        tokens = tokenizer.tokenize()
        
        surfaces = [t.surface for t in tokens]
        assert surfaces == ["b", "ea", "t"]
        assert tokens[1].token_class == "vowel"


class TestTokenizerModifiers:
    def test_left_attaching_modifier(self):
        """Test that left-attaching modifiers attach to previous token."""
        rule = create_test_rule(
            vowels='aoуие',
            consonants='кмпьтр',
            modifiers_attach_left='ь'
        )
        
        tokenizer = Tokenizer("компь", rule)
        tokens = tokenizer.tokenize()
        
        surfaces = [t.surface for t in tokens]
        assert surfaces == ["к", "о", "м", "пь"]
        assert tokens[3].is_modifier == True
    
    def test_separator(self):
        """Test separator tokens."""
        rule = create_test_rule(
            vowels='aeiou',
            consonants='bcdfg',
            modifiers_separators='-'
        )
        
        tokenizer = Tokenizer("ab-cd", rule)
        tokens = tokenizer.tokenize()
        
        surfaces = [t.surface for t in tokens]
        classes = [t.token_class for t in tokens]
        assert surfaces == ["a", "b", "-", "c", "d"]
        assert classes == ["vowel", "cons", "sep", "cons", "cons"]


class TestTokenizerSingleChars:
    def test_vowel_classification(self):
        """Test single vowel classification."""
        rule = create_test_rule()
        
        tokenizer = Tokenizer("aei", rule)
        tokens = tokenizer.tokenize()
        
        assert all(t.token_class == "vowel" for t in tokens)
    
    def test_consonant_classification(self):
        """Test single consonant classification."""
        rule = create_test_rule()
        
        tokenizer = Tokenizer("bcd", rule)
        tokens = tokenizer.tokenize()
        
        assert all(t.token_class == "cons" for t in tokens)
    
    def test_glide_classification(self):
        """Test that glides are marked correctly."""
        rule = create_test_rule(
            consonants='bcdjwy',
            glides='jwy'
        )
        
        tokenizer = Tokenizer("jay", rule)
        tokens = tokenizer.tokenize()
        
        assert tokens[0].token_class == "cons"
        assert tokens[0].is_glide == True
        assert tokens[2].token_class == "cons"
        assert tokens[2].is_glide == True
    
    def test_unknown_char_classification(self):
        """Test that unknown characters get 'other' class."""
        rule = create_test_rule(
            vowels='aeiou',
            consonants='bcdfg'
        )
        
        tokenizer = Tokenizer("a#b", rule)
        tokens = tokenizer.tokenize()
        
        assert tokens[0].token_class == "vowel"
        assert tokens[1].token_class == "other"
        assert tokens[2].token_class == "cons"


class TestTokenizerEdgeCases:
    def test_empty_string(self):
        """Test tokenizing empty string."""
        rule = create_test_rule()
        tokenizer = Tokenizer("", rule)
        tokens = tokenizer.tokenize()
        assert tokens == []
    
    def test_case_preservation(self):
        """Test that original case is preserved in surface."""
        rule = create_test_rule()
        tokenizer = Tokenizer("HeLLo", rule)
        tokens = tokenizer.tokenize()
        
        surfaces = [t.surface for t in tokens]
        assert surfaces == ["H", "e", "L", "L", "o"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])