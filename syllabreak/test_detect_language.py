from pathlib import Path

import pytest
import yaml

from syllabreak import Syllabreak


def load_test_cases():
    test_file = Path(__file__).parent / "data" / "detect_language_tests.yaml"
    with open(test_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    test_cases = []
    for group in data["tests"]:
        lang = group.get("lang")
        expected = [lang] if lang else []
        for text in group["cases"]:
            test_cases.append((text, expected))
    return test_cases


@pytest.mark.parametrize("text,expected", load_test_cases())
def test_detect_language(text, expected):
    s = Syllabreak()
    result = s.detect_language(text)

    if expected:
        assert result, f"Failed for '{text}': got empty result, expected {expected}"
        assert result[0] == expected[0], (
            f"Failed for '{text}': got {result[0]} as first (from {result}), expected {expected[0]}"
        )
    else:
        assert result == [], f"Failed for '{text}': got {result}, expected empty list"
