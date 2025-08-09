import yaml
from pathlib import Path
import pytest
from syllabreak import Syllabreak


def load_test_cases():
    test_file = Path(__file__).parent / 'data' / 'syllabify_tests.yaml'
    with open(test_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    test_cases = []
    for section in data['tests']:
        section_name = section['section']
        for case in section['cases']:
            test_cases.append((section_name, case['text'], case['want']))
    return test_cases


@pytest.mark.parametrize("section,text,want", load_test_cases())
def test_syllabify(section, text, want):
    syllabifier = Syllabreak()
    result = syllabifier.syllabify(text)
    assert result == want, f"[{section}] Failed for '{text}': got '{result}', want '{want}'"