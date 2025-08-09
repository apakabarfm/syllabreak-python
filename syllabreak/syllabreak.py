class Syllabreak:
    def __init__(self, soft_hyphen: str = '\u00AD'):
        self.soft_hyphen = soft_hyphen
    
    def detect_language(self, text: str) -> list[str]:
        return []
    
    def syllabify(self, text: str) -> str:
        return text