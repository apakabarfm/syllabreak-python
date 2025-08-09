import pytest
from syllabreak import Syllabreak
from syllabreak.syllabreak import Token


class TestTokenization:
    def setup_method(self):
        self.s = Syllabreak("-")
    
    def test_tokenize_english_simple(self):
        """Test basic English word tokenization."""
        rule = self.s._select_language_rule("hello")
        tokens = self.s._tokenize_word("hello", rule)
        
        assert len(tokens) == 5
        assert tokens[0].surface == "h"
        assert tokens[0].token_class == "cons"
        assert tokens[1].surface == "e"
        assert tokens[1].token_class == "vowel"
        assert tokens[2].surface == "l"
        assert tokens[2].token_class == "cons"
        assert tokens[3].surface == "l"
        assert tokens[3].token_class == "cons"
        assert tokens[4].surface == "o"
        assert tokens[4].token_class == "vowel"
    
    def test_tokenize_serbian_latin_digraph_nj(self):
        """Test Serbian Latin 'nj' digraph tokenization."""
        rule = self.s._select_language_rule("njegov")
        tokens = self.s._tokenize_word("njegov", rule)
        
        # Print for debugging
        print(f"\nTokens for 'njegov':")
        for i, t in enumerate(tokens):
            print(f"  {i}: '{t.surface}' class={t.token_class}")
        
        # 'nj' should be a single token
        expected_surfaces = ["nj", "e", "g", "o", "v"]
        actual_surfaces = [t.surface for t in tokens]
        assert actual_surfaces == expected_surfaces, f"Expected {expected_surfaces}, got {actual_surfaces}"
        
        assert tokens[0].token_class == "cons"  # nj is a consonant digraph
        assert tokens[1].token_class == "vowel"  # e
        assert tokens[2].token_class == "cons"   # g
        assert tokens[3].token_class == "vowel"  # o
        assert tokens[4].token_class == "cons"   # v
    
    def test_tokenize_serbian_latin_digraph_lj(self):
        """Test Serbian Latin 'lj' digraph tokenization."""
        rule = self.s._select_language_rule("učitelj")
        tokens = self.s._tokenize_word("učitelj", rule)
        
        print(f"\nTokens for 'učitelj':")
        for i, t in enumerate(tokens):
            print(f"  {i}: '{t.surface}' class={t.token_class}")
        
        # Check that 'lj' is a single token
        surfaces = [t.surface for t in tokens]
        assert "lj" in surfaces, f"'lj' should be a single token, got {surfaces}"
    
    def test_tokenize_russian_soft_sign(self):
        """Test Russian soft sign (ь) tokenization."""
        rule = self.s._select_language_rule("компьютер")
        tokens = self.s._tokenize_word("компьютер", rule)
        
        print(f"\nTokens for 'компьютер':")
        for i, t in enumerate(tokens):
            print(f"  {i}: '{t.surface}' class={t.token_class}")
        
        # ь should attach to the previous token (п)
        surfaces = [t.surface for t in tokens]
        assert "пь" in surfaces, f"'пь' should be a single token with soft sign attached, got {surfaces}"
        
        # ью should be a digraph vowel
        assert "ю" in surfaces, f"'ю' should be a token, got {surfaces}"
    
    def test_tokenize_english_world(self):
        """Test 'world' tokenization - special case with 'rl' cluster."""
        rule = self.s._select_language_rule("world")
        tokens = self.s._tokenize_word("world", rule)
        
        print(f"\nTokens for 'world':")
        for i, t in enumerate(tokens):
            print(f"  {i}: '{t.surface}' class={t.token_class}")
        
        assert len(tokens) == 5
        assert tokens[0].surface == "w"
        assert tokens[0].token_class == "cons"
        assert tokens[1].surface == "o"
        assert tokens[1].token_class == "vowel"
        assert tokens[2].surface == "r"
        assert tokens[2].token_class == "cons"
        assert tokens[3].surface == "l"
        assert tokens[3].token_class == "cons"
        assert tokens[4].surface == "d"
        assert tokens[4].token_class == "cons"
    
    def test_find_nuclei_simple(self):
        """Test nucleus detection in simple word."""
        rule = self.s._select_language_rule("hello")
        tokens = self.s._tokenize_word("hello", rule)
        nuclei = self.s._find_nuclei(tokens, rule)
        
        # hello has two vowels: e (index 1) and o (index 4)
        assert nuclei == [1, 4]
    
    def test_find_nuclei_serbian_njegov(self):
        """Test nucleus detection in Serbian 'njegov'."""
        rule = self.s._select_language_rule("njegov")
        tokens = self.s._tokenize_word("njegov", rule)
        nuclei = self.s._find_nuclei(tokens, rule)
        
        print(f"\nNuclei for 'njegov': {nuclei}")
        print(f"Token indices: {[(i, t.surface) for i, t in enumerate(tokens)]}")
        
        # Should have nuclei at 'e' and 'o' positions
        # If tokenized correctly: ["nj", "e", "g", "o", "v"]
        # Nuclei should be at indices 1 and 3
        assert len(nuclei) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])