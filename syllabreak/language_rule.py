class LanguageRule:
    lang3: str
    script: str
    vowels: set[str]
    consonants: set[str]
    sonorants: set[str]
    clusters_keep_next: set[str]
    dont_split_digraphs: set[str]
    digraph_vowels: set[str]
    glides: set[str]
    syllabic_consonants: set[str]
    modifiers_attach_left: set[str]
    modifiers_attach_right: set[str]
    modifiers_separators: set[str]
    _all_chars: set[str]
    
    def __init__(self, data: dict):
        self.lang3 = data['lang3']
        self.script = data.get('script', '')
        self.vowels = set(data['vowels'])
        self.consonants = set(data['consonants'])
        self.sonorants = set(data['sonorants'])
        self.clusters_keep_next = set(data.get('clusters_keep_next', []))
        self.dont_split_digraphs = set(data.get('dont_split_digraphs', []))
        self.digraph_vowels = set(data.get('digraph_vowels', []))
        self.glides = set(data.get('glides', ''))
        self.syllabic_consonants = set(data.get('syllabic_consonants', ''))
        self.modifiers_attach_left = set(data.get('modifiers_attach_left', ''))
        self.modifiers_attach_right = set(data.get('modifiers_attach_right', ''))
        self.modifiers_separators = set(data.get('modifiers_separators', ''))
        
        self._all_chars = self.vowels | self.consonants
    
    def is_vowel(self, char: str) -> bool:
        return char in self.vowels
    
    def is_consonant(self, char: str) -> bool:
        return char in self.consonants
    
    def contains_char(self, char: str) -> bool:
        return char in self._all_chars
    
    def calculate_match_score(self, text: str) -> float:
        clean_text = ''.join(c.lower() for c in text if c.isalpha())
        if not clean_text:
            return 0.0
        
        matching = sum(1 for c in clean_text if self.contains_char(c))
        return matching / len(clean_text)