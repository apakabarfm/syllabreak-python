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

        # First pass: collect all vowel nuclei
        for i, token in enumerate(self.tokens):
            if token.token_class == TokenClass.VOWEL:
                nuclei.append(i)

        # If we have any vowels, syllabic consonants are not used
        if nuclei:
            return nuclei

        # Second pass: only if NO vowels, use syllabic consonants
        for i, token in enumerate(self.tokens):
            if token.token_class == TokenClass.CONSONANT and token.surface.lower() in self.rule.syllabic_consonants:
                nuclei.append(i)

        return nuclei

    def _find_cluster_between_nuclei(self, nk: int, nk1: int) -> tuple[list[Token], list[int]]:
        """Find consonant cluster between two nuclei, skipping separators."""
        # Find L (index after Nk, skipping sep)
        L = nk + 1
        while L < len(self.tokens) and self.tokens[L].token_class == TokenClass.SEPARATOR:
            L += 1

        # Find R (index before Nk+1, skipping sep)
        R = nk1 - 1
        while R >= 0 and self.tokens[R].token_class == TokenClass.SEPARATOR:
            R -= 1

        # Collect consonant cluster
        cluster = []
        cluster_indices = []
        for i in range(L, R + 1):
            if self.tokens[i].token_class == TokenClass.CONSONANT:
                cluster.append(self.tokens[i])
                cluster_indices.append(i)

        return cluster, cluster_indices

    def _find_boundary_in_cluster(self, cluster: list[Token], cluster_indices: list[int]) -> int | None:
        """Determine where to place boundary in a consonant cluster."""
        if len(cluster) == 0:
            # No boundary needed between vowels
            return None
        elif len(cluster) == 1:
            # V-CV: boundary before single consonant
            return cluster_indices[0]
        elif len(cluster) == 2:
            # Check if cluster should be kept together
            c1_surface = cluster[0].surface.lower()
            c2_surface = cluster[1].surface.lower()
            onset_candidate = c1_surface + c2_surface

            if onset_candidate in self.rule.clusters_keep_next:
                # V-CCV: boundary before first consonant
                return cluster_indices[0]
            else:
                # VC-CV: boundary between consonants
                return cluster_indices[1]
        else:  # len(cluster) >= 3
            # Try to find the longest valid onset from the right
            # Default: leave one consonant for the onset
            boundary_idx = cluster_indices[-1]

            # Check if last two consonants form valid onset
            if len(cluster) >= 2:
                c1_surface = cluster[-2].surface.lower()
                c2_surface = cluster[-1].surface.lower()
                onset_candidate = c1_surface + c2_surface

                if onset_candidate in self.rule.clusters_keep_next:
                    # Can take two consonants for onset
                    boundary_idx = cluster_indices[-2]

            return boundary_idx

    def _place_boundaries(self) -> list[int]:
        """Determine syllable boundaries between nuclei."""
        boundaries = []

        for k in range(len(self.nuclei) - 1):
            cluster, cluster_indices = self._find_cluster_between_nuclei(self.nuclei[k], self.nuclei[k + 1])
            boundary = self._find_boundary_in_cluster(cluster, cluster_indices)
            if boundary is not None:
                boundaries.append(boundary)

        return boundaries

    def syllabify(self) -> str:
        """Perform syllabification and return the word with soft hyphens."""
        # If less than 2 nuclei, no hyphenation needed
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

