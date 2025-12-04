from typing import Optional

from .language_rule import LanguageRule
from .tokenizer import Token, TokenClass, Tokenizer


class WordSyllabifier:
    """Handles syllabification of a single word."""

    def __init__(self, word: str, rule: LanguageRule, soft_hyphen: str):
        self.word = word
        self.rule = rule
        self.soft_hyphen = soft_hyphen
        self.tokens = self._tokenize()
        self.nuclei = self._find_nuclei()

    def _tokenize(self) -> list[Token]:
        """Tokenize the word according to language rules."""
        tokenizer = Tokenizer(self.word, self.rule)
        return tokenizer.tokenize()

    def _find_nuclei(self) -> list[int]:
        """Find syllable nuclei in the token list."""
        nuclei = []
        for i, token in enumerate(self.tokens):
            if token.token_class == TokenClass.VOWEL:
                nuclei.append(i)

        # Check for final semivowels (e.g., Romanian final -i after consonant)
        # These don't form a separate syllable nucleus
        if nuclei and self.rule.final_semivowels:
            last_nucleus_idx = nuclei[-1]
            last_token = self.tokens[last_nucleus_idx]
            # Check if it's the last token (or only followed by non-letters)
            is_final = all(
                self.tokens[j].token_class in (TokenClass.SEPARATOR, TokenClass.OTHER)
                for j in range(last_nucleus_idx + 1, len(self.tokens))
            )
            if is_final and last_token.surface.lower() in self.rule.final_semivowels:
                # Check if preceded by consonant
                if last_nucleus_idx > 0:
                    prev_idx = last_nucleus_idx - 1
                    if self.tokens[prev_idx].token_class == TokenClass.CONSONANT:
                        # Remove this nucleus - it's a semivowel, not a syllable
                        nuclei.pop()

        if nuclei:
            return nuclei

        for i, token in enumerate(self.tokens):
            if token.token_class == TokenClass.CONSONANT and token.surface.lower() in self.rule.syllabic_consonants:
                nuclei.append(i)

        return nuclei

    def _skip_separators_forward(self, start: int) -> int:
        """Skip separator tokens forward from start position."""
        pos = start
        while pos < len(self.tokens) and self.tokens[pos].token_class == TokenClass.SEPARATOR:
            pos += 1
        return pos

    def _skip_separators_backward(self, start: int) -> int:
        """Skip separator tokens backward from start position."""
        pos = start
        while pos >= 0 and self.tokens[pos].token_class == TokenClass.SEPARATOR:
            pos -= 1
        return pos

    def _extract_consonant_cluster(self, left: int, right: int) -> tuple[list[Token], list[int]]:
        """Extract consonants between left and right indices."""
        cluster = []
        cluster_indices = []
        for i in range(left, right + 1):
            if self.tokens[i].token_class == TokenClass.CONSONANT:
                cluster.append(self.tokens[i])
                cluster_indices.append(i)
        return cluster, cluster_indices

    def _find_cluster_between_nuclei(self, nk: int, nk1: int) -> tuple[list[Token], list[int]]:
        """Find consonant cluster between two nuclei."""
        left = self._skip_separators_forward(nk + 1)
        right = self._skip_separators_backward(nk1 - 1)
        return self._extract_consonant_cluster(left, right)

    def _is_valid_onset(self, consonant1: str, consonant2: str, prev_nucleus_idx: Optional[int] = None) -> bool:
        """Check if two consonants form a valid onset cluster."""
        onset_candidate = consonant1.lower() + consonant2.lower()
        
        # Check if this cluster requires a long vowel before it
        if onset_candidate in self.rule.clusters_only_after_long and prev_nucleus_idx is not None:
            # Check if previous nucleus is long (digraph or marked as long)
            if not self._is_long_nucleus(prev_nucleus_idx):
                return False
        
        return onset_candidate in self.rule.clusters_keep_next
    
    def _is_long_nucleus(self, nucleus_idx: int) -> bool:
        """Check if nucleus at given index is long (digraph vowel or followed by lengthening marker)."""
        if nucleus_idx >= len(self.tokens):
            return False
            
        # Get the vowel token
        vowel_token = self.tokens[nucleus_idx]
        
        # Check if this vowel token itself is already a digraph (tokenized as one unit)
        if vowel_token.surface.lower() in self.rule.digraph_vowels:
            return True
            
        # Check if current vowel + next character forms a digraph vowel
        if nucleus_idx + 1 < len(self.tokens):
            next_token = self.tokens[nucleus_idx + 1]
            # Build potential digraph from current vowel and next token
            digraph = vowel_token.surface.lower() + next_token.surface.lower()
            if digraph in self.rule.digraph_vowels:
                return True
        
        # Single vowel is considered short
        return False

    def _find_boundary_for_single_consonant(self, cluster_indices: list[int]) -> int:
        """V-CV: boundary before single consonant."""
        return cluster_indices[0]

    def _find_boundary_for_two_consonants(self, cluster: list[Token], cluster_indices: list[int], prev_nucleus_idx: Optional[int] = None) -> int:
        """Determine boundary for two-consonant cluster."""
        if self._is_valid_onset(cluster[0].surface, cluster[1].surface, prev_nucleus_idx):
            return cluster_indices[0]
        else:
            return cluster_indices[1]

    def _find_boundary_for_long_cluster(self, cluster: list[Token], cluster_indices: list[int], prev_nucleus_idx: Optional[int] = None) -> int:
        """Determine boundary for cluster with 3+ consonants."""
        boundary_idx = cluster_indices[-1]

        if len(cluster) >= 2 and self._is_valid_onset(cluster[-2].surface, cluster[-1].surface, prev_nucleus_idx):
            boundary_idx = cluster_indices[-2]

        return boundary_idx

    def _find_boundary_in_cluster(self, cluster: list[Token], cluster_indices: list[int], nk: int, nk1: int) -> Optional[int]:
        """Determine where to place boundary in a consonant cluster or between vowels."""
        if len(cluster) == 0:
            # Check for vowel hiatus (adjacent vowels that form separate syllables)
            if not self.rule.split_hiatus:
                return None

            # Check if nuclei are adjacent (or only separated by modifiers/separators)
            are_adjacent = nk1 - nk == 1
            if not are_adjacent:
                # Check if there are only separators between vowels
                all_separators = True
                for i in range(nk + 1, nk1):
                    if self.tokens[i].token_class != TokenClass.SEPARATOR:
                        all_separators = False
                        break
                are_adjacent = all_separators

            if are_adjacent:
                # Check if these two vowels form a digraph (don't split)
                vowel_pair = self.tokens[nk].surface.lower() + self.tokens[nk1].surface.lower()
                if vowel_pair in self.rule.digraph_vowels:
                    return None
                # Hiatus: split between vowels
                return nk1
            return None
        elif len(cluster) == 1:
            return self._find_boundary_for_single_consonant(cluster_indices)
        elif len(cluster) == 2:
            return self._find_boundary_for_two_consonants(cluster, cluster_indices, nk)
        else:
            return self._find_boundary_for_long_cluster(cluster, cluster_indices, nk)

    def _place_boundaries(self) -> list[int]:
        """Determine syllable boundaries between nuclei."""
        boundaries = []

        for k in range(len(self.nuclei) - 1):
            cluster, cluster_indices = self._find_cluster_between_nuclei(self.nuclei[k], self.nuclei[k + 1])
            boundary = self._find_boundary_in_cluster(cluster, cluster_indices, self.nuclei[k], self.nuclei[k + 1])
            if boundary is not None:
                boundaries.append(boundary)

        return boundaries

    def syllabify(self) -> str:
        """Perform syllabification and return the word with soft hyphens."""
        if len(self.nuclei) < 2:
            return self.word

        boundaries = self._place_boundaries()
        if not boundaries:
            return self.word

        result = []
        boundary_set = set(boundaries)

        for i, token in enumerate(self.tokens):
            if i in boundary_set:
                result.append(self.soft_hyphen)
            result.append(token.surface)

        return "".join(result)
