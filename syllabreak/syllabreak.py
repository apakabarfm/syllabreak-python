import yaml
from pathlib import Path
from .language_rule import LanguageRule, MetaRule
from .tokenizer import Token, Tokenizer
from typing import Optional


class Syllabreak:
    def __init__(self, soft_hyphen: str = '\u00AD'):
        self.soft_hyphen = soft_hyphen
        self.meta_rule = self._load_rules()
    
    def _load_rules(self) -> MetaRule:
        rules_file = Path(__file__).parent / 'data' / 'rules.yaml'
        with open(rules_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        rules = [LanguageRule(rule_data) for rule_data in data['rules']]
        return MetaRule(rules)
    
    def detect_language(self, text: str) -> list[str]:
        matching_rules = self.meta_rule.find_matches(text)
        return [rule.lang3 for rule in matching_rules]
    
    def _select_language_rule(self, text: str) -> Optional[LanguageRule]:
        """Select the first matching language rule for the text."""
        text_lower = text.lower()
        for rule in self.meta_rule.rules:
            all_chars = (rule.vowels | rule.consonants | rule.glides | 
                        rule.syllabic_consonants | rule.modifiers_attach_left | 
                        rule.modifiers_separators)
            if any(c in all_chars for c in text_lower):
                return rule
        return None
    
    def _tokenize_word(self, word: str, rule: LanguageRule) -> list[Token]:
        """Tokenize a word according to language rules."""
        tokenizer = Tokenizer(word, rule)
        return tokenizer.tokenize()
    
    def _find_nuclei(self, tokens: list[Token], rule: LanguageRule) -> list[int]:
        """Find syllable nuclei in the token list."""
        nuclei = []
        
        for i, token in enumerate(tokens):
            if token.token_class == 'vowel':
                nuclei.append(i)
            elif (token.token_class == 'cons' and 
                  token.surface.lower() in rule.syllabic_consonants):
                # Check if not adjacent to any vowel
                has_adjacent_vowel = False
                # Check left
                for j in range(i - 1, -1, -1):
                    if tokens[j].token_class == 'vowel':
                        has_adjacent_vowel = True
                        break
                    if tokens[j].token_class != 'sep':
                        break
                # Check right
                if not has_adjacent_vowel:
                    for j in range(i + 1, len(tokens)):
                        if tokens[j].token_class == 'vowel':
                            has_adjacent_vowel = True
                            break
                        if tokens[j].token_class != 'sep':
                            break
                
                if not has_adjacent_vowel:
                    nuclei.append(i)
        
        return nuclei
    
    def _place_boundaries(self, tokens: list[Token], nuclei: list[int], rule: LanguageRule) -> list[int]:
        """Determine syllable boundaries between nuclei."""
        boundaries = []
        
        for k in range(len(nuclei) - 1):
            nk = nuclei[k]
            nk1 = nuclei[k + 1]
            
            # Find L (index after Nk, skipping sep)
            L = nk + 1
            while L < len(tokens) and tokens[L].token_class == 'sep':
                L += 1
            
            # Find R (index before Nk+1, skipping sep)
            R = nk1 - 1
            while R >= 0 and tokens[R].token_class == 'sep':
                R -= 1
            
            # Collect consonant cluster
            cluster = []
            cluster_indices = []
            for i in range(L, R + 1):
                if tokens[i].token_class == 'cons':
                    cluster.append(tokens[i])
                    cluster_indices.append(i)
            
            # Determine boundary based on cluster size
            if len(cluster) == 0:
                # No boundary needed between vowels
                continue
            elif len(cluster) == 1:
                # V-CV: boundary before single consonant
                boundaries.append(cluster_indices[0])
            elif len(cluster) == 2:
                # Check if cluster should be kept together
                c1_surface = cluster[0].surface.lower()
                c2_surface = cluster[1].surface.lower()
                onset_candidate = c1_surface + c2_surface
                
                if onset_candidate in rule.clusters_keep_next:
                    # V-CCV: boundary before first consonant
                    boundaries.append(cluster_indices[0])
                else:
                    # VC-CV: boundary between consonants
                    boundaries.append(cluster_indices[1])
            else:  # len(cluster) >= 3
                # Try to find the longest valid onset from the right
                # Default: leave one consonant for the onset
                boundary_idx = cluster_indices[-1]
                
                # Check if last two consonants form valid onset
                if len(cluster) >= 2:
                    c1_surface = cluster[-2].surface.lower()
                    c2_surface = cluster[-1].surface.lower()
                    onset_candidate = c1_surface + c2_surface
                    
                    if onset_candidate in rule.clusters_keep_next:
                        # Can take two consonants for onset
                        boundary_idx = cluster_indices[-2]
                
                boundaries.append(boundary_idx)
        
        return boundaries
    
    def _reconstruct_with_hyphens(self, word: str, tokens: list[Token], boundaries: list[int]) -> str:
        """Reconstruct word with soft hyphens at boundaries."""
        if not boundaries:
            return word
        
        result = []
        boundary_set = set(boundaries)
        
        for i, token in enumerate(tokens):
            if i in boundary_set:
                result.append(self.soft_hyphen)
            result.append(token.surface)
        
        return ''.join(result)
    
    def syllabify(self, text: str) -> str:
        """Syllabify text by inserting soft hyphens at syllable boundaries."""
        if not text:
            return text
        
        # Select language rule
        rule = self._select_language_rule(text)
        if not rule:
            return text
        
        # Process each word
        result = []
        i = 0
        
        while i < len(text):
            # Find word boundaries
            if not text[i].isalpha():
                # Non-letter character
                result.append(text[i])
                i += 1
                continue
            
            # Found start of word
            word_start = i
            while i < len(text) and text[i].isalpha():
                i += 1
            word = text[word_start:i]
            
            # Tokenize word
            tokens = self._tokenize_word(word, rule)
            
            # Find nuclei
            nuclei = self._find_nuclei(tokens, rule)
            
            # If less than 2 nuclei, no hyphenation needed
            if len(nuclei) < 2:
                result.append(word)
                continue
            
            # Place boundaries
            boundaries = self._place_boundaries(tokens, nuclei, rule)
            
            # Reconstruct with hyphens
            hyphenated = self._reconstruct_with_hyphens(word, tokens, boundaries)
            result.append(hyphenated)
        
        return ''.join(result)