import yaml
from pathlib import Path
from .language_rule import LanguageRule, MetaRule


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
    
    def syllabify(self, text: str) -> str:
        return text