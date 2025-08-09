import pytest
from syllabreak import Syllabreak


class TestRuleSelectionLogic:
    def setup_method(self):
        self.s = Syllabreak("-")
    
    def test_english_rule_chars(self):
        """Test what characters are in English rule."""
        eng_rule = None
        for rule in self.s.meta_rule.rules:
            if rule.lang == "eng":
                eng_rule = rule
                break
        
        assert eng_rule is not None
        assert 'n' in eng_rule.consonants
        assert 'j' in eng_rule.consonants
        assert 'e' in eng_rule.vowels
        assert 'g' in eng_rule.consonants
        assert 'o' in eng_rule.vowels
        assert 'v' in eng_rule.consonants
        # So "njegov" contains only chars that are in English
    
    def test_serbian_latin_rule_chars(self):
        """Test what characters are in Serbian Latin rule."""
        srp_rule = None
        for rule in self.s.meta_rule.rules:
            if rule.lang == "srp-latn":
                srp_rule = rule
                break
        
        assert srp_rule is not None
        # Check special Serbian chars
        assert 'č' in srp_rule.consonants
        assert 'š' in srp_rule.consonants
        assert 'ž' in srp_rule.consonants
        
    def test_rules_order(self):
        """Test the order of rules in meta_rule."""
        rule_order = [rule.lang for rule in self.s.meta_rule.rules]
        # English comes before Serbian Latin
        eng_idx = rule_order.index("eng")
        srp_idx = rule_order.index("srp-latn")
        assert eng_idx < srp_idx, f"English at {eng_idx}, Serbian Latin at {srp_idx}"
    
    def test_unique_chars_for_serbian_latin(self):
        """Test unique characters that only Serbian Latin has."""
        srp_rule = None
        for rule in self.s.meta_rule.rules:
            if rule.lang == "srp-latn":
                srp_rule = rule
                break
        
        assert srp_rule is not None
        # MetaRule should calculate unique_chars
        assert hasattr(srp_rule, 'unique_chars')
        assert 'č' in srp_rule.unique_chars
        assert 'š' in srp_rule.unique_chars
        assert 'ž' in srp_rule.unique_chars


if __name__ == "__main__":
    pytest.main([__file__, "-v"])